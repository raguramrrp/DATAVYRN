from typing import Dict, Any, List, Optional
import pandas as pd
from core.database import get_db_session
from core.models import Experiment


class ExperimentManager:
    """Manages experiment comparisons, rankings, and persistent experiment catalog."""

    @staticmethod
    def list_experiments(
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        problem_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with get_db_session() as session:
            q = session.query(Experiment)
            if project_id:
                q = q.filter(Experiment.project_id == project_id)
            if dataset_id:
                q = q.filter(Experiment.dataset_id == dataset_id)
            if problem_type:
                q = q.filter(Experiment.problem_type == problem_type)
            exps = q.order_by(Experiment.created_at.desc()).all()
            return [e.to_dict() for e in exps]

    @staticmethod
    def compare_experiments(experiment_ids: List[str]) -> Dict[str, Any]:
        """
        Builds side-by-side comparison table and determines best-performing experiment
        using metric-aware evaluation (higher is better for accuracy/f1/r2; lower is better for mse/rmse/mae).
        """
        if not experiment_ids:
            return {"experiments": [], "comparison_df": pd.DataFrame(), "best_experiment": None}

        with get_db_session() as session:
            exps = session.query(Experiment).filter(Experiment.id.in_(experiment_ids)).all()
            exp_dicts = [e.to_dict() for e in exps]

        if not exp_dicts:
            return {"experiments": [], "comparison_df": pd.DataFrame(), "best_experiment": None}

        rows = []
        for e in exp_dicts:
            metrics = e.get("metrics", {})
            row = {
                "Experiment ID": e["id"],
                "Model": e["model_name"],
                "Problem Type": e["problem_type"].capitalize(),
                "Target": e["target_column"],
                "Dataset Ver": f"v{e['dataset_version']}",
                "Training Time (s)": round(e["training_duration_sec"], 3)
            }

            if e["problem_type"] == "classification":
                row["Accuracy"] = metrics.get("accuracy", 0.0)
                row["F1 (Macro)"] = metrics.get("f1_macro", 0.0)
                row["Precision (Macro)"] = metrics.get("precision_macro", 0.0)
                row["Recall (Macro)"] = metrics.get("recall_macro", 0.0)
                row["ROC-AUC"] = metrics.get("roc_auc", "N/A")
                row["CV Score"] = metrics.get("cv_score", "N/A")
            elif e["problem_type"] == "regression":
                row["RMSE"] = metrics.get("rmse", 0.0)
                row["MAE"] = metrics.get("mae", 0.0)
                row["R²"] = metrics.get("r2", 0.0)
                row["CV Score"] = metrics.get("cv_score", "N/A")
            elif e["problem_type"] == "unsupervised":
                row["Silhouette"] = metrics.get("silhouette_score", "N/A")
                row["Davies-Bouldin"] = metrics.get("davies_bouldin_score", "N/A")

            rows.append(row)

        comp_df = pd.DataFrame(rows)

        # Determine best experiment
        best_exp = None
        first_pt = exp_dicts[0]["problem_type"]
        if first_pt == "classification":
            best_exp = max(exp_dicts, key=lambda x: x.get("metrics", {}).get("f1_macro", 0.0))
            best_reason = f"Highest F1 Score: {best_exp.get('metrics', {}).get('f1_macro', 0.0)}"
        elif first_pt == "regression":
            best_exp = min(exp_dicts, key=lambda x: x.get("metrics", {}).get("rmse", float("inf")))
            best_reason = f"Lowest RMSE: {best_exp.get('metrics', {}).get('rmse', 0.0)}"
        else:
            best_exp = exp_dicts[0]
            best_reason = "Selected baseline experiment"

        return {
            "experiments": exp_dicts,
            "comparison_df": comp_df,
            "best_experiment": best_exp,
            "best_reason": best_reason
        }
