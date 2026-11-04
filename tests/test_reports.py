import os
import io
import pytest
from sklearn.datasets import load_wine

import config
from core.database import init_db, get_db_session
from core.models import Project
from core.dataset_manager import DatasetManager
from core.training_engine import TrainingEngine
from core.report_generator import ReportGenerator


@pytest.fixture(autouse=True)
def setup_report_env():
    init_db()
    with get_db_session() as session:
        proj = session.query(Project).filter(Project.id == "rep_proj").first()
        if not proj:
            session.add(Project(id="rep_proj", name="Report Project", is_active=True))
            session.commit()

    wine = load_wine(as_frame=True)
    wine_df = wine.frame.copy()
    wine_df["target"] = wine_df["target"].astype(str)

    buf = io.StringIO()
    wine_df.to_csv(buf, index=False)
    buf.seek(0)

    ds = DatasetManager.import_tabular_file(
        project_id="rep_proj",
        file_path_or_buffer=buf,
        filename="report_wine.csv",
        name="Wine Report Set"
    )

    exp = TrainingEngine.train_model(
        project_id="rep_proj",
        dataset_id=ds.id,
        problem_type="classification",
        algorithm_key="rf",
        target_column="target",
        hyperparameters={"n_estimators": 10},
        random_state=42
    )
    return exp


def test_generate_pdf_report(setup_report_env):
    exp = setup_report_env
    pdf_path = ReportGenerator.generate_pdf_report(exp["id"])
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # valid PDF generated


def test_export_csv_and_json(setup_report_env):
    exp = setup_report_env
    csv_path = ReportGenerator.export_csv_summary([exp["id"]])
    assert os.path.exists(csv_path)

    json_path = ReportGenerator.export_json_report(exp["id"])
    assert os.path.exists(json_path)
