import io
import os
import json
import pytest
from PIL import Image

import config
from core.database import init_db, get_db_session
from core.models import Project, Dataset, ImageItem
from core.dataset_manager import DatasetManager
from core.annotation_engine import AnnotationEngine


@pytest.fixture(autouse=True)
def setup_image_env():
    init_db()
    with get_db_session() as session:
        proj = session.query(Project).filter(Project.id == "ann_proj").first()
        if not proj:
            session.add(Project(id="ann_proj", name="Annotation Test Project", is_active=True))
            session.commit()

    # Create dummy images
    img_files = []
    for i in range(2):
        im = Image.new("RGB", (300, 200), color="#151C27")
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        img_files.append((f"test_img_{i}.png", buf.getvalue()))

    ds = DatasetManager.import_image_files(
        project_id="ann_proj",
        files_data=img_files,
        name="Test Image Set",
        initial_classes=["Defect", "Object"]
    )
    return ds


def test_iou_calculation():
    boxA = (10.0, 10.0, 50.0, 50.0)  # area = 2500
    boxB = (10.0, 10.0, 50.0, 50.0)  # same box -> IoU = 1.0
    iou = AnnotationEngine.calculate_iou(boxA, boxB)
    assert iou == pytest.approx(1.0)

    # Disjoint boxes
    boxC = (100.0, 100.0, 50.0, 50.0)
    iou_disjoint = AnnotationEngine.calculate_iou(boxA, boxC)
    assert iou_disjoint == 0.0


def test_save_annotations_and_review(setup_image_env):
    ds = setup_image_env
    images = AnnotationEngine.get_images(ds.id)
    assert len(images) == 2

    img_id = images[0]["id"]
    test_boxes = [
        {"label_name": "Defect", "bbox_x": 20, "bbox_y": 30, "bbox_w": 80, "bbox_h": 60, "confidence": 0.95},
        {"label_name": "Object", "bbox_x": 120, "bbox_y": 80, "bbox_w": 100, "bbox_h": 90, "confidence": 0.98}
    ]

    save_res = AnnotationEngine.save_image_annotations(img_id, test_boxes, mark_status="completed")
    assert save_res["saved_count"] == 2
    assert save_res["status"] == "completed"

    # Verify retrieval
    loaded_anns = AnnotationEngine.get_annotations_for_image(img_id)
    assert len(loaded_anns) == 2

    # Review image
    rev_res = AnnotationEngine.review_annotation(img_id, status="approved", reviewer="Test QA", comment="Verified")
    assert rev_res["reviewer_status"] == "approved"


def test_export_coco(setup_image_env):
    ds = setup_image_env
    images = AnnotationEngine.get_images(ds.id)
    test_boxes = [{"label_name": "Defect", "bbox_x": 10, "bbox_y": 10, "bbox_w": 40, "bbox_h": 40}]
    AnnotationEngine.save_image_annotations(images[0]["id"], test_boxes)

    coco_res = AnnotationEngine.export_coco(ds.id)
    assert os.path.exists(coco_res["file_path"])
    assert coco_res["annotations_count"] >= 1
    assert len(coco_res["json_data"]["categories"]) >= 2


def test_export_yolo(setup_image_env):
    ds = setup_image_env
    images = AnnotationEngine.get_images(ds.id)
    test_boxes = [{"label_name": "Defect", "bbox_x": 10, "bbox_y": 10, "bbox_w": 40, "bbox_h": 40}]
    AnnotationEngine.save_image_annotations(images[0]["id"], test_boxes)

    yolo_res = AnnotationEngine.export_yolo(ds.id)
    assert os.path.exists(yolo_res["dir_path"])
    assert os.path.exists(os.path.join(yolo_res["dir_path"], "classes.txt"))
    assert yolo_res["annotations_count"] >= 1


def test_export_voc(setup_image_env):
    ds = setup_image_env
    images = AnnotationEngine.get_images(ds.id)
    test_boxes = [{"label_name": "Defect", "bbox_x": 10, "bbox_y": 10, "bbox_w": 40, "bbox_h": 40}]
    AnnotationEngine.save_image_annotations(images[0]["id"], test_boxes)

    voc_res = AnnotationEngine.export_voc(ds.id)
    assert os.path.exists(voc_res["dir_path"])
    assert voc_res["annotations_count"] >= 1
