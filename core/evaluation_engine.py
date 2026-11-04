import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve, auc

import config
from core.database import get_db_session
from core.models import Experiment


class EvaluationEngine:
    """Computes evaluation analytics, ROC curves, residual distributions, and comparative benchmarks."""

    @staticmethod
    def get_experiment_eval_data(exp_id: str) -> Dict[str, Any]:
        """Loads experiment metrics, test predictions, and confusion matrix."""
        with get_db_session() as session:
            exp = session.query(Experiment).filter(Experiment.id == exp_id).first()
            if not exp:
                raise ValueError(f"Experiment {exp_id} not found")

            exp_dict = exp.to_dict()

            test_data = {}
            if exp.test_data_path and Path(exp.test_data_path).exists():
                try:
                    with open(exp.test_data_path, "r") as f:
                        test_data = json.load(f)
                except Exception:
                    test_data = {}

            return {
                "experiment": exp_dict,
                "test_data": test_data
            }

    @staticmethod
    def compute_roc_curve_data(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Computes ROC curve points from saved test data."""
        y_true = test_data.get("y_true", [])
        probabilities = test_data.get("probabilities", [])

        if not y_true or not probabilities:
            return {"curves": []}

        y_true_arr = np.array(y_true)
        probs_arr = np.array(probabilities)
        unique_classes = np.unique(y_true_arr)

        curves = []
        if len(unique_classes) == 2 and probs_arr.shape[1] >= 2:
            # Binary classification
            pos_class = unique_classes[1]
            y_binary = (y_true_arr == pos_class).astype(int)
            fpr, tpr, _ = roc_curve(y_binary, probs_arr[:, 1])
            roc_auc = auc(fpr, tpr)
            curves.append({
                "class_name": str(pos_class),
                "fpr": [round(float(v), 4) for v in fpr],
                "tpr": [round(float(v), 4) for v in tpr],
                "auc": round(float(roc_auc), 4)
            })
        elif len(unique_classes) > 2 and probs_arr.shape[1] == len(unique_classes):
            # Multiclass OvR
            for idx, c in enumerate(unique_classes):
                y_binary = (y_true_arr == c).astype(int)
                fpr, tpr, _ = roc_curve(y_binary, probs_arr[:, idx])
                roc_auc = auc(fpr, tpr)
                curves.append({
                    "class_name": str(c),
                    "fpr": [round(float(v), 4) for v in fpr],
                    "tpr": [round(float(v), 4) for v in tpr],
                    "auc": round(float(roc_auc), 4)
                })

        return {"curves": curves}

    @staticmethod
    def compute_residuals_data(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Computes residual analytics for regression experiments."""
        y_true = np.array(test_data.get("y_true", []))
        y_pred = np.array(test_data.get("y_pred", []))
        residuals = np.array(test_data.get("residuals", []))

        if len(y_true) == 0:
            return {}

        return {
            "y_true": [round(float(v), 4) for v in y_true],
            "y_pred": [round(float(v), 4) for v in y_pred],
            "residuals": [round(float(v), 4) for v in residuals],
            "abs_residuals": [round(float(abs(v)), 4) for v in residuals],
            "mean_residual": round(float(np.mean(residuals)), 4),
            "std_residual": round(float(np.std(residuals)), 4),
            "max_error": round(float(np.max(np.abs(residuals))), 4)
        }
