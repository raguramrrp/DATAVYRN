import streamlit as st
import json
from pathlib import Path

import config
from core.database import get_db_session
from core.models import Experiment
from core.training_engine import TrainingEngine
from core.report_generator import ReportGenerator
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the comprehensive Report Generation and Technical Documentation Hub."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Report Generation — Technical Audits & Export Suite</div>
            <div class="card-subtitle-clean">Automated audit report compilation, vector PDF generation, tabular CSV and JSON export pipelines</div>
        </div>
        <span class="badge badge-accent">ReportLab Engine</span>
    </div>
    """, unsafe_allow_html=True)

    experiments = TrainingEngine.list_experiments(project_id=project_id)
    if not experiments:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("file-text", size=24)}</div>
            <div class="empty-state-title">No Experiment Records Available</div>
            <div class="empty-state-desc">Train a model in the Training Lab to automatically compile compliance reports and technical audit documents.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    exp_map = {
        e["id"]: f"{e['model_name']} ({e['problem_type'].capitalize()} • ID: {e['id'][:8]})"
        for e in experiments
    }

    current_exp_id = st.session_state.get("selected_experiment_id")
    if current_exp_id not in exp_map:
        current_exp_id = experiments[0]["id"]

    col_sel, col_btns = st.columns([6, 4])
    with col_sel:
        selected_exp_id = st.selectbox(
            "Select Experiment for Report Export",
            options=list(exp_map.keys()),
            format_func=lambda x: exp_map.get(x, x),
            key="rep_exp_select"
        )
        st.session_state["selected_experiment_id"] = selected_exp_id

    selected_exp = next(e for e in experiments if e["id"] == selected_exp_id)

    # -------------------------------------------------------------
    # Report Export Actions
    # -------------------------------------------------------------
    with col_btns:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns(3)

        with col_b1:
            if st.button("Build PDF", type="primary", use_container_width=True):
                with st.spinner("Compiling ReportLab PDF document..."):
                    pdf_path = ReportGenerator.generate_pdf_report(selected_exp_id)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "Download PDF",
                            data=f.read(),
                            file_name=Path(pdf_path).name,
                            mime="application/pdf",
                            use_container_width=True
                        )

        with col_b2:
            if st.button("CSV Export", use_container_width=True):
                csv_path = ReportGenerator.export_csv_summary([selected_exp_id])
                with open(csv_path, "r") as f:
                    st.download_button(
                        "Download CSV",
                        data=f.read(),
                        file_name=Path(csv_path).name,
                        mime="text/csv",
                        use_container_width=True
                    )

        with col_b3:
            if st.button("JSON Export", use_container_width=True):
                json_path = ReportGenerator.export_json_report(selected_exp_id)
                with open(json_path, "r") as f:
                    st.download_button(
                        "Download JSON",
                        data=f.read(),
                        file_name=Path(json_path).name,
                        mime="application/json",
                        use_container_width=True
                    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Interactive Report Document Preview
    # -------------------------------------------------------------
    st.markdown(f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 24px; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 14px; margin-bottom: 20px;">
            <div>
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em;">DATAVYRN — Technical Experiment Audit</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px;">Unified Data Intelligence & Machine Learning Benchmark</div>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-success">Verified Validation</span>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px; font-family: var(--font-mono);">Engine v1.0 • Offline Ready</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Preview Sections
    p_c1, p_c2 = st.columns(2)
    with p_c1:
        st.markdown(f"""
        **1. Experiment Identity & Architecture**
        - **Experiment ID:** `{selected_exp['id']}`
        - **Model Algorithm:** `{selected_exp['model_name']}`
        - **Problem Domain:** `{selected_exp['problem_type'].capitalize()}`
        - **Dataset Reference:** `{selected_exp.get('dataset_name', 'Dataset')} (v{selected_exp['dataset_version']})`
        - **Target Variable:** `{selected_exp.get('target_column') or 'Unsupervised'}`
        """)

    with p_c2:
        st.markdown(f"""
        **2. Computational Profile**
        - **Training Execution Time:** `{selected_exp['training_duration_sec']} seconds`
        - **Validation Strategy:** `{int(selected_exp['test_split_ratio']*100)}% Holdout / {selected_exp['cv_folds']}-Fold Cross-Validation`
        - **Random Seed:** `{selected_exp['random_state']}`
        - **Feature Dimension:** `{len(selected_exp.get('feature_columns', []))} features`
        """)

    st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

    st.markdown("**3. Audited Metric Matrix**")
    metrics = selected_exp.get("metrics", {})
    m_cols = st.columns(len(metrics))
    for i, (k, v) in enumerate(metrics.items()):
        with m_cols[i]:
            val_display = f"{v*100:.2f}%" if "acc" in k or "f1" in k else str(v)
            st.metric(k.replace("_", " ").title(), val_display)

    st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

    st.markdown("**4. Model Hyperparameters & Configuration**")
    st.json(selected_exp.get("hyperparameters", {}))

    st.markdown("</div>", unsafe_allow_html=True)
