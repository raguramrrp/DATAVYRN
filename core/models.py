import json
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    dataset_type = Column(String(32), nullable=False)  # 'tabular' or 'image'
    original_filename = Column(String(256), nullable=False)
    current_version = Column(Integer, default=1)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    record_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    status = Column(String(32), default="ready")
    quality_score = Column(Float, default=100.0)
    quality_report_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan", order_by="DatasetVersion.version_number")
    images = relationship("ImageItem", back_populates="dataset", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="dataset", cascade="all, delete-orphan")
    annotation_classes = relationship("AnnotationClass", back_populates="dataset", cascade="all, delete-orphan")

    def to_dict(self):
        report = {}
        try:
            report = json.loads(self.quality_report_json) if self.quality_report_json else {}
        except Exception:
            pass
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "dataset_type": self.dataset_type,
            "original_filename": self.original_filename,
            "current_version": self.current_version,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "record_count": self.record_count,
            "feature_count": self.feature_count,
            "image_count": self.image_count,
            "status": self.status,
            "quality_score": round(self.quality_score, 1) if self.quality_score is not None else 0.0,
            "quality_report": report,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    record_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    change_summary = Column(Text, default="")
    operations_pipeline_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="versions")

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "version_number": self.version_number,
            "file_path": self.file_path,
            "record_count": self.record_count,
            "feature_count": self.feature_count,
            "change_summary": self.change_summary,
            "operations_pipeline": json.loads(self.operations_pipeline_json) if self.operations_pipeline_json else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ImageItem(Base):
    __tablename__ = "image_items"

    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    filename = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    format = Column(String(16), default="jpg")
    file_size_bytes = Column(Integer, default=0)
    status = Column(String(32), default="pending")  # 'pending', 'in_progress', 'completed', 'needs_review'
    review_notes = Column(Text, default="")
    reviewer_status = Column(String(32), default="unreviewed")  # 'unreviewed', 'approved', 'rejected'
    rejection_reason = Column(Text, default="")
    is_corrupted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="images")
    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")
    review_logs = relationship("AnnotationReviewLog", back_populates="image", cascade="all, delete-orphan")

    def to_dict(self):
        try:
            ann_count = len(self.annotations) if self.annotations else 0
        except Exception:
            ann_count = 0

        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "file_size_bytes": self.file_size_bytes,
            "status": self.status,
            "review_notes": self.review_notes,
            "reviewer_status": self.reviewer_status,
            "rejection_reason": self.rejection_reason,
            "is_corrupted": self.is_corrupted,
            "annotation_count": ann_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnnotationClass(Base):
    __tablename__ = "annotation_classes"

    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    name = Column(String(64), nullable=False)
    color_hex = Column(String(16), default="#36D9F2")
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="annotation_classes")

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "name": self.name,
            "color_hex": self.color_hex,
        }


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String(64), primary_key=True)
    image_id = Column(String(64), ForeignKey("image_items.id"), nullable=False)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    label_name = Column(String(64), nullable=False)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_w = Column(Float, nullable=False)
    bbox_h = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    annotation_source = Column(String(32), default="manual")  # 'manual', 'model_assisted', 'ground_truth'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    image = relationship("ImageItem", back_populates="annotations")

    def to_dict(self):
        return {
            "id": self.id,
            "image_id": self.image_id,
            "dataset_id": self.dataset_id,
            "label_name": self.label_name,
            "bbox_x": round(self.bbox_x, 2),
            "bbox_y": round(self.bbox_y, 2),
            "bbox_w": round(self.bbox_w, 2),
            "bbox_h": round(self.bbox_h, 2),
            "confidence": round(self.confidence, 3) if self.confidence is not None else None,
            "annotation_source": self.annotation_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnnotationReviewLog(Base):
    __tablename__ = "annotation_review_logs"

    id = Column(String(64), primary_key=True)
    image_id = Column(String(64), ForeignKey("image_items.id"), nullable=False)
    reviewer = Column(String(64), default="Lead Reviewer")
    status = Column(String(32), nullable=False)  # 'approved', 'rejected', 'corrected'
    agreement_score = Column(Float, default=1.0)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageItem", back_populates="review_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "image_id": self.image_id,
            "reviewer": self.reviewer,
            "status": self.status,
            "agreement_score": self.agreement_score,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(64), primary_key=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    dataset_version = Column(Integer, default=1)
    problem_type = Column(String(32), nullable=False)  # 'classification', 'regression', 'clustering', 'anomaly_detection'
    model_name = Column(String(128), nullable=False)
    algorithm_key = Column(String(64), nullable=False)
    target_column = Column(String(128), default="")
    feature_columns_json = Column(Text, default="[]")
    hyperparameters_json = Column(Text, default="{}")
    test_split_ratio = Column(Float, default=0.2)
    random_state = Column(Integer, default=42)
    cv_folds = Column(Integer, default=5)
    training_duration_sec = Column(Float, default=0.0)
    metrics_json = Column(Text, default="{}")
    classification_report_json = Column(Text, default="{}")
    confusion_matrix_json = Column(Text, default="[]")
    feature_importance_json = Column(Text, default="{}")
    model_file_path = Column(String(512), default="")
    test_data_path = Column(String(512), default="")
    status = Column(String(32), default="completed")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="experiments")
    dataset = relationship("Dataset", back_populates="experiments", lazy="joined")
    error_notes = relationship("ErrorAnalysisRecord", back_populates="experiment", cascade="all, delete-orphan")

    def to_dict(self):
        try:
            ds_name = self.dataset.name if self.dataset else "Unknown"
        except Exception:
            ds_name = "Unknown"

        return {
            "id": self.id,
            "project_id": self.project_id,
            "dataset_id": self.dataset_id,
            "dataset_name": ds_name,
            "dataset_version": self.dataset_version,
            "problem_type": self.problem_type,
            "model_name": self.model_name,
            "algorithm_key": self.algorithm_key,
            "target_column": self.target_column,
            "feature_columns": json.loads(self.feature_columns_json) if self.feature_columns_json else [],
            "hyperparameters": json.loads(self.hyperparameters_json) if self.hyperparameters_json else {},
            "test_split_ratio": self.test_split_ratio,
            "random_state": self.random_state,
            "cv_folds": self.cv_folds,
            "training_duration_sec": round(self.training_duration_sec, 3),
            "metrics": json.loads(self.metrics_json) if self.metrics_json else {},
            "classification_report": json.loads(self.classification_report_json) if self.classification_report_json else {},
            "confusion_matrix": json.loads(self.confusion_matrix_json) if self.confusion_matrix_json else [],
            "feature_importance": json.loads(self.feature_importance_json) if self.feature_importance_json else {},
            "model_file_path": self.model_file_path,
            "test_data_path": self.test_data_path,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ErrorAnalysisRecord(Base):
    __tablename__ = "error_analysis_records"

    id = Column(String(64), primary_key=True)
    experiment_id = Column(String(64), ForeignKey("experiments.id"), nullable=False)
    sample_index = Column(Integer, nullable=False)
    true_value = Column(String(128), default="")
    predicted_value = Column(String(128), default="")
    confidence = Column(Float, default=0.0)
    suspected_cause = Column(String(256), default="")
    action_taken = Column(String(256), default="")
    corrected_value = Column(String(128), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="error_notes")

    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "sample_index": self.sample_index,
            "true_value": self.true_value,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "suspected_cause": self.suspected_cause,
            "action_taken": self.action_taken,
            "corrected_value": self.corrected_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
