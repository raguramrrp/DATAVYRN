import os
import json
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import config
from core.database import get_db_session
from core.models import ImageItem, Annotation, AnnotationClass, AnnotationReviewLog, Dataset


class AnnotationEngine:
    """Handles image bounding box annotations, review lifecycle, class management, and exports (COCO, YOLO, Pascal VOC)."""

    @staticmethod
    def calculate_iou(boxA: Tuple[float, float, float, float], boxB: Tuple[float, float, float, float]) -> float:
        """
        Calculates Intersection-over-Union (IoU) between two bounding boxes.
        Each box is given as (x, y, w, h).
        """
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        inter_w = max(0.0, xB - xA)
        inter_h = max(0.0, yB - yA)
        inter_area = inter_w * inter_h

        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        union_area = float(boxAArea + boxBArea - inter_area)

        if union_area <= 0:
            return 0.0
        return inter_area / union_area

    @staticmethod
    def get_classes(dataset_id: str) -> List[Dict[str, Any]]:
        """Returns all annotation classes for a dataset."""
        with get_db_session() as session:
            classes = session.query(AnnotationClass).filter(
                AnnotationClass.dataset_id == dataset_id
            ).order_by(AnnotationClass.name).all()
            return [c.to_dict() for c in classes]

    @staticmethod
    def add_class(dataset_id: str, name: str, color_hex: str = "#36D9F2") -> Dict[str, Any]:
        """Creates a new annotation class."""
        with get_db_session() as session:
            existing = session.query(AnnotationClass).filter(
                AnnotationClass.dataset_id == dataset_id,
                AnnotationClass.name == name
            ).first()
            if existing:
                return existing.to_dict()

            cls_obj = AnnotationClass(
                id=f"cls_{uuid.uuid4().hex[:8]}",
                dataset_id=dataset_id,
                name=name,
                color_hex=color_hex
            )
            session.add(cls_obj)
            session.commit()
            return cls_obj.to_dict()

    @staticmethod
    def get_images(
        dataset_id: str,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns images for a dataset with optional status and search filtering."""
        with get_db_session() as session:
            q = session.query(ImageItem).filter(ImageItem.dataset_id == dataset_id)
            if status_filter and status_filter != "all":
                q = q.filter(ImageItem.status == status_filter)
            if search_query:
                q = q.filter(ImageItem.filename.ilike(f"%{search_query}%"))

            images = q.order_by(ImageItem.created_at.asc()).all()
            return [img.to_dict() for img in images]

    @staticmethod
    def get_annotations_for_image(image_id: str) -> List[Dict[str, Any]]:
        """Returns all bounding box annotations for an image."""
        with get_db_session() as session:
            anns = session.query(Annotation).filter(Annotation.image_id == image_id).all()
            return [a.to_dict() for a in anns]

    @classmethod
    def save_image_annotations(
        cls,
        image_id: str,
        annotations_data: List[Dict[str, Any]],
        mark_status: Optional[str] = None,
        review_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Replaces annotations for an image with the provided bounding boxes."""
        with get_db_session() as session:
            image = session.query(ImageItem).filter(ImageItem.id == image_id).first()
            if not image:
                raise ValueError(f"Image {image_id} not found")

            # Remove existing annotations for clean overwrite
            session.query(Annotation).filter(Annotation.image_id == image_id).delete()

            # Insert new annotations
            new_objs = []
            for b in annotations_data:
                # Validate coordinates
                w = float(b.get("bbox_w", b.get("width", 0)))
                h = float(b.get("bbox_h", b.get("height", 0)))
                if w <= 1 or h <= 1:
                    continue  # ignore zero-size degenerate boxes

                ann = Annotation(
                    id=f"ann_{uuid.uuid4().hex[:10]}",
                    image_id=image_id,
                    dataset_id=image.dataset_id,
                    label_name=b.get("label_name", b.get("label", "Object")),
                    bbox_x=float(b.get("bbox_x", b.get("left", 0))),
                    bbox_y=float(b.get("bbox_y", b.get("top", 0))),
                    bbox_w=w,
                    bbox_h=h,
                    confidence=float(b["confidence"]) if "confidence" in b and b["confidence"] is not None else 1.0,
                    annotation_source=b.get("annotation_source", "manual")
                )
                session.add(ann)
                new_objs.append(ann)

            if mark_status:
                image.status = mark_status
            elif len(new_objs) > 0 and image.status == "pending":
                image.status = "in_progress"

            if review_notes is not None:
                image.review_notes = review_notes

            image.updated_at = datetime.utcnow()
            session.commit()

            return {
                "image_id": image_id,
                "saved_count": len(new_objs),
                "status": image.status
            }

    @staticmethod
    def review_annotation(
        image_id: str,
        status: str,  # 'approved', 'rejected', 'corrected'
        rejection_reason: str = "",
        reviewer: str = "Lead Reviewer",
        comment: str = ""
    ) -> Dict[str, Any]:
        """Records an official quality review outcome for an image."""
        with get_db_session() as session:
            image = session.query(ImageItem).filter(ImageItem.id == image_id).first()
            if not image:
                raise ValueError(f"Image {image_id} not found")

            image.reviewer_status = status
            image.rejection_reason = rejection_reason if status == "rejected" else ""
            if status == "approved":
                image.status = "completed"
            elif status == "rejected":
                image.status = "needs_review"

            image.updated_at = datetime.utcnow()

            # Record review log
            log = AnnotationReviewLog(
                id=f"rev_{uuid.uuid4().hex[:10]}",
                image_id=image_id,
                reviewer=reviewer,
                status=status,
                agreement_score=1.0 if status == "approved" else 0.0,
                comment=comment or rejection_reason
            )
            session.add(log)
            session.commit()

            return image.to_dict()

    @classmethod
    def export_coco(cls, dataset_id: str) -> Dict[str, Any]:
        """Exports annotations in COCO JSON format."""
        with get_db_session() as session:
            dataset = session.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError("Dataset not found")

            images = session.query(ImageItem).filter(ImageItem.dataset_id == dataset_id).all()
            classes = session.query(AnnotationClass).filter(AnnotationClass.dataset_id == dataset_id).all()

            cat_map = {c.name: idx + 1 for idx, c in enumerate(classes)}
            categories = [{"id": cat_map[c.name], "name": c.name, "supercategory": "object"} for c in classes]

            coco_images = []
            coco_annotations = []
            ann_id = 1

            for img_idx, img in enumerate(images):
                img_num_id = img_idx + 1
                coco_images.append({
                    "id": img_num_id,
                    "file_name": img.filename,
                    "width": img.width,
                    "height": img.height
                })

                for ann in img.annotations:
                    cat_id = cat_map.get(ann.label_name, 1)
                    bbox = [ann.bbox_x, ann.bbox_y, ann.bbox_w, ann.bbox_h]
                    area = ann.bbox_w * ann.bbox_h
                    coco_annotations.append({
                        "id": ann_id,
                        "image_id": img_num_id,
                        "category_id": cat_id,
                        "bbox": bbox,
                        "area": area,
                        "iscrowd": 0,
                        "score": ann.confidence
                    })
                    ann_id += 1

            coco_data = {
                "info": {
                    "description": f"DATAVYRN Export - {dataset.name}",
                    "version": "1.0",
                    "year": datetime.utcnow().year,
                    "date_created": datetime.utcnow().isoformat()
                },
                "images": coco_images,
                "annotations": coco_annotations,
                "categories": categories
            }

            export_file = config.EXPORTS_DIR / f"{dataset_id}_coco.json"
            with open(export_file, "w") as f:
                json.dump(coco_data, f, indent=2)

            return {
                "file_path": str(export_file),
                "format": "COCO JSON",
                "images_count": len(coco_images),
                "annotations_count": len(coco_annotations),
                "json_data": coco_data
            }

    @classmethod
    def export_yolo(cls, dataset_id: str) -> Dict[str, Any]:
        """Exports annotations in YOLO normalized TXT format."""
        with get_db_session() as session:
            dataset = session.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError("Dataset not found")

            images = session.query(ImageItem).filter(ImageItem.dataset_id == dataset_id).all()
            classes = session.query(AnnotationClass).filter(AnnotationClass.dataset_id == dataset_id).all()

            cat_map = {c.name: idx for idx, c in enumerate(classes)}
            yolo_dir = config.EXPORTS_DIR / f"{dataset_id}_yolo"
            yolo_dir.mkdir(parents=True, exist_ok=True)

            # Write classes.txt
            with open(yolo_dir / "classes.txt", "w") as f:
                for c in classes:
                    f.write(f"{c.name}\n")

            total_exported_boxes = 0
            for img in images:
                txt_filename = Path(img.filename).stem + ".txt"
                txt_path = yolo_dir / txt_filename
                lines = []
                w_img = max(float(img.width), 1.0)
                h_img = max(float(img.height), 1.0)

                for ann in img.annotations:
                    cat_id = cat_map.get(ann.label_name, 0)
                    # YOLO: x_center, y_center, width, height (normalized 0 to 1)
                    x_center = (ann.bbox_x + (ann.bbox_w / 2.0)) / w_img
                    y_center = (ann.bbox_y + (ann.bbox_h / 2.0)) / h_img
                    w_norm = ann.bbox_w / w_img
                    h_norm = ann.bbox_h / h_img

                    # Clamp
                    x_center = min(max(x_center, 0.0), 1.0)
                    y_center = min(max(y_center, 0.0), 1.0)
                    w_norm = min(max(w_norm, 0.0), 1.0)
                    h_norm = min(max(h_norm, 0.0), 1.0)

                    lines.append(f"{cat_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
                    total_exported_boxes += 1

                with open(txt_path, "w") as f:
                    f.writelines(lines)

            return {
                "dir_path": str(yolo_dir),
                "format": "YOLO TXT",
                "images_count": len(images),
                "annotations_count": total_exported_boxes,
                "classes": [c.name for c in classes]
            }

    @classmethod
    def export_voc(cls, dataset_id: str) -> Dict[str, Any]:
        """Exports annotations in Pascal VOC XML format."""
        with get_db_session() as session:
            dataset = session.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError("Dataset not found")

            images = session.query(ImageItem).filter(ImageItem.dataset_id == dataset_id).all()
            voc_dir = config.EXPORTS_DIR / f"{dataset_id}_pascal_voc"
            voc_dir.mkdir(parents=True, exist_ok=True)

            total_exported_boxes = 0
            for img in images:
                root = ET.Element("annotation")
                ET.SubElement(root, "folder").text = dataset.name
                ET.SubElement(root, "filename").text = img.filename
                ET.SubElement(root, "path").text = img.file_path

                source = ET.SubElement(root, "source")
                ET.SubElement(source, "database").text = "DATAVYRN Annotation Studio"

                size = ET.SubElement(root, "size")
                ET.SubElement(size, "width").text = str(img.width)
                ET.SubElement(size, "height").text = str(img.height)
                ET.SubElement(size, "depth").text = "3"

                ET.SubElement(root, "segmented").text = "0"

                for ann in img.annotations:
                    obj = ET.SubElement(root, "object")
                    ET.SubElement(obj, "name").text = ann.label_name
                    ET.SubElement(obj, "pose").text = "Unspecified"
                    ET.SubElement(obj, "truncated").text = "0"
                    ET.SubElement(obj, "difficult").text = "0"

                    bndbox = ET.SubElement(obj, "bndbox")
                    ET.SubElement(bndbox, "xmin").text = str(int(round(ann.bbox_x)))
                    ET.SubElement(bndbox, "ymin").text = str(int(round(ann.bbox_y)))
                    ET.SubElement(bndbox, "xmax").text = str(int(round(ann.bbox_x + ann.bbox_w)))
                    ET.SubElement(bndbox, "ymax").text = str(int(round(ann.bbox_y + ann.bbox_h)))
                    total_exported_boxes += 1

                xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
                xml_filename = Path(img.filename).stem + ".xml"
                with open(voc_dir / xml_filename, "w") as f:
                    f.write(xml_str)

            return {
                "dir_path": str(voc_dir),
                "format": "Pascal VOC XML",
                "images_count": len(images),
                "annotations_count": total_exported_boxes
            }
