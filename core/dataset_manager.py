import os
import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import pandas as pd
import numpy as np
from PIL import Image

import config
from core.database import get_db_session
from core.models import Dataset, DatasetVersion, ImageItem, AnnotationClass, Annotation


class DatasetManager:
    """Manages tabular and image dataset ingestion, profiling, quality scoring, and versioning."""

    @staticmethod
    def calculate_tabular_quality(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates a transparent, explainable data quality score (0-100).
        Deductions:
        - Missing cell ratio (up to 30 pts)
        - Duplicate row ratio (up to 20 pts)
        - Constant columns (up to 20 pts, 10 pts per column)
        - Severe outlier presence in numerical features (up to 15 pts)
        - High class imbalance if classification target specified (up to 15 pts)
        """
        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = max(total_rows * total_cols, 1)

        # 1. Missing values
        missing_count = int(df.isna().sum().sum())
        missing_pct = (missing_count / total_cells) * 100.0
        missing_penalty = min(30.0, (missing_pct / 100.0) * 60.0)

        # 2. Duplicate rows
        duplicate_count = int(df.duplicated().sum())
        duplicate_pct = (duplicate_count / max(total_rows, 1)) * 100.0
        duplicate_penalty = min(20.0, (duplicate_pct / 100.0) * 50.0)

        # 3. Constant / single-value columns
        constant_cols = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]
        constant_penalty = min(20.0, len(constant_cols) * 10.0)

        # 4. Outliers in numeric columns using IQR rule
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outlier_counts = {}
        total_outliers = 0
        for col in numeric_cols:
            col_series = df[col].dropna()
            if len(col_series) > 4:
                q1 = col_series.quantile(0.25)
                q3 = col_series.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr
                    cnt = int(((col_series < lower) | (col_series > upper)).sum())
                    if cnt > 0:
                        outlier_counts[col] = cnt
                        total_outliers += cnt

        outlier_ratio = total_outliers / max(total_cells, 1)
        outlier_penalty = min(15.0, outlier_ratio * 100.0 * 2.0)

        # 5. Class imbalance (if target column specified and categorical/discrete)
        imbalance_penalty = 0.0
        target_distribution = {}
        if target_col and target_col in df.columns:
            counts = df[target_col].value_counts()
            target_distribution = counts.to_dict()
            if len(counts) > 1:
                max_share = counts.iloc[0] / total_rows
                min_share = counts.iloc[-1] / total_rows
                # If top class is over 80% and lowest is under 5%
                if max_share > 0.8:
                    imbalance_penalty = min(15.0, (max_share - 0.5) * 30.0)

        total_penalty = missing_penalty + duplicate_penalty + constant_penalty + outlier_penalty + imbalance_penalty
        quality_score = max(0.0, min(100.0, 100.0 - total_penalty))

        # Explainability audit
        deductions = [
            {
                "rule": "Missing Values Penalty",
                "finding": f"{missing_count} cells ({missing_pct:.2f}%) are null or missing",
                "deduction": round(missing_penalty, 1),
                "threshold": "Up to 30 points deducted for missing data"
            },
            {
                "rule": "Duplicate Rows Penalty",
                "finding": f"{duplicate_count} duplicate rows ({duplicate_pct:.2f}%) detected",
                "deduction": round(duplicate_penalty, 1),
                "threshold": "Up to 20 points deducted for duplicate records"
            },
            {
                "rule": "Constant Columns Penalty",
                "finding": f"{len(constant_cols)} columns have zero variance ({', '.join(constant_cols) if constant_cols else 'None'})",
                "deduction": round(constant_penalty, 1),
                "threshold": "10 points deducted per constant feature"
            },
            {
                "rule": "Statistical Outlier Penalty",
                "finding": f"{total_outliers} numerical outliers detected via 1.5*IQR criterion across {len(outlier_counts)} features",
                "deduction": round(outlier_penalty, 1),
                "threshold": "Up to 15 points deducted for extreme outlier ratios"
            }
        ]
        if target_col:
            deductions.append({
                "rule": "Target Class Imbalance",
                "finding": f"Target '{target_col}' class distribution evaluated",
                "deduction": round(imbalance_penalty, 1),
                "threshold": "Up to 15 points deducted for severe class skew"
            })

        return {
            "score": round(quality_score, 1),
            "deductions": deductions,
            "metrics": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "total_cells": total_cells,
                "missing_cells": missing_count,
                "missing_pct": round(missing_pct, 2),
                "duplicate_rows": duplicate_count,
                "duplicate_pct": round(duplicate_pct, 2),
                "constant_columns": constant_cols,
                "numeric_columns_count": len(numeric_cols),
                "categorical_columns_count": total_cols - len(numeric_cols),
                "outlier_counts": outlier_counts,
                "target_distribution": target_distribution
            }
        }

    @staticmethod
    def profile_tabular(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates comprehensive tabular statistics for inspection."""
        column_profiles = []
        for col in df.columns:
            s = df[col]
            dtype_str = str(s.dtype)
            missing = int(s.isna().sum())
            missing_pct = round((missing / max(len(s), 1)) * 100.0, 2)
            unique_count = int(s.nunique(dropna=True))

            profile_entry = {
                "column": col,
                "dtype": dtype_str,
                "missing_count": missing,
                "missing_pct": missing_pct,
                "unique_count": unique_count,
                "is_numeric": pd.api.types.is_numeric_dtype(s),
                "is_constant": unique_count <= 1,
            }

            if pd.api.types.is_numeric_dtype(s):
                valid_s = s.dropna()
                if len(valid_s) > 0:
                    profile_entry.update({
                        "min": round(float(valid_s.min()), 3),
                        "mean": round(float(valid_s.mean()), 3),
                        "std": round(float(valid_s.std()), 3) if len(valid_s) > 1 else 0.0,
                        "median": round(float(valid_s.median()), 3),
                        "max": round(float(valid_s.max()), 3),
                        "skew": round(float(valid_s.skew()), 3) if len(valid_s) > 2 else 0.0
                    })
            else:
                top_vals = s.value_counts(dropna=True).head(5).to_dict()
                profile_entry["top_categories"] = {str(k): int(v) for k, v in top_vals.items()}

            column_profiles.append(profile_entry)

        return {
            "columns": column_profiles,
            "shape": {"rows": len(df), "cols": len(df.columns)},
            "dtypes_summary": df.dtypes.astype(str).value_counts().to_dict()
        }

    @classmethod
    def import_tabular_file(
        cls,
        project_id: str,
        file_path_or_buffer: Any,
        filename: str,
        name: Optional[str] = None,
        description: str = ""
    ) -> Dataset:
        """Imports a CSV, Excel, or JSON file, profiles it, calculates quality, and persists records."""
        ext = Path(filename).suffix.lower()
        if ext not in config.TABULAR_FORMATS:
            raise ValueError(f"Unsupported format '{ext}'. Allowed: {config.TABULAR_FORMATS}")

        # Read into dataframe
        if ext == ".csv":
            df = pd.read_csv(file_path_or_buffer)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path_or_buffer)
        elif ext == ".json":
            df = pd.read_json(file_path_or_buffer)
        else:
            raise ValueError(f"Unsupported tabular extension: {ext}")

        dataset_id = f"ds_{uuid.uuid4().hex[:10]}"
        dataset_name = name or Path(filename).stem.replace("_", " ").title()

        # Save local storage copy
        dest_filename = f"{dataset_id}_v1_{filename}"
        dest_path = config.DATASETS_DIR / dest_filename
        df.to_csv(dest_path, index=False)

        # Profile and evaluate quality
        quality_assessment = cls.calculate_tabular_quality(df)
        profiling = cls.profile_tabular(df)
        quality_assessment["profiling"] = profiling

        file_size = os.path.getsize(dest_path)

        with get_db_session() as session:
            dataset = Dataset(
                id=dataset_id,
                project_id=project_id,
                name=dataset_name,
                description=description,
                dataset_type="tabular",
                original_filename=filename,
                current_version=1,
                file_path=str(dest_path),
                file_size_bytes=file_size,
                record_count=len(df),
                feature_count=len(df.columns),
                image_count=0,
                status="ready",
                quality_score=quality_assessment["score"],
                quality_report_json=json.dumps(quality_assessment)
            )
            session.add(dataset)

            # Create initial version 1 record
            version = DatasetVersion(
                id=f"dsv_{uuid.uuid4().hex[:10]}",
                dataset_id=dataset_id,
                version_number=1,
                file_path=str(dest_path),
                record_count=len(df),
                feature_count=len(df.columns),
                change_summary="Initial dataset import",
                operations_pipeline_json=json.dumps([{"step": "import", "description": f"Imported {filename}"}])
            )
            session.add(version)

        return cls.get_dataset(dataset_id)

    @classmethod
    def import_image_files(
        cls,
        project_id: str,
        files_data: List[Tuple[str, bytes]],  # list of (filename, file_bytes)
        name: str,
        description: str = "",
        initial_classes: Optional[List[str]] = None
    ) -> Dataset:
        """Imports images, extracts image metadata, checks corruption, and persists records."""
        dataset_id = f"ds_img_{uuid.uuid4().hex[:10]}"
        dataset_dir = config.IMAGES_DIR / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)

        image_items_to_create = []
        total_size = 0
        corrupted_count = 0

        for fname, fbytes in files_data:
            ext = Path(fname).suffix.lower()
            if ext not in config.IMAGE_FORMATS:
                continue

            file_id = f"img_{uuid.uuid4().hex[:10]}"
            saved_filename = f"{file_id}_{fname}"
            saved_path = dataset_dir / saved_filename

            with open(saved_path, "wb") as f:
                f.write(fbytes)

            size_bytes = len(fbytes)
            total_size += size_bytes

            # Validate image with PIL
            is_corrupt = False
            width, height = 0, 0
            img_format = ext.replace(".", "")
            try:
                with Image.open(saved_path) as im:
                    im.verify()
                # Reopen to read dimensions after verify
                with Image.open(saved_path) as im:
                    width, height = im.size
                    img_format = im.format.lower() if im.format else img_format
            except Exception:
                is_corrupt = True
                corrupted_count += 1

            image_items_to_create.append({
                "id": file_id,
                "dataset_id": dataset_id,
                "filename": fname,
                "file_path": str(saved_path),
                "width": width,
                "height": height,
                "format": img_format,
                "file_size_bytes": size_bytes,
                "status": "pending",
                "is_corrupted": is_corrupt
            })

        # Quality score for images: penalize corrupted images
        total_valid = len(image_items_to_create)
        corrupted_penalty = (corrupted_count / max(total_valid, 1)) * 100.0 if total_valid > 0 else 0
        quality_score = max(0.0, 100.0 - corrupted_penalty)

        quality_report = {
            "score": round(quality_score, 1),
            "deductions": [
                {
                    "rule": "Corrupted Images",
                    "finding": f"{corrupted_count} corrupted or unreadable images detected out of {total_valid}",
                    "deduction": round(corrupted_penalty, 1),
                    "threshold": "100% deduction for all corrupt files"
                }
            ],
            "metrics": {
                "total_images": total_valid,
                "corrupted_images": corrupted_count,
                "valid_images": total_valid - corrupted_count,
                "formats": list(set(it["format"] for it in image_items_to_create if not it["is_corrupted"]))
            }
        }

        with get_db_session() as session:
            dataset = Dataset(
                id=dataset_id,
                project_id=project_id,
                name=name,
                description=description,
                dataset_type="image",
                original_filename=f"{len(image_items_to_create)} images uploaded",
                current_version=1,
                file_path=str(dataset_dir),
                file_size_bytes=total_size,
                record_count=total_valid,
                feature_count=0,
                image_count=total_valid,
                status="ready",
                quality_score=quality_score,
                quality_report_json=json.dumps(quality_report)
            )
            session.add(dataset)

            # Add images
            for it in image_items_to_create:
                item_obj = ImageItem(**it)
                session.add(item_obj)

            # Add default annotation classes
            classes_to_add = initial_classes or ["Object", "Defect", "Vehicle", "Person"]
            palette = ["#36D9F2", "#438BFF", "#34D399", "#F5B942", "#FF5757", "#A855F7"]
            for idx, cname in enumerate(classes_to_add):
                color = palette[idx % len(palette)]
                session.add(AnnotationClass(
                    id=f"cls_{uuid.uuid4().hex[:8]}",
                    dataset_id=dataset_id,
                    name=cname,
                    color_hex=color
                ))

        return cls.get_dataset(dataset_id)

    @classmethod
    def create_dataset_version(
        cls,
        dataset_id: str,
        new_df: pd.DataFrame,
        change_summary: str,
        operations_pipeline: List[Dict[str, Any]]
    ) -> DatasetVersion:
        """Saves a new tabular dataset version without overwriting prior versions."""
        with get_db_session() as session:
            dataset = session.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")

            new_version_num = dataset.current_version + 1
            version_id = f"dsv_{uuid.uuid4().hex[:10]}"
            new_filename = f"{dataset_id}_v{new_version_num}.csv"
            new_path = config.DATASETS_DIR / new_filename

            new_df.to_csv(new_path, index=False)
            file_size = os.path.getsize(new_path)

            # Recalculate quality on new version
            quality_assessment = cls.calculate_tabular_quality(new_df)
            quality_assessment["profiling"] = cls.profile_tabular(new_df)

            version = DatasetVersion(
                id=version_id,
                dataset_id=dataset_id,
                version_number=new_version_num,
                file_path=str(new_path),
                record_count=len(new_df),
                feature_count=len(new_df.columns),
                change_summary=change_summary,
                operations_pipeline_json=json.dumps(operations_pipeline)
            )
            session.add(version)

            # Update dataset pointer to latest version
            dataset.current_version = new_version_num
            dataset.file_path = str(new_path)
            dataset.file_size_bytes = file_size
            dataset.record_count = len(new_df)
            dataset.feature_count = len(new_df.columns)
            dataset.quality_score = quality_assessment["score"]
            dataset.quality_report_json = json.dumps(quality_assessment)
            dataset.updated_at = datetime.utcnow()

            session.commit()
            return version

    @staticmethod
    def get_dataset(dataset_id: str) -> Optional[Dataset]:
        """Retrieves a dataset by ID with fresh session."""
        with get_db_session() as session:
            return session.query(Dataset).filter(Dataset.id == dataset_id).first()

    @staticmethod
    def list_datasets(project_id: Optional[str] = None, dataset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists datasets matching criteria."""
        with get_db_session() as session:
            q = session.query(Dataset)
            if project_id:
                q = q.filter(Dataset.project_id == project_id)
            if dataset_type:
                q = q.filter(Dataset.dataset_type == dataset_type)
            datasets = q.order_by(Dataset.created_at.desc()).all()
            return [d.to_dict() for d in datasets]

    @staticmethod
    def load_tabular_dataframe(dataset_id: str, version_number: Optional[int] = None) -> Tuple[pd.DataFrame, int]:
        """Loads the DataFrame for a dataset and version."""
        with get_db_session() as session:
            dataset = session.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")

            target_version = version_number or dataset.current_version
            version_rec = session.query(DatasetVersion).filter(
                DatasetVersion.dataset_id == dataset_id,
                DatasetVersion.version_number == target_version
            ).first()

            file_path = version_rec.file_path if version_rec else dataset.file_path
            df = pd.read_csv(file_path)
            return df, target_version
