import io
import pytest
import pandas as pd
import numpy as np

import config
from core.database import init_db, get_db_session
from core.models import Project, Dataset
from core.dataset_manager import DatasetManager


@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    with get_db_session() as session:
        proj = session.query(Project).filter(Project.id == "test_proj").first()
        if not proj:
            session.add(Project(id="test_proj", name="Test Project", is_active=True))
            session.commit()


def test_calculate_tabular_quality_clean():
    df = pd.DataFrame({
        "feature_a": [1.0, 2.0, 3.0, 4.0, 5.0],
        "feature_b": [10.0, 20.0, 30.0, 40.0, 50.0],
        "target": ["A", "B", "A", "B", "A"]
    })
    quality = DatasetManager.calculate_tabular_quality(df)
    assert quality["score"] == 100.0
    assert len(quality["deductions"]) > 0


def test_calculate_tabular_quality_penalties():
    # DataFrame with missing values, duplicates, and constant column
    df = pd.DataFrame({
        "feature_a": [1.0, 1.0, None, 4.0, 5.0],
        "feature_b": [10.0, 10.0, 30.0, 40.0, 50.0],
        "const_col": ["C", "C", "C", "C", "C"],
        "target": ["A", "A", "B", "B", "A"]
    })
    quality = DatasetManager.calculate_tabular_quality(df)
    assert quality["score"] < 100.0
    assert quality["metrics"]["missing_cells"] == 1
    assert quality["metrics"]["duplicate_rows"] == 1
    assert "const_col" in quality["metrics"]["constant_columns"]


def test_import_and_profile_tabular():
    csv_content = "feat1,feat2,target\n1.2,5.6,0\n2.3,6.7,1\n3.4,7.8,0\n4.5,8.9,1\n"
    buffer = io.StringIO(csv_content)

    dataset = DatasetManager.import_tabular_file(
        project_id="test_proj",
        file_path_or_buffer=buffer,
        filename="test_dataset.csv",
        name="Test CSV Dataset"
    )

    assert dataset is not None
    assert dataset.record_count == 4
    assert dataset.feature_count == 3
    assert dataset.current_version == 1

    # Load back
    loaded_df, ver = DatasetManager.load_tabular_dataframe(dataset.id)
    assert len(loaded_df) == 4
    assert ver == 1


def test_dataset_versioning():
    csv_content = "a,b,c\n1,2,3\n4,5,6\n7,8,9\n"
    ds = DatasetManager.import_tabular_file(
        project_id="test_proj",
        file_path_or_buffer=io.StringIO(csv_content),
        filename="version_test.csv"
    )

    df_v1, v1 = DatasetManager.load_tabular_dataframe(ds.id)
    df_v2 = df_v1.copy()
    df_v2["d"] = [10, 20, 30]

    version_rec = DatasetManager.create_dataset_version(
        dataset_id=ds.id,
        new_df=df_v2,
        change_summary="Added column d",
        operations_pipeline=[{"operation": "add_column", "column": "d"}]
    )

    assert version_rec.version_number == 2
    assert version_rec.feature_count == 4

    # Verify v1 is preserved
    df_loaded_v1, _ = DatasetManager.load_tabular_dataframe(ds.id, version_number=1)
    df_loaded_v2, _ = DatasetManager.load_tabular_dataframe(ds.id, version_number=2)

    assert len(df_loaded_v1.columns) == 3
    assert len(df_loaded_v2.columns) == 4
