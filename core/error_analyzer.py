import json
import uuid
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

import config
from core.database import get_db_session
from core.models import Experiment, ErrorAnalysisRecord, Dataset
from core.dataset_manager import DatasetManager


class ErrorAnalyzer:
    """Investigates misclassified records, high residuals, and orchestrates guided corrections."""

    @staticmethod
    def get_classification_errors(exp_id: str) -> Dict[str, Any]:
        """Finds all misclassified test samples with confidence scores and confused class matrix."""
        with get_db_session() as session:
            exp = session.query(Experiment).filter(Experiment.id == exp_id).first()
            if not exp or exp.problem_type != "classification":
                return {"errors": [], "confused_pairs": {}, "total_errors": 0}

            if not exp.test_data_path:
                return {"errors": [], "confused_pairs": {}, "total_errors": 0}

            try:
                with open(exp.test_data_path, "r") as f:
                    td = json.load(f)
            except Exception:
                return {"errors": [], "confused_pairs": {}, "total_errors": 0}

            indices = td.get("indices", [])
            y_true = td.get("y_true", [])
            y_pred = td.get("y_pred", [])
            probs = td.get("probabilities", [])

            errors = []
            confused_pairs = {}

            # Also fetch existing error investigation notes from DB
            existing_notes = {
                note.sample_index: note.to_dict()
                for note in exp.error_notes
            }

            for i in range(len(y_true)):
                actual = str(y_true[i])
                pred = str(y_pred[i])
                if actual != pred:
                    pair_key = f"{actual} -> {pred}"
                    confused_pairs[pair_key] = confused_pairs.get(pair_key, 0) + 1

                    sample_idx = indices[i] if i < len(indices) else i
                    prob_val = None
                    if probs and i < len(probs) and len(probs[i]) > 0:
                        prob_val = round(float(np.max(probs[i])), 3)

                    note_info = existing_notes.get(sample_idx, {})

                    errors.append({
                        "sample_index": sample_idx,
                        "actual": actual,
                        "predicted": pred,
                        "confidence": prob_val,
                        "suspected_cause": note_info.get("suspected_cause", ""),
                        "action_taken": note_info.get("action_taken", ""),
                        "corrected_value": note_info.get("corrected_value", "")
                    })

            return {
                "total_errors": len(errors),
                "error_rate": round(len(errors) / max(len(y_true), 1) * 100.0, 2),
                "total_samples": len(y_true),
                "confused_pairs": dict(sorted(confused_pairs.items(), key=lambda x: x[1], reverse=True)),
                "errors": errors
            }

    @staticmethod
    def get_regression_errors(exp_id: str, top_n: int = 20) -> Dict[str, Any]:
        """Finds worst residual samples for regression models."""
        with get_db_session() as session:
            exp = session.query(Experiment).filter(Experiment.id == exp_id).first()
            if not exp or exp.problem_type != "regression":
                return {"high_errors": [], "total_samples": 0}

            try:
                with open(exp.test_data_path, "r") as f:
                    td = json.load(f)
            except Exception:
                return {"high_errors": [], "total_samples": 0}

            indices = td.get("indices", [])
            y_true = td.get("y_true", [])
            y_pred = td.get("y_pred", [])
            residuals = td.get("residuals", [])

            items = []
            for i in range(len(y_true)):
                sample_idx = indices[i] if i < len(indices) else i
                res = residuals[i] if i < len(residuals) else (y_true[i] - y_pred[i])
                items.append({
                    "sample_index": sample_idx,
                    "actual": round(float(y_true[i]), 4),
                    "predicted": round(float(y_pred[i]), 4),
                    "residual": round(float(res), 4),
                    "abs_error": round(float(abs(res)), 4)
                })

            items.sort(key=lambda x: x["abs_error"], reverse=True)
            return {
                "high_errors": items[:top_n],
                "total_samples": len(y_true)
            }

    @staticmethod
    def log_error_investigation(
        exp_id: str,
        sample_index: int,
        true_value: str,
        predicted_value: str,
        confidence: float,
        suspected_cause: str,
        action_taken: str = "",
        corrected_value: str = ""
    ) -> Dict[str, Any]:
        """Saves error diagnostics note into the database."""
        with get_db_session() as session:
            rec = session.query(ErrorAnalysisRecord).filter(
                ErrorAnalysisRecord.experiment_id == exp_id,
                ErrorAnalysisRecord.sample_index == sample_index
            ).first()

            if not rec:
                rec = ErrorAnalysisRecord(
                    id=f"err_{uuid.uuid4().hex[:10]}",
                    experiment_id=exp_id,
                    sample_index=sample_index,
                    true_value=str(true_value),
                    predicted_value=str(predicted_value),
                    confidence=confidence,
                    suspected_cause=suspected_cause,
                    action_taken=action_taken,
                    corrected_value=str(corrected_value)
                )
                session.add(rec)
            else:
                rec.suspected_cause = suspected_cause
                rec.action_taken = action_taken
                rec.corrected_value = str(corrected_value)

            session.commit()
            return rec.to_dict()

    @staticmethod
    def apply_data_corrections(
        dataset_id: str,
        corrections: List[Dict[str, Any]],  # list of {index: int, column: str, new_value: Any} or {index: int, action: 'drop'}
        change_summary: str = "Corrected verified label errors via Error Analysis Workbench"
    ) -> Any:
        """
        Creates a new dataset version reflecting verified user corrections.
        Never automatically modifies without user review.
        """
        df, ver = DatasetManager.load_tabular_dataframe(dataset_id)
        df_new = df.copy()

        applied_ops = []
        rows_to_drop = []

        for corr in corrections:
            idx = corr.get("index")
            action = corr.get("action", "modify")
            if action == "drop":
                if idx in df_new.index:
                    rows_to_drop.append(idx)
                    applied_ops.append(f"Dropped mislabeled row index {idx}")
            elif action == "modify":
                col = corr.get("column")
                new_val = corr.get("new_value")
                if col in df_new.columns and idx in df_new.index:
                    # Cast new_val to target column type
                    target_dtype = df_new[col].dtype
                    try:
                        cast_val = pd.Series([new_val]).astype(target_dtype).iloc[0]
                    except Exception:
                        cast_val = new_val
                    df_new.loc[idx, col] = cast_val
                    applied_ops.append(f"Row {idx} '{col}' corrected to '{new_val}'")

        if rows_to_drop:
            df_new = df_new.drop(index=rows_to_drop)

        ops_pipeline = [{
            "step": "error_analysis_correction",
            "changes_count": len(applied_ops),
            "details": applied_ops
        }]

        new_version = DatasetManager.create_dataset_version(
            dataset_id=dataset_id,
            new_df=df_new,
            change_summary=change_summary,
            operations_pipeline=ops_pipeline
        )
        return new_version
