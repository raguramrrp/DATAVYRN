import streamlit as st
import pandas as pd
from typing import Dict, Any, List

import config
from core.database import get_db_session
from core.models import Experiment, Dataset
from core.training_engine import TrainingEngine
from core.error_analyzer import ErrorAnalyzer
from core.dataset_manager import DatasetManager
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the Error Analysis Workbench with guided diagnosis and data correction workflows."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Error Analysis Workbench — Model Diagnostics & Correction</div>
            <div class="card-subtitle-clean">Root-cause failure inspection, confused class pairs, and verified ground-truth correction loops</div>
        </div>
        <span class="badge badge-warning">Root Cause Diagnostics</span>
    </div>
    """, unsafe_allow_html=True)

    experiments = TrainingEngine.list_experiments(project_id=project_id)
    if not experiments:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("alert-triangle", size=24)}</div>
            <div class="empty-state-title">No Trained Models Available for Error Analysis</div>
            <div class="empty-state-desc">Train a classification or regression model in the Training Lab to isolate misclassifications and high-residual samples.</div>
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

    selected_exp_id = st.selectbox(
        "Select Model Experiment for Error Analysis",
        options=list(exp_map.keys()),
        format_func=lambda x: exp_map.get(x, x),
        key="err_exp_select"
    )
    st.session_state["selected_experiment_id"] = selected_exp_id

    selected_exp = next(e for e in experiments if e["id"] == selected_exp_id)
    pt = selected_exp["problem_type"]

    # -------------------------------------------------------------
    # 1. Classification Error Analysis
    # -------------------------------------------------------------
    if pt == "classification":
        error_bundle = ErrorAnalyzer.get_classification_errors(selected_exp_id)
        errors = error_bundle.get("errors", [])
        confused_pairs = error_bundle.get("confused_pairs", {})
        total_samples = error_bundle.get("total_samples", 0)
        error_rate = error_bundle.get("error_rate", 0.0)

        # KPI Summary
        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Test Samples", str(total_samples), "Held-out Validation", icon_name="database", badge_variant="neutral")
        with c2:
            render_kpi_card("Incorrect Predictions", str(len(errors)), f"{error_rate}% Error Rate", icon_name="alert-triangle", badge_variant="warning" if len(errors) > 0 else "success")
        with c3:
            top_confusion = list(confused_pairs.keys())[0] if confused_pairs else "None"
            render_kpi_card("Top Confused Pair", top_confusion, f"{list(confused_pairs.values())[0] if confused_pairs else 0} occurrences", icon_name="git-compare", badge_variant="warning")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        if not errors:
            st.markdown(f"""
            <div style="padding: 16px; border: 1px solid var(--border-subtle); border-radius: 6px; background: var(--bg-card); display: flex; align-items: center; gap: 12px;">
                <span style="color: #10b981;">{get_svg_icon("check-circle", size=20)}</span>
                <div>
                    <div style="font-weight: 600; font-size: 0.85rem; color: var(--text-primary);">Zero Prediction Errors Detected</div>
                    <div style="font-size: 0.78rem; color: var(--text-secondary);">The model achieved 100% accuracy on this test partition with no misclassified records.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col_tbl, col_diag = st.columns([6, 4])

            with col_tbl:
                st.markdown(f"""
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    {get_svg_icon("x", size=14)} Misclassified Records ({len(errors)} Samples)
                </div>
                """, unsafe_allow_html=True)
                err_df = pd.DataFrame(errors)
                st.dataframe(
                    err_df[["sample_index", "actual", "predicted", "confidence", "suspected_cause"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Confused pairs summary
                st.markdown(f"""
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    {get_svg_icon("git-compare", size=14)} Frequently Confused Class Pairs
                </div>
                """, unsafe_allow_html=True)
                pairs_data = [{"Confused Pair (Actual -> Predicted)": k, "Error Count": v} for k, v in confused_pairs.items()]
                st.table(pd.DataFrame(pairs_data))

            with col_diag:
                st.markdown(f"""
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    {get_svg_icon("search", size=14)} Guided Error Investigation
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 10px;'>Select a sample index to record diagnosis notes or execute a verified data/label correction.</div>", unsafe_allow_html=True)

                sample_indices = [e["sample_index"] for e in errors]
                chosen_idx = st.selectbox("Select Sample Index", sample_indices, key="diag_sample_idx")
                chosen_sample = next(e for e in errors if e["sample_index"] == chosen_idx)

                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 12px;">
                    <div style="font-size: 0.78rem; margin-bottom: 4px;"><strong>Row Index:</strong> <code style="font-family: var(--font-mono); color: var(--text-primary);">{chosen_idx}</code></div>
                    <div style="font-size: 0.78rem; margin-bottom: 4px;"><strong>Ground Truth:</strong> <span class="badge badge-success font-mono">{chosen_sample['actual']}</span></div>
                    <div style="font-size: 0.78rem; margin-bottom: 4px;"><strong>Model Predicted:</strong> <span class="badge badge-danger font-mono">{chosen_sample['predicted']}</span></div>
                    <div style="font-size: 0.78rem;"><strong>Confidence:</strong> <span style="font-family: var(--font-mono);">{f"{chosen_sample['confidence']*100:.1f}%" if chosen_sample['confidence'] else 'N/A'}</span></div>
                </div>
                """, unsafe_allow_html=True)

                with st.form("form_error_diagnosis"):
                    suspected_cause = st.selectbox(
                        "Suspected Cause of Error",
                        [
                            "Ambiguous or Incorrect Source Label",
                            "Feature Values are Outliers / Measurement Noise",
                            "Edge-case sample lacking feature separation",
                            "Model Underfitting / Capacity Limitation"
                        ]
                    )
                    action_plan = st.selectbox(
                        "Proposed Action",
                        [
                            "Relabel ground truth in dataset",
                            "Drop erroneous row from dataset",
                            "Keep sample (model limitation only)"
                        ]
                    )
                    corrected_label = st.text_input("Corrected Ground Truth Label (if relabeling)", str(chosen_sample["actual"]))

                    submitted_note = st.form_submit_button("Log Diagnostic Note", use_container_width=True)

                    if submitted_note:
                        ErrorAnalyzer.log_error_investigation(
                            exp_id=selected_exp_id,
                            sample_index=chosen_idx,
                            true_value=chosen_sample["actual"],
                            predicted_value=chosen_sample["predicted"],
                            confidence=chosen_sample.get("confidence") or 0.0,
                            suspected_cause=suspected_cause,
                            action_taken=action_plan,
                            corrected_value=corrected_label
                        )
                        st.success(f"Recorded diagnosis for sample {chosen_idx}.")
                        st.rerun()

                st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

                # Guided Correction & Versioning Trigger
                st.markdown(f"""
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    {get_svg_icon("save", size=14)} Apply Verified Correction to Dataset
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;'>Create a new dataset version with this correction applied, then retrain to measure improvements.</div>", unsafe_allow_html=True)

                corr_action = st.radio("Correction Action", ["Relabel Target", "Drop Row"], horizontal=True)

                if st.button("Apply Correction & Create New Version", type="primary", use_container_width=True):
                    with st.spinner("Applying verified correction and creating new version..."):
                        try:
                            corrections = []
                            if corr_action == "Relabel Target":
                                corrections.append({
                                    "index": chosen_idx,
                                    "column": selected_exp["target_column"],
                                    "new_value": corrected_label,
                                    "action": "modify"
                                })
                            else:
                                corrections.append({
                                    "index": chosen_idx,
                                    "action": "drop"
                                })

                            new_ver = ErrorAnalyzer.apply_data_corrections(
                                dataset_id=selected_exp["dataset_id"],
                                corrections=corrections,
                                change_summary=f"Corrected sample {chosen_idx} based on error analysis of {selected_exp['model_name']}"
                            )

                            st.success(f"Created Dataset Version {new_ver.version_number}. You can now retrain in Training Lab.")
                            if st.button("Retrain Model in Training Lab"):
                                st.session_state["active_page"] = "training_lab"
                                st.rerun()

                        except Exception as e:
                            st.error(f"Correction failed: {str(e)}")

    # -------------------------------------------------------------
    # 2. Regression Error Analysis
    # -------------------------------------------------------------
    elif pt == "regression":
        reg_bundle = ErrorAnalyzer.get_regression_errors(selected_exp_id, top_n=20)
        high_errors = reg_bundle.get("high_errors", [])

        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("alert-triangle", size=14)} Top {len(high_errors)} Highest Residual Errors
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(high_errors), use_container_width=True, hide_index=True)

    else:
        st.info("Error analysis is specialized for supervised Classification and Regression tasks.")
