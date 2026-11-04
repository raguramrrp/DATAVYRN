import streamlit as st
import pandas as pd
from typing import Dict, Any, List

import config
from core.database import get_db_session
from core.models import Experiment
from core.training_engine import TrainingEngine
from core.experiment_manager import ExperimentManager
from core.report_generator import ReportGenerator
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the persistent Experiment Registry and Side-by-Side Model Comparison Center."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Experiment Registry — Tracking & Multi-Model Comparison</div>
            <div class="card-subtitle-clean">Persistent audit log, lineage tracking, side-by-side benchmarking, and leaderboard generation</div>
        </div>
        <span class="badge badge-accent">Model Registry</span>
    </div>
    """, unsafe_allow_html=True)

    experiments = TrainingEngine.list_experiments(project_id=project_id)
    if not experiments:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("git-compare", size=24)}</div>
            <div class="empty-state-title">No Experiments Logged</div>
            <div class="empty-state-desc">Train models in the Training Lab to automatically populate the experiment registry and enable side-by-side benchmarking.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    tab_registry, tab_compare = st.tabs(["Experiment Catalog", "Multi-Model Comparison"])

    # -------------------------------------------------------------
    # TAB 1: EXPERIMENT CATALOG
    # -------------------------------------------------------------
    with tab_registry:
        c_f1, c_f2 = st.columns([5, 5])
        with c_f1:
            problem_filter = st.selectbox("Filter Problem Type", ["All", "Classification", "Regression", "Unsupervised"])
        with c_f2:
            sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Training Duration"])

        filtered_exps = experiments
        if problem_filter != "All":
            filtered_exps = [e for e in filtered_exps if e["problem_type"].lower() == problem_filter.lower()]

        if sort_by == "Newest First":
            filtered_exps.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        elif sort_by == "Oldest First":
            filtered_exps.sort(key=lambda x: x.get("created_at") or "")
        elif sort_by == "Training Duration":
            filtered_exps.sort(key=lambda x: x.get("training_duration_sec") or 0, reverse=True)

        rows = []
        for e in filtered_exps:
            m = e.get("metrics", {})
            primary_metric = f"Acc: {m.get('accuracy', 0)*100:.1f}%" if e["problem_type"] == "classification" else (
                f"RMSE: {m.get('rmse', 0):.3f}" if e["problem_type"] == "regression" else f"Clusters: {m.get('n_clusters', 0)}"
            )
            rows.append({
                "Experiment ID": e["id"],
                "Model": e["model_name"],
                "Problem Type": e["problem_type"].capitalize(),
                "Target": e["target_column"] or "N/A",
                "Dataset": f"{e.get('dataset_name', 'DS')} (v{e['dataset_version']})",
                "Primary Metric": primary_metric,
                "Duration (s)": f"{e['training_duration_sec']}s",
                "Date": e["created_at"][:19].replace("T", " ") if e.get("created_at") else "N/A",
                "Status": e["status"].upper()
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Quick actions
        col_act1, col_act2 = st.columns([7, 3])
        with col_act2:
            if st.button("Export Catalog to CSV", use_container_width=True):
                csv_path = ReportGenerator.export_csv_summary([e["id"] for e in filtered_exps])
                with open(csv_path, "r") as f:
                    st.download_button(
                        "Download CSV File",
                        data=f.read(),
                        file_name="DATAVYRN_Experiment_Catalog.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

    # -------------------------------------------------------------
    # TAB 2: MULTI-MODEL COMPARISON
    # -------------------------------------------------------------
    with tab_compare:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("git-compare", size=14)} Side-by-Side Model Benchmarking
        </div>
        """, unsafe_allow_html=True)
        all_ids = [e["id"] for e in experiments]
        id_labels = {e["id"]: f"{e['model_name']} ({e['id'][:8]} • v{e['dataset_version']})" for e in experiments}

        selected_compare_ids = st.multiselect(
            "Select 2 or More Experiments to Compare",
            options=all_ids,
            default=all_ids[:min(3, len(all_ids))],
            format_func=lambda x: id_labels.get(x, x),
            key="comp_multiselect"
        )

        if len(selected_compare_ids) < 2:
            st.info("Select at least two experiments from the list above to generate comparative benchmarks.")
        else:
            comp_res = ExperimentManager.compare_experiments(selected_compare_ids)
            comp_df = comp_res.get("comparison_df", pd.DataFrame())
            best_exp = comp_res.get("best_experiment")
            best_reason = comp_res.get("best_reason")

            if best_exp:
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 16px; border-left: 3px solid var(--accent-primary);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.82rem; font-weight: 600; color: var(--accent-primary); text-transform: uppercase; letter-spacing: 0.04em;">Top Performing Model Recommendation</span>
                        <span class="badge badge-accent font-mono">{best_exp['model_name']}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 6px;">
                        <strong style="color: var(--text-primary);">Evaluation Criterion:</strong> {best_reason}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.dataframe(comp_df, use_container_width=True, hide_index=True)

            # Metric-aware comparative bar chart
            st.markdown(f"""
            <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                {get_svg_icon("line-chart", size=14)} Comparative Performance Chart
            </div>
            """, unsafe_allow_html=True)
            if "Accuracy" in comp_df.columns:
                chart_metric = st.selectbox("Select Metric to Chart", [c for c in ["Accuracy", "F1 (Macro)", "Precision (Macro)", "Training Time (s)"] if c in comp_df.columns])
                st.bar_chart(comp_df.set_index("Model")[chart_metric])
            elif "RMSE" in comp_df.columns:
                chart_metric = st.selectbox("Select Metric to Chart", [c for c in ["RMSE", "MAE", "R²", "Training Time (s)"] if c in comp_df.columns])
                st.bar_chart(comp_df.set_index("Model")[chart_metric])

            # Export comparison
            col_c1, col_c2 = st.columns([7, 3])
            with col_c2:
                if st.button("Generate Technical Report for Top Model", type="primary", use_container_width=True):
                    st.session_state["selected_experiment_id"] = best_exp["id"]
                    st.session_state["active_page"] = "reports"
                    st.rerun()
