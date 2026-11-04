import streamlit as st
import pandas as pd
from typing import Dict, Any, List

import config
from core.database import get_db_session
from core.models import Experiment
from core.training_engine import TrainingEngine
from core.evaluation_engine import EvaluationEngine
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon
from components.charts import (
    plot_confusion_matrix, plot_roc_curves, plot_feature_importance,
    plot_actual_vs_predicted, plot_residuals_distribution
)


def render(project_id: str):
    """Renders the comprehensive Model Evaluation Center with live interactive charts and metrics."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Model Evaluation Center — Benchmarks & Diagnostics</div>
            <div class="card-subtitle-clean">Validation matrix, classification ROC/AUC, confusion matrices, and feature attribution</div>
        </div>
        <span class="badge badge-accent">Validation Matrix</span>
    </div>
    """, unsafe_allow_html=True)

    experiments = TrainingEngine.list_experiments(project_id=project_id)
    if not experiments:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("line-chart", size=24)}</div>
            <div class="empty-state-title">No Trained Models Found</div>
            <div class="empty-state-desc">Train a model in the Training Lab to inspect performance curves, confusion matrices, and feature importance.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    exp_map = {
        e["id"]: f"{e['model_name']} ({e['problem_type'].capitalize()} • ID: {e['id'][:8]} • {e['created_at'][:16].replace('T', ' ') if e.get('created_at') else ''})"
        for e in experiments
    }

    current_exp_id = st.session_state.get("selected_experiment_id")
    if current_exp_id not in exp_map:
        current_exp_id = experiments[0]["id"]

    selected_exp_id = st.selectbox(
        "Select Trained Model Experiment",
        options=list(exp_map.keys()),
        format_func=lambda x: exp_map.get(x, x),
        key="eval_exp_select"
    )
    st.session_state["selected_experiment_id"] = selected_exp_id

    # Fetch evaluation data
    eval_bundle = EvaluationEngine.get_experiment_eval_data(selected_exp_id)
    exp = eval_bundle["experiment"]
    test_data = eval_bundle["test_data"]
    metrics = exp.get("metrics", {})
    pt = exp["problem_type"]

    # -------------------------------------------------------------
    # 1. High-Level KPI Cards
    # -------------------------------------------------------------
    if pt == "classification":
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi_card("Accuracy", f"{metrics.get('accuracy', 0)*100:.2f}%", "Test Split", icon_name="target", badge_variant="success")
        with c2:
            render_kpi_card("F1-Score (Macro)", f"{metrics.get('f1_macro', 0)*100:.2f}%", "Unweighted", icon_name="activity", badge_variant="success")
        with c3:
            render_kpi_card("Precision", f"{metrics.get('precision_macro', 0)*100:.2f}%", "Macro Avg", icon_name="search", badge_variant="neutral")
        with c4:
            render_kpi_card("Recall", f"{metrics.get('recall_macro', 0)*100:.2f}%", "Sensitivity", icon_name="line-chart", badge_variant="neutral")
        with c5:
            auc_val = metrics.get("roc_auc")
            auc_str = f"{auc_val:.3f}" if auc_val is not None else "N/A"
            render_kpi_card("ROC-AUC", auc_str, "OvR Discriminator", icon_name="award", badge_variant="success")

    elif pt == "regression":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("RMSE", f"{metrics.get('rmse', 0):.4f}", "Root Mean Sq Error", icon_name="line-chart", badge_variant="neutral")
        with c2:
            render_kpi_card("MAE", f"{metrics.get('mae', 0):.4f}", "Mean Abs Error", icon_name="activity", badge_variant="neutral")
        with c3:
            render_kpi_card("MSE", f"{metrics.get('mse', 0):.4f}", "Mean Sq Error", icon_name="sliders", badge_variant="neutral")
        with c4:
            render_kpi_card("R² Score", f"{metrics.get('r2', 0):.4f}", "Variance Explained", icon_name="award", badge_variant="success")

    elif pt == "unsupervised":
        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Silhouette Score", str(metrics.get("silhouette_score", "N/A")), "Cluster Cohesion", icon_name="award", badge_variant="success")
        with c2:
            render_kpi_card("Davies-Bouldin", str(metrics.get("davies_bouldin_score", "N/A")), "Lower is Better", icon_name="activity", badge_variant="neutral")
        with c3:
            render_kpi_card("Clusters / Samples", str(metrics.get("n_clusters", metrics.get("total_samples", "N/A"))), "Partitioning", icon_name="layers", badge_variant="neutral")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. Detailed Visualizations (Classification / Regression)
    # -------------------------------------------------------------
    if pt == "classification":
        col_cm, col_roc = st.columns(2)

        with col_cm:
            cm = exp.get("confusion_matrix", [])
            if cm:
                fig_cm = plot_confusion_matrix(cm)
                st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Confusion matrix not recorded for this model.")

        with col_roc:
            roc_data = EvaluationEngine.compute_roc_curve_data(test_data)
            if roc_data.get("curves"):
                fig_roc = plot_roc_curves(roc_data["curves"])
                st.plotly_chart(fig_roc, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("ROC curves require predicted class probabilities.")

        # Classification Report Table
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("file-text", size=14)} Detailed Classification Report (Per-Class Performance)
        </div>
        """, unsafe_allow_html=True)
        report_dict = exp.get("classification_report", {})
        if report_dict:
            rep_rows = []
            for k, v in report_dict.items():
                if isinstance(v, dict):
                    rep_rows.append({
                        "Class / Metric": k,
                        "Precision": round(v.get("precision", 0), 4),
                        "Recall": round(v.get("recall", 0), 4),
                        "F1-Score": round(v.get("f1-score", 0), 4),
                        "Support": int(v.get("support", 0))
                    })
            st.dataframe(pd.DataFrame(rep_rows), use_container_width=True, hide_index=True)

    elif pt == "regression":
        col_reg1, col_reg2 = st.columns(2)

        with col_reg1:
            y_t = test_data.get("y_true", [])
            y_p = test_data.get("y_pred", [])
            if y_t and y_p:
                fig_act = plot_actual_vs_predicted(y_t, y_p)
                st.plotly_chart(fig_act, use_container_width=True, config={"displayModeBar": False})

        with col_reg2:
            res_data = EvaluationEngine.compute_residuals_data(test_data)
            if res_data.get("residuals"):
                fig_res = plot_residuals_distribution(res_data["residuals"])
                st.plotly_chart(fig_res, use_container_width=True, config={"displayModeBar": False})

    # -------------------------------------------------------------
    # 3. Feature Importance (Compatible Models)
    # -------------------------------------------------------------
    feat_imp = exp.get("feature_importance", {})
    if feat_imp:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("layers", size=14)} Model Feature Importance Analysis
        </div>
        """, unsafe_allow_html=True)
        fig_feat = plot_feature_importance(feat_imp)
        st.plotly_chart(fig_feat, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr style='border-color: var(--border-subtle); margin: 20px 0;'>", unsafe_allow_html=True)

    # Direct handoff to Error Analysis Workbench
    col_hand1, col_hand2 = st.columns([8, 2])
    with col_hand2:
        if st.button("Inspect Prediction Errors", type="primary", use_container_width=True):
            st.session_state["active_page"] = "error_analysis"
            st.rerun()
