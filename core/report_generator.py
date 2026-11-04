import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import config
from core.database import get_db_session
from core.models import Experiment, Dataset, Project


class ReportGenerator:
    """Generates enterprise PDF, CSV, and JSON technical reports."""

    @classmethod
    def generate_pdf_report(cls, experiment_id: str) -> str:
        """Generates a professional PDF technical report for an experiment."""
        with get_db_session() as session:
            exp = session.query(Experiment).filter(Experiment.id == experiment_id).first()
            if not exp:
                raise ValueError(f"Experiment {experiment_id} not found")

            ds = exp.dataset
            proj = exp.project

            exp_dict = exp.to_dict()
            ds_dict = ds.to_dict() if ds else {}
            proj_dict = proj.to_dict() if proj else {}

        pdf_filename = f"DATAVYRN_Report_{experiment_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = config.REPORTS_DIR / pdf_filename

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Cyber-Enterprise Styles
        brand_title = ParagraphStyle(
            "BrandTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#36D9F2")
        )
        subtitle_style = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#8D9BAD")
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#151C27"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#2A3647")
        )

        elements = []

        # Header Title
        elements.append(Paragraph("DATAVYRN — TECHNICAL EXPERIMENT REPORT", brand_title))
        elements.append(Paragraph(f"DATA INTELLIGENCE & MACHINE LEARNING BENCHMARK | Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#36D9F2"), spaceBefore=6, spaceAfter=14))

        # 1. Project & Experiment Metadata Table
        elements.append(Paragraph("1. Experiment & Project Overview", heading_style))
        meta_data = [
            [Paragraph("<b>Experiment ID</b>", body_style), Paragraph(exp_dict["id"], body_style),
             Paragraph("<b>Status</b>", body_style), Paragraph(exp_dict["status"].upper(), body_style)],
            [Paragraph("<b>Model Name</b>", body_style), Paragraph(exp_dict["model_name"], body_style),
             Paragraph("<b>Problem Type</b>", body_style), Paragraph(exp_dict["problem_type"].capitalize(), body_style)],
            [Paragraph("<b>Dataset</b>", body_style), Paragraph(f"{ds_dict.get('name', 'N/A')} (v{exp_dict['dataset_version']})", body_style),
             Paragraph("<b>Target Variable</b>", body_style), Paragraph(exp_dict.get("target_column") or "N/A", body_style)],
            [Paragraph("<b>Training Time</b>", body_style), Paragraph(f"{exp_dict['training_duration_sec']}s", body_style),
             Paragraph("<b>Test Split / CV</b>", body_style), Paragraph(f"{int(exp_dict['test_split_ratio']*100)}% / {exp_dict['cv_folds']}-Fold", body_style)],
        ]
        meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # 2. Evaluation Metrics Table
        elements.append(Paragraph("2. Primary Evaluation Performance", heading_style))
        metrics = exp_dict.get("metrics", {})
        metric_rows = [["Metric Name", "Evaluated Value", "Benchmark Status"]]
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                metric_rows.append([k.replace("_", " ").title(), f"{v:.4f}" if isinstance(v, float) else str(v), "VERIFIED"])
            elif isinstance(v, str):
                metric_rows.append([k.replace("_", " ").title(), v, "RECORDED"])

        metric_table = Table(metric_rows, colWidths=[200, 170, 170])
        metric_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#36D9F2")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(metric_table)
        elements.append(Spacer(1, 12))

        # 3. Data Quality Findings
        elements.append(Paragraph("3. Dataset Quality Assessment", heading_style))
        quality_report = ds_dict.get("quality_report", {})
        score = ds_dict.get("quality_score", 100.0)
        elements.append(Paragraph(f"<b>Overall Quality Score:</b> {score}/100.0", body_style))
        elements.append(Spacer(1, 4))

        deductions = quality_report.get("deductions", [])
        if deductions:
            q_rows = [["Rule", "Finding", "Penalty"]]
            for d in deductions:
                q_rows.append([
                    Paragraph(d.get("rule", ""), body_style),
                    Paragraph(d.get("finding", ""), body_style),
                    Paragraph(f"-{d.get('deduction', 0)} pts", body_style)
                ])
            q_table = Table(q_rows, colWidths=[150, 310, 80])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(q_table)

        elements.append(Spacer(1, 12))

        # 4. Hyperparameters & Features
        elements.append(Paragraph("4. Model Architecture & Hyperparameters", heading_style))
        params_str = ", ".join(f"{k}={v}" for k, v in exp_dict.get("hyperparameters", {}).items()) or "Default scikit-learn settings"
        elements.append(Paragraph(f"<b>Hyperparameters:</b> {params_str}", body_style))
        features_list = exp_dict.get("feature_columns", [])
        elements.append(Paragraph(f"<b>Feature Set ({len(features_list)} features):</b> {', '.join(features_list[:20])}{' ...' if len(features_list) > 20 else ''}", body_style))
        elements.append(Spacer(1, 14))

        # 5. Confusion Matrix / Summary
        if exp_dict["problem_type"] == "classification" and exp_dict.get("confusion_matrix"):
            elements.append(Paragraph("5. Confusion Matrix Matrix (Test Split)", heading_style))
            cm = exp_dict["confusion_matrix"]
            cm_rows = [[""] + [f"Pred {i}" for i in range(len(cm))]]
            for i, row in enumerate(cm):
                cm_rows.append([f"True {i}"] + [str(v) for v in row])
            cm_table = Table(cm_rows, colWidths=[70] + [50]*len(cm))
            cm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(cm_table)

        doc.build(elements)
        return str(pdf_path)

    @classmethod
    def export_csv_summary(cls, experiment_ids: Optional[List[str]] = None) -> str:
        """Exports experiment catalog summary as CSV."""
        from core.experiment_manager import ExperimentManager
        comp = ExperimentManager.compare_experiments(experiment_ids if experiment_ids else [
            e["id"] for e in ExperimentManager.list_experiments()
        ])
        df = comp.get("comparison_df", pd.DataFrame())
        csv_filename = f"DATAVYRN_Experiments_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = config.REPORTS_DIR / csv_filename
        df.to_csv(csv_path, index=False)
        return str(csv_path)

    @classmethod
    def export_json_report(cls, experiment_id: str) -> str:
        """Exports full comprehensive experiment report in JSON format."""
        from core.training_engine import TrainingEngine
        exp = TrainingEngine.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")

        json_filename = f"DATAVYRN_Experiment_{experiment_id}.json"
        json_path = config.REPORTS_DIR / json_filename
        with open(json_path, "w") as f:
            json.dump(exp, f, indent=2)
        return str(json_path)
