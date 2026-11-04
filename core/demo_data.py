import os
import io
import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from sklearn.datasets import load_wine

import config
from core.database import get_db_session, init_db
from core.models import Project, Dataset, DatasetVersion, ImageItem, AnnotationClass, Annotation, Experiment, AnnotationReviewLog, ErrorAnalysisRecord
from core.dataset_manager import DatasetManager
from core.annotation_engine import AnnotationEngine
from core.training_engine import TrainingEngine


def create_synthetic_inspection_image(filename: str, scene_type: str = "component") -> Tuple[str, bytes, List[Dict[str, Any]]]:
    """Generates clean, synthetic inspection images using PIL drawing with realistic bounding boxes."""
    width, height = 640, 480
    img = Image.new("RGB", (width, height), color="#151C27")
    draw = ImageDraw.Draw(img)

    annotations = []

    # Draw grid background
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill="#1E293B", width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill="#1E293B", width=1)

    if scene_type == "circuit":
        # Draw PCB board
        draw.rectangle([80, 60, 560, 420], fill="#0F382A", outline="#34D399", width=2)
        # IC Chip 1
        draw.rectangle([140, 120, 260, 220], fill="#1E293B", outline="#36D9F2", width=2)
        draw.rectangle([160, 140, 240, 200], fill="#090C12")
        annotations.append({"label_name": "IC_Chip", "bbox_x": 135, "bbox_y": 115, "bbox_w": 130, "bbox_h": 110, "confidence": 0.98})

        # Capacitor
        draw.ellipse([320, 130, 400, 210], fill="#438BFF", outline="#E8EDF5", width=2)
        annotations.append({"label_name": "Capacitor", "bbox_x": 315, "bbox_y": 125, "bbox_w": 90, "bbox_h": 90, "confidence": 0.94})

        # Solder Bridge Defect
        draw.line([(450, 160), (490, 160)], fill="#F5B942", width=6)
        annotations.append({"label_name": "Defect", "bbox_x": 440, "bbox_y": 150, "bbox_w": 60, "bbox_h": 30, "confidence": 0.88})

        # Resistor Array
        draw.rectangle([180, 280, 340, 360], fill="#2A3647", outline="#F5B942", width=2)
        annotations.append({"label_name": "Resistor_Array", "bbox_x": 175, "bbox_y": 275, "bbox_w": 170, "bbox_h": 90, "confidence": 0.96})

    elif scene_type == "urban":
        # Ground / road
        draw.rectangle([0, 280, width, height], fill="#111722", outline="#2A3647")
        draw.line([(0, 380), (width, 380)], fill="#F5B942", width=3)

        # Vehicle 1
        draw.rectangle([100, 240, 280, 340], fill="#192230", outline="#36D9F2", width=2)
        draw.rectangle([130, 210, 250, 250], fill="#2A3647", outline="#36D9F2", width=2)
        draw.ellipse([120, 320, 160, 360], fill="#090C12", outline="#36D9F2", width=2)
        draw.ellipse([220, 320, 260, 360], fill="#090C12", outline="#36D9F2", width=2)
        annotations.append({"label_name": "Vehicle", "bbox_x": 95, "bbox_y": 205, "bbox_w": 190, "bbox_h": 160, "confidence": 0.97})

        # Pedestrian
        draw.ellipse([360, 220, 390, 250], fill="#E8EDF5")
        draw.rectangle([355, 250, 395, 330], fill="#438BFF")
        draw.line([(365, 330), (360, 380)], fill="#E8EDF5", width=3)
        draw.line([(385, 330), (390, 380)], fill="#E8EDF5", width=3)
        annotations.append({"label_name": "Pedestrian", "bbox_x": 350, "bbox_y": 215, "bbox_w": 50, "bbox_h": 170, "confidence": 0.92})

        # Traffic Sign
        draw.line([(520, 180), (520, 360)], fill="#8D9BAD", width=4)
        draw.polygon([(520, 140), (550, 180), (490, 180)], fill="#FF5757", outline="#E8EDF5")
        annotations.append({"label_name": "Traffic_Sign", "bbox_x": 485, "bbox_y": 135, "bbox_w": 70, "bbox_h": 70, "confidence": 0.99})

    elif scene_type == "fabric":
        # Surface texture
        draw.rectangle([60, 60, 580, 420], fill="#1E2A3C", outline="#2A3647", width=2)
        # Micro-crack defect 1
        draw.line([(180, 150), (220, 190), (250, 180)], fill="#FF5757", width=3)
        annotations.append({"label_name": "Defect", "bbox_x": 170, "bbox_y": 140, "bbox_w": 90, "bbox_h": 60, "confidence": 0.91})
        # Hole defect 2
        draw.ellipse([400, 260, 450, 310], fill="#090C12", outline="#FF5757", width=2)
        annotations.append({"label_name": "Defect", "bbox_x": 395, "bbox_y": 255, "bbox_w": 60, "bbox_h": 60, "confidence": 0.95})

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return filename, buffer.getvalue(), annotations


def initialize_demo_workspace():
    """Initializes the database with default projects, Wine dataset, 3 trained models, and annotated images."""
    init_db()

    with get_db_session() as session:
        # Check if already initialized
        proj = session.query(Project).filter(Project.id == "proj_alpha").first()
        if proj:
            return  # Already seeded

        # 1. Create Default Project
        proj = Project(
            id="proj_alpha",
            name="Project Alpha: Model Workbench",
            description="Production machine learning & vision benchmarking workspace",
            is_active=True
        )
        session.add(proj)

    # 2. Ingest Wine Recognition Dataset from Scikit-Learn
    wine = load_wine(as_frame=True)
    wine_df = wine.frame.copy()
    # Rename target values to descriptive class names for clarity
    target_map = {0: "Class_0_Barolo", 1: "Class_1_Grignolino", 2: "Class_2_Barbera"}
    wine_df["wine_class"] = wine_df["target"].map(target_map)
    wine_df = wine_df.drop(columns=["target"])

    wine_csv_bytes = io.BytesIO()
    wine_df.to_csv(wine_csv_bytes, index=False)
    wine_csv_bytes.seek(0)

    wine_dataset = DatasetManager.import_tabular_file(
        project_id="proj_alpha",
        file_path_or_buffer=wine_csv_bytes,
        filename="wine_recognition.csv",
        name="Wine Recognition Benchmark",
        description="Scikit-Learn Wine Dataset: 178 samples, 13 chemical features, 3 target cultivars."
    )

    # 3. Train 3 Real Baseline Algorithms
    TrainingEngine.train_model(
        project_id="proj_alpha",
        dataset_id=wine_dataset.id,
        problem_type="classification",
        algorithm_key="rf",
        target_column="wine_class",
        hyperparameters={"n_estimators": 100, "max_depth": 6},
        random_state=42,
        cv_folds=5
    )

    TrainingEngine.train_model(
        project_id="proj_alpha",
        dataset_id=wine_dataset.id,
        problem_type="classification",
        algorithm_key="lr",
        target_column="wine_class",
        hyperparameters={"C": 1.0, "max_iter": 500},
        random_state=42,
        cv_folds=5
    )

    TrainingEngine.train_model(
        project_id="proj_alpha",
        dataset_id=wine_dataset.id,
        problem_type="classification",
        algorithm_key="dt",
        target_column="wine_class",
        hyperparameters={"max_depth": 4},
        random_state=42,
        cv_folds=5
    )

    # 4. Generate and Ingest Synthetic Image Dataset for Image Studio
    images_meta = [
        create_synthetic_inspection_image("pcb_sample_01.png", "circuit"),
        create_synthetic_inspection_image("pcb_sample_02.png", "circuit"),
        create_synthetic_inspection_image("urban_scene_01.png", "urban"),
        create_synthetic_inspection_image("urban_scene_02.png", "urban"),
        create_synthetic_inspection_image("fabric_sample_01.png", "fabric"),
        create_synthetic_inspection_image("fabric_sample_02.png", "fabric"),
    ]

    files_data = [(fname, fbytes) for fname, fbytes, _ in images_meta]
    initial_classes = ["IC_Chip", "Capacitor", "Defect", "Resistor_Array", "Vehicle", "Pedestrian", "Traffic_Sign"]

    img_dataset = DatasetManager.import_image_files(
        project_id="proj_alpha",
        files_data=files_data,
        name="Vision & Industrial Quality Inspection",
        description="High-resolution multiclass optical inspection and object detection set.",
        initial_classes=initial_classes
    )

    # Apply annotations to images
    with get_db_session() as session:
        items = session.query(ImageItem).filter(ImageItem.dataset_id == img_dataset.id).all()
        for idx, item in enumerate(items):
            if idx < len(images_meta):
                _, _, anns = images_meta[idx]
                status = "completed" if idx < 3 else ("needs_review" if idx == 3 else "in_progress")
                AnnotationEngine.save_image_annotations(item.id, anns, mark_status=status)

                # Add a sample review log
                if idx == 0:
                    AnnotationEngine.review_annotation(
                        image_id=item.id,
                        status="approved",
                        reviewer="Lead QA Inspector",
                        comment="All component boxes verified against CAD schematic"
                    )
                elif idx == 3:
                    AnnotationEngine.review_annotation(
                        image_id=item.id,
                        status="rejected",
                        rejection_reason="Pedestrian bounding box requires tighter boundaries",
                        reviewer="Senior Reviewer"
                    )


def reset_demo_workspace():
    """Wipes all storage and database tables and recreates pristine demo state."""
    init_db()
    with get_db_session() as session:
        session.query(ErrorAnalysisRecord).delete()
        session.query(AnnotationReviewLog).delete()
        session.query(Annotation).delete()
        session.query(AnnotationClass).delete()
        session.query(ImageItem).delete()
        session.query(Experiment).delete()
        session.query(DatasetVersion).delete()
        session.query(Dataset).delete()
        session.query(Project).delete()
        session.commit()

    initialize_demo_workspace()
