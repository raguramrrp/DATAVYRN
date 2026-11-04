import json
from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder


class PreprocessingPipeline:
    """Handles tabular data preparation, cleaning, feature transformation, and versioning pipelines."""

    def __init__(self, df: pd.DataFrame):
        self.original_df = df.copy()
        self.df = df.copy()
        self.operations_log: List[Dict[str, Any]] = []

    def get_df(self) -> pd.DataFrame:
        return self.df

    def get_operations(self) -> List[Dict[str, Any]]:
        return self.operations_log

    # -------------------------------------------------------------
    # Data Cleaning Operations
    # -------------------------------------------------------------

    def remove_duplicates(self) -> "PreprocessingPipeline":
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = initial_rows - len(self.df)
        self.operations_log.append({
            "operation": "remove_duplicates",
            "description": f"Removed {removed} duplicate rows ({initial_rows} -> {len(self.df)})",
            "removed_count": removed
        })
        return self

    def drop_missing_rows(self, subset_cols: Optional[List[str]] = None) -> "PreprocessingPipeline":
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=subset_cols)
        removed = initial_rows - len(self.df)
        col_desc = f"in columns {subset_cols}" if subset_cols else "across all columns"
        self.operations_log.append({
            "operation": "drop_missing_rows",
            "description": f"Dropped {removed} rows with missing values {col_desc}",
            "removed_count": removed
        })
        return self

    def impute_missing(self, column: str, strategy: str = "mean", constant_value: Any = None) -> "PreprocessingPipeline":
        if column not in self.df.columns:
            return self

        null_count = int(self.df[column].isna().sum())
        if null_count == 0:
            return self

        fill_val = None
        if strategy == "mean" and pd.api.types.is_numeric_dtype(self.df[column]):
            fill_val = self.df[column].mean()
            self.df[column] = self.df[column].fillna(fill_val)
        elif strategy == "median" and pd.api.types.is_numeric_dtype(self.df[column]):
            fill_val = self.df[column].median()
            self.df[column] = self.df[column].fillna(fill_val)
        elif strategy == "mode":
            mode_series = self.df[column].mode(dropna=True)
            if not mode_series.empty:
                fill_val = mode_series[0]
                self.df[column] = self.df[column].fillna(fill_val)
        elif strategy == "constant":
            fill_val = constant_value
            self.df[column] = self.df[column].fillna(fill_val)

        self.operations_log.append({
            "operation": "impute_missing",
            "column": column,
            "strategy": strategy,
            "fill_value": str(fill_val),
            "imputed_count": null_count,
            "description": f"Imputed {null_count} nulls in '{column}' using {strategy} ({fill_val})"
        })
        return self

    def drop_columns(self, columns: List[str]) -> "PreprocessingPipeline":
        valid_drops = [c for c in columns if c in self.df.columns]
        if valid_drops:
            self.df = self.df.drop(columns=valid_drops)
            self.operations_log.append({
                "operation": "drop_columns",
                "columns": valid_drops,
                "description": f"Dropped {len(valid_drops)} column(s): {', '.join(valid_drops)}"
            })
        return self

    def rename_column(self, old_name: str, new_name: str) -> "PreprocessingPipeline":
        if old_name in self.df.columns and new_name and old_name != new_name:
            self.df = self.df.rename(columns={old_name: new_name})
            self.operations_log.append({
                "operation": "rename_column",
                "old_name": old_name,
                "new_name": new_name,
                "description": f"Renamed column '{old_name}' -> '{new_name}'"
            })
        return self

    def cast_type(self, column: str, target_type: str) -> "PreprocessingPipeline":
        if column not in self.df.columns:
            return self

        try:
            if target_type == "int":
                self.df[column] = pd.to_numeric(self.df[column], errors="coerce").fillna(0).astype(int)
            elif target_type == "float":
                self.df[column] = pd.to_numeric(self.df[column], errors="coerce").astype(float)
            elif target_type == "string":
                self.df[column] = self.df[column].astype(str)
            elif target_type == "category":
                self.df[column] = self.df[column].astype("category")

            self.operations_log.append({
                "operation": "cast_type",
                "column": column,
                "target_type": target_type,
                "description": f"Converted column '{column}' to type {target_type}"
            })
        except Exception as e:
            self.operations_log.append({
                "operation": "cast_type_failed",
                "column": column,
                "error": str(e)
            })
        return self

    def clip_outliers_iqr(self, columns: List[str], factor: float = 1.5) -> "PreprocessingPipeline":
        for col in columns:
            if col in self.df.columns and pd.api.types.is_numeric_dtype(self.df[col]):
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    lower = q1 - factor * iqr
                    upper = q3 + factor * iqr
                    self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                    self.operations_log.append({
                        "operation": "clip_outliers",
                        "column": col,
                        "lower_bound": round(float(lower), 3),
                        "upper_bound": round(float(upper), 3),
                        "description": f"Clipped outliers in '{col}' to range [{lower:.2f}, {upper:.2f}]"
                    })
        return self

    # -------------------------------------------------------------
    # Feature Engineering Operations
    # -------------------------------------------------------------

    def label_encode(self, columns: List[str]) -> "PreprocessingPipeline":
        for col in columns:
            if col in self.df.columns:
                le = LabelEncoder()
                # Cast to str to handle mixed types cleanly
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                mapping = {str(cls_): int(idx) for idx, cls_ in enumerate(le.classes_[:10])}
                self.operations_log.append({
                    "operation": "label_encode",
                    "column": col,
                    "num_classes": len(le.classes_),
                    "preview_mapping": mapping,
                    "description": f"Label encoded '{col}' into {len(le.classes_)} discrete numeric values"
                })
        return self

    def one_hot_encode(self, columns: List[str], drop_first: bool = False) -> "PreprocessingPipeline":
        valid_cols = [c for c in columns if c in self.df.columns]
        if valid_cols:
            prev_cols_count = len(self.df.columns)
            self.df = pd.get_dummies(self.df, columns=valid_cols, drop_first=drop_first, dtype=int)
            new_cols_count = len(self.df.columns)
            self.operations_log.append({
                "operation": "one_hot_encode",
                "columns": valid_cols,
                "added_columns": new_cols_count - prev_cols_count,
                "description": f"One-hot encoded {len(valid_cols)} categorical columns (created {new_cols_count - prev_cols_count} dummy features)"
            })
        return self

    def scale_features(self, columns: List[str], method: str = "standard") -> "PreprocessingPipeline":
        valid_cols = [c for c in columns if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
        if not valid_cols:
            return self

        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        elif method == "robust":
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown scaling method '{method}'")

        self.df[valid_cols] = scaler.fit_transform(self.df[valid_cols])
        self.operations_log.append({
            "operation": "scale_features",
            "columns": valid_cols,
            "method": method,
            "description": f"Applied {method.capitalize()}Scaler to {len(valid_cols)} numerical features"
        })
        return self

    # -------------------------------------------------------------
    # Leakage-Free Train/Test Split Utility
    # -------------------------------------------------------------

    @staticmethod
    def prepare_train_test_split(
        df: pd.DataFrame,
        target_col: str,
        feature_cols: Optional[List[str]] = None,
        test_size: float = 0.2,
        random_state: int = 42,
        is_classification: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Creates clean train-test split with optional stratification for classification.
        Guarantees that test data is completely isolated.
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")

        features = feature_cols if feature_cols else [c for c in df.columns if c != target_col]
        X = df[features].copy()
        y = df[target_col].copy()

        # Check stratification eligibility
        stratify_y = None
        if is_classification:
            val_counts = y.value_counts()
            if (val_counts >= 2).all():
                stratify_y = y

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_y
        )
        return X_train, X_test, y_train, y_test
