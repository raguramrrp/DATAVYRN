import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score,
    silhouette_score, davies_bouldin_score
)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import config
from core.database import get_db_session
from core.models import Experiment, Dataset
from core.preprocessing import PreprocessingPipeline


class TrainingEngine:
    """Trains, cross-validates, evaluates, and persists machine learning models."""

    SUPPORTED_ALGORITHMS = {
        "classification": {
            "rf": {"name": "Random Forest Classifier", "class": RandomForestClassifier},
            "lr": {"name": "Logistic Regression", "class": LogisticRegression},
            "dt": {"name": "Decision Tree Classifier", "class": DecisionTreeClassifier},
            "knn": {"name": "K-Nearest Neighbors", "class": KNeighborsClassifier},
            "svm": {"name": "Support Vector Machine", "class": SVC},
            "nb": {"name": "Gaussian Naive Bayes", "class": GaussianNB}
        },
        "regression": {
            "linear_regression": {"name": "Linear Regression", "class": LinearRegression},
            "rf_regressor": {"name": "Random Forest Regressor", "class": RandomForestRegressor},
            "dt_regressor": {"name": "Decision Tree Regressor", "class": DecisionTreeRegressor}
        },
        "unsupervised": {
            "kmeans": {"name": "K-Means Clustering", "class": KMeans},
            "isolation_forest": {"name": "Isolation Forest (Anomaly Detection)", "class": IsolationForest},
            "pca": {"name": "Principal Component Analysis", "class": PCA}
        }
    }

    @classmethod
    def get_supported_models(cls, problem_type: str) -> Dict[str, str]:
        """Returns key -> name mapping of supported algorithms."""
        pt = problem_type.lower()
        if pt in cls.SUPPORTED_ALGORITHMS:
            return {k: v["name"] for k, v in cls.SUPPORTED_ALGORITHMS[pt].items()}
        return {}

    @classmethod
    def train_model(
        cls,
        project_id: str,
        dataset_id: str,
        problem_type: str,
        algorithm_key: str,
        target_column: Optional[str] = None,
        feature_columns: Optional[List[str]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        test_split_ratio: float = 0.2,
        random_state: int = 42,
        cv_folds: int = 5,
        dataset_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Executes full training pipeline, computes metrics, saves artifacts, and stores experiment in DB."""
        # 1. Load Dataset
        with get_db_session() as session:
            ds = session.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not ds:
                raise ValueError(f"Dataset {dataset_id} not found")
            target_version = dataset_version or ds.current_version

        df, ver_num = DatasetManager_load_df(dataset_id, target_version)

        # 2. Validate Target & Features
        pt = problem_type.lower()
        params = hyperparameters or {}

        if pt in ["classification", "regression"]:
            if not target_column or target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' is required and must exist in dataset.")
            features = feature_columns if feature_columns else [c for c in df.columns if c != target_column]
            if not features:
                raise ValueError("At least one feature column must be selected.")

            # Drop missing rows in selected features & target for robust training
            clean_df = df[features + [target_column]].dropna()
            if len(clean_df) < 10:
                raise ValueError(f"Insufficient samples ({len(clean_df)}) remaining after dropping missing values.")

            X_train, X_test, y_train, y_test = PreprocessingPipeline.prepare_train_test_split(
                clean_df,
                target_col=target_column,
                feature_cols=features,
                test_size=test_split_ratio,
                random_state=random_state,
                is_classification=(pt == "classification")
            )
        else:
            # Unsupervised
            features = feature_columns if feature_columns else df.select_dtypes(include=[np.number]).columns.tolist()
            if not features:
                raise ValueError("Unsupervised learning requires at least one numeric feature column.")
            clean_df = df[features].dropna()
            X_train = clean_df
            X_test = clean_df
            y_train = None
            y_test = None

        # 3. Instantiate Model
        model_instance = cls._instantiate_model(pt, algorithm_key, params, random_state)

        # 4. Train with Precise Timing
        start_time = time.perf_counter()
        if pt in ["classification", "regression"]:
            model_instance.fit(X_train, y_train)
        else:
            model_instance.fit(X_train)
        duration_sec = time.perf_counter() - start_time

        # 5. Cross-Validation (if applicable and enough samples)
        cv_mean_score = None
        if pt in ["classification", "regression"] and cv_folds >= 2 and len(X_train) >= cv_folds * 2:
            try:
                cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state) if pt == "classification" else KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
                scoring = "accuracy" if pt == "classification" else "r2"
                scores = cross_val_score(model_instance, X_train, y_train, cv=cv, scoring=scoring)
                cv_mean_score = round(float(np.mean(scores)), 4)
            except Exception:
                cv_mean_score = None

        # 6. Evaluation on Test Set
        metrics = {}
        classification_report_dict = {}
        confusion_matrix_list = []
        feature_importance_dict = {}
        test_data_summary = {}

        if pt == "classification":
            y_pred = model_instance.predict(X_test)
            y_prob = None
            if hasattr(model_instance, "predict_proba"):
                try:
                    y_prob = model_instance.predict_proba(X_test)
                except Exception:
                    y_prob = None

            acc = float(accuracy_score(y_test, y_pred))
            prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
            rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
            f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
            f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

            roc_auc_val = None
            if y_prob is not None:
                try:
                    classes = np.unique(y_test)
                    if len(classes) == 2:
                        roc_auc_val = float(roc_auc_score(y_test, y_prob[:, 1]))
                    else:
                        roc_auc_val = float(roc_auc_score(y_test, y_prob, multi_class="ovr", average="macro"))
                except Exception:
                    roc_auc_val = None

            cm = confusion_matrix(y_test, y_pred)
            confusion_matrix_list = cm.tolist()
            classification_report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

            metrics = {
                "accuracy": round(acc, 4),
                "precision_macro": round(prec_macro, 4),
                "recall_macro": round(rec_macro, 4),
                "f1_macro": round(f1_macro, 4),
                "f1_weighted": round(f1_weighted, 4),
                "roc_auc": round(roc_auc_val, 4) if roc_auc_val is not None else None,
                "cv_score": cv_mean_score,
                "train_samples": len(X_train),
                "test_samples": len(X_test)
            }

            # Save test prediction snapshot for error analysis
            test_data_summary = {
                "indices": X_test.index.tolist(),
                "y_true": [str(v) for v in y_test.tolist()],
                "y_pred": [str(v) for v in y_pred.tolist()],
                "probabilities": y_prob.tolist() if y_prob is not None else []
            }

        elif pt == "regression":
            y_pred = model_instance.predict(X_test)
            mae = float(mean_absolute_error(y_test, y_pred))
            mse = float(mean_squared_error(y_test, y_pred))
            rmse = float(np.sqrt(mse))
            r2 = float(r2_score(y_test, y_pred))

            metrics = {
                "mae": round(mae, 4),
                "mse": round(mse, 4),
                "rmse": round(rmse, 4),
                "r2": round(r2, 4),
                "cv_score": cv_mean_score,
                "train_samples": len(X_train),
                "test_samples": len(X_test)
            }

            test_data_summary = {
                "indices": X_test.index.tolist(),
                "y_true": [float(v) for v in y_test.tolist()],
                "y_pred": [float(v) for v in y_pred.tolist()],
                "residuals": [float(y_t - y_p) for y_t, y_p in zip(y_test, y_pred)]
            }

        elif pt == "unsupervised":
            if algorithm_key == "kmeans":
                labels = model_instance.labels_
                sil = float(silhouette_score(X_train, labels)) if len(set(labels)) > 1 else 0.0
                db = float(davies_bouldin_score(X_train, labels)) if len(set(labels)) > 1 else 0.0
                metrics = {
                    "silhouette_score": round(sil, 4),
                    "davies_bouldin_score": round(db, 4),
                    "inertia": round(float(model_instance.inertia_), 2),
                    "n_clusters": int(params.get("n_clusters", 3))
                }
            elif algorithm_key == "isolation_forest":
                preds = model_instance.predict(X_train)
                anomaly_count = int((preds == -1).sum())
                metrics = {
                    "anomaly_count": anomaly_count,
                    "anomaly_percentage": round((anomaly_count / len(X_train)) * 100.0, 2),
                    "total_samples": len(X_train)
                }
            elif algorithm_key == "pca":
                explained = model_instance.explained_variance_ratio_
                metrics = {
                    "explained_variance_ratio": [round(float(v), 4) for v in explained],
                    "total_variance_explained": round(float(np.sum(explained)), 4)
                }

        # 7. Extract Feature Importance
        if hasattr(model_instance, "feature_importances_"):
            fi = model_instance.feature_importances_
            feature_importance_dict = {col: round(float(score), 4) for col, score in zip(features, fi)}
        elif hasattr(model_instance, "coef_"):
            coef = model_instance.coef_
            if coef.ndim > 1:
                mean_coef = np.mean(np.abs(coef), axis=0)
            else:
                mean_coef = np.abs(coef)
            feature_importance_dict = {col: round(float(score), 4) for col, score in zip(features, mean_coef)}

        # 8. Persist Model and Test Artifacts
        exp_id = f"exp_{uuid.uuid4().hex[:10]}"
        model_path = config.MODELS_DIR / f"{exp_id}.joblib"
        joblib.dump(model_instance, model_path)

        test_data_path = config.MODELS_DIR / f"{exp_id}_test_data.json"
        with open(test_data_path, "w") as f:
            json.dump(test_data_summary, f)

        model_name = cls.SUPPORTED_ALGORITHMS.get(pt, {}).get(algorithm_key, {}).get("name", algorithm_key)

        # 9. Save to SQLite
        with get_db_session() as session:
            experiment = Experiment(
                id=exp_id,
                project_id=project_id,
                dataset_id=dataset_id,
                dataset_version=target_version,
                problem_type=pt,
                model_name=model_name,
                algorithm_key=algorithm_key,
                target_column=target_column or "",
                feature_columns_json=json.dumps(features),
                hyperparameters_json=json.dumps(params),
                test_split_ratio=test_split_ratio,
                random_state=random_state,
                cv_folds=cv_folds,
                training_duration_sec=duration_sec,
                metrics_json=json.dumps(metrics),
                classification_report_json=json.dumps(classification_report_dict),
                confusion_matrix_json=json.dumps(confusion_matrix_list),
                feature_importance_json=json.dumps(feature_importance_dict),
                model_file_path=str(model_path),
                test_data_path=str(test_data_path),
                status="completed"
            )
            session.add(experiment)

        return cls.get_experiment(exp_id)

    @classmethod
    def _instantiate_model(cls, problem_type: str, algorithm_key: str, params: Dict[str, Any], random_state: int):
        """Constructs scikit-learn estimator instance with validated parameters."""
        if problem_type == "classification":
            if algorithm_key == "rf":
                return RandomForestClassifier(
                    n_estimators=int(params.get("n_estimators", 100)),
                    max_depth=int(params["max_depth"]) if params.get("max_depth") else None,
                    random_state=random_state
                )
            elif algorithm_key == "lr":
                return LogisticRegression(
                    C=float(params.get("C", 1.0)),
                    max_iter=int(params.get("max_iter", 500)),
                    random_state=random_state
                )
            elif algorithm_key == "dt":
                return DecisionTreeClassifier(
                    max_depth=int(params["max_depth"]) if params.get("max_depth") else None,
                    random_state=random_state
                )
            elif algorithm_key == "knn":
                return KNeighborsClassifier(
                    n_neighbors=int(params.get("n_neighbors", 5))
                )
            elif algorithm_key == "svm":
                return SVC(
                    C=float(params.get("C", 1.0)),
                    kernel=params.get("kernel", "rbf"),
                    probability=True,
                    random_state=random_state
                )
            elif algorithm_key == "nb":
                return GaussianNB()

        elif problem_type == "regression":
            if algorithm_key == "linear_regression":
                return LinearRegression()
            elif algorithm_key == "rf_regressor":
                return RandomForestRegressor(
                    n_estimators=int(params.get("n_estimators", 100)),
                    max_depth=int(params["max_depth"]) if params.get("max_depth") else None,
                    random_state=random_state
                )
            elif algorithm_key == "dt_regressor":
                return DecisionTreeRegressor(
                    max_depth=int(params["max_depth"]) if params.get("max_depth") else None,
                    random_state=random_state
                )

        elif problem_type == "unsupervised":
            if algorithm_key == "kmeans":
                return KMeans(
                    n_clusters=int(params.get("n_clusters", 3)),
                    random_state=random_state,
                    n_init=10
                )
            elif algorithm_key == "isolation_forest":
                return IsolationForest(
                    contamination=float(params.get("contamination", 0.05)),
                    random_state=random_state
                )
            elif algorithm_key == "pca":
                return PCA(
                    n_components=int(params.get("n_components", 2)),
                    random_state=random_state
                )

        raise ValueError(f"Unsupported algorithm '{algorithm_key}' for problem type '{problem_type}'")

    @staticmethod
    def get_experiment(exp_id: str) -> Optional[Dict[str, Any]]:
        with get_db_session() as session:
            exp = session.query(Experiment).filter(Experiment.id == exp_id).first()
            return exp.to_dict() if exp else None

    @staticmethod
    def list_experiments(project_id: Optional[str] = None, dataset_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_db_session() as session:
            q = session.query(Experiment)
            if project_id:
                q = q.filter(Experiment.project_id == project_id)
            if dataset_id:
                q = q.filter(Experiment.dataset_id == dataset_id)
            exps = q.order_by(Experiment.created_at.desc()).all()
            return [e.to_dict() for e in exps]


def DatasetManager_load_df(dataset_id: str, version: int):
    """Helper to avoid circular import."""
    from core.dataset_manager import DatasetManager
    return DatasetManager.load_tabular_dataframe(dataset_id, version)
