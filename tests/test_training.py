import io
import os
import joblib
import pytest
import pandas as pd
from sklearn.datasets import load_wine

import config
from core.database import init_db, get_db_session
from core.models import Project, Dataset, Experiment
from core.dataset_manager import DatasetManager
from core.training_engine import TrainingEngine


@pytest.fixture(autouse=True)
def setup_training_env():
    init_db()
    with get_db_session() as session:
        proj = session.query(Project).filter(Project.id == "train_proj").first()
        if not proj:
            session.add(Project(id="train_proj", name="Training Test Project", is_active=True))
            session.commit()

    # Ingest a clean tabular dataset for testing
    wine = load_wine(as_frame=True)
    wine_df = wine.frame.copy()
    wine_df["wine_class"] = wine_df["target"].astype(str)
    wine_df = wine_df.drop(columns=["target"])

    buf = io.StringIO()
    wine_df.to_csv(buf, index=False)
    buf.seek(0)

    ds = DatasetManager.import_tabular_file(
        project_id="train_proj",
        file_path_or_buffer=buf,
        filename="test_wine.csv",
        name="Test Wine Dataset"
    )
    return ds


def test_train_classification_random_forest(setup_training_env):
    ds = setup_training_env
    exp = TrainingEngine.train_model(
        project_id="train_proj",
        dataset_id=ds.id,
        problem_type="classification",
        algorithm_key="rf",
        target_column="wine_class",
        hyperparameters={"n_estimators": 20, "max_depth": 4},
        test_split_ratio=0.2,
        random_state=42,
        cv_folds=3
    )

    assert exp is not None
    assert exp["status"] == "completed"
    assert "accuracy" in exp["metrics"]
    assert exp["metrics"]["accuracy"] > 0.80
    assert exp["training_duration_sec"] > 0.0

    # Verify model artifact exists on disk and can be loaded
    assert os.path.exists(exp["model_file_path"])
    loaded_model = joblib.load(exp["model_file_path"])
    assert hasattr(loaded_model, "predict")


def test_train_classification_logistic_regression(setup_training_env):
    ds = setup_training_env
    exp = TrainingEngine.train_model(
        project_id="train_proj",
        dataset_id=ds.id,
        problem_type="classification",
        algorithm_key="lr",
        target_column="wine_class",
        hyperparameters={"C": 1.0, "max_iter": 300},
        test_split_ratio=0.2,
        random_state=42
    )

    assert exp is not None
    assert exp["metrics"]["accuracy"] > 0.80
    assert len(exp["confusion_matrix"]) == 3


def test_train_unsupervised_kmeans(setup_training_env):
    ds = setup_training_env
    exp = TrainingEngine.train_model(
        project_id="train_proj",
        dataset_id=ds.id,
        problem_type="unsupervised",
        algorithm_key="kmeans",
        hyperparameters={"n_clusters": 3},
        random_state=42
    )

    assert exp is not None
    assert "silhouette_score" in exp["metrics"]
    assert exp["metrics"]["n_clusters"] == 3
