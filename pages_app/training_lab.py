import streamlit as st
import pandas as pd
from typing import Dict, Any, List

import config
from core.database import get_db_session
from core.models import Dataset, Experiment
from core.dataset_manager import DatasetManager
from core.training_engine import TrainingEngine
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the core Training Lab module with actual scikit-learn execution and persistence."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Training Lab — Machine Learning Model Compiler</div>
            <div class="card-subtitle-clean">Algorithm selection, hyperparameter tuning, cross-validation, and production model compilation</div>
        </div>
        <span class="badge badge-accent">Scikit-Learn Engine</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Dataset Selection
    datasets = DatasetManager.list_datasets(project_id=project_id, dataset_type="tabular")
    if not datasets:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("cpu", size=24)}</div>
            <div class="empty-state-title">No Datasets Available for Training</div>
            <div class="empty-state-desc">Import a tabular dataset in the Datasets module to begin configuring model architectures and hyperparameters.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    ds_map = {d["id"]: f"{d['name']} (v{d['current_version']} • {d['record_count']} rows)" for d in datasets}
    current_ds_id = st.session_state.get("selected_dataset_id")
    if current_ds_id not in ds_map:
        current_ds_id = datasets[0]["id"]

    col_ds, col_prob = st.columns([6, 4])

    with col_ds:
        selected_ds_id = st.selectbox(
            "Select Training Dataset",
            options=list(ds_map.keys()),
            format_func=lambda x: ds_map.get(x, x),
            key="train_dataset_select"
        )
        st.session_state["selected_dataset_id"] = selected_ds_id

    # Load dataframe to inspect columns
    df, current_ver = DatasetManager.load_tabular_dataframe(selected_ds_id)

    with col_prob:
        problem_type = st.selectbox(
            "Problem Category",
            ["Classification", "Regression", "Unsupervised"],
            key="train_prob_type"
        ).lower()

    # -------------------------------------------------------------
    # Target and Feature Selection
    # -------------------------------------------------------------
    col_targ, col_feat = st.columns([4, 8])

    with col_targ:
        if problem_type in ["classification", "regression"]:
            target_col = st.selectbox(
                "Target Variable (Y)",
                options=df.columns.tolist(),
                index=len(df.columns)-1,  # default to last column
                key="train_target_col"
            )
            candidate_features = [c for c in df.columns if c != target_col]
        else:
            target_col = None
            candidate_features = df.select_dtypes(include=["number"]).columns.tolist()

    with col_feat:
        feature_cols = st.multiselect(
            f"Feature Variables (X) — {len(candidate_features)} Available",
            options=candidate_features,
            default=candidate_features,
            key="train_feature_cols"
        )

    st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Algorithm and Hyperparameters
    # -------------------------------------------------------------
    supported_models = TrainingEngine.get_supported_models(problem_type)
    if not supported_models:
        st.error(f"No models registered for problem type {problem_type}")
        return

    col_algo, col_params = st.columns([4, 8])

    with col_algo:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("cpu", size=14)} Model Architecture
        </div>
        """, unsafe_allow_html=True)
        selected_algo_key = st.radio(
            "Select Algorithm",
            options=list(supported_models.keys()),
            format_func=lambda k: supported_models[k],
            key="train_algo_key"
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        test_split = st.slider("Test Split Ratio (%)", 10, 40, 20, 5, key="train_test_split") / 100.0
        cv_folds = st.slider("Cross-Validation Folds", 2, 10, 5, key="train_cv_folds")
        random_seed = st.number_input("Random State Seed", value=42, key="train_seed")

    with col_params:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("sliders", size=14)} Hyperparameter Tuning
        </div>
        """, unsafe_allow_html=True)
        hyperparams = {}

        if selected_algo_key in ["rf", "rf_regressor"]:
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                hyperparams["n_estimators"] = st.slider("Number of Estimators (Trees)", 10, 500, 100, 10)
            with c_p2:
                max_d = st.slider("Max Tree Depth (0 = Unlimited)", 0, 30, 6, 1)
                hyperparams["max_depth"] = max_d if max_d > 0 else None

        elif selected_algo_key in ["dt", "dt_regressor"]:
            max_d = st.slider("Max Tree Depth (0 = Unlimited)", 0, 30, 4, 1)
            hyperparams["max_depth"] = max_d if max_d > 0 else None

        elif selected_algo_key == "lr":
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                hyperparams["C"] = st.slider("Inverse Regularization Strength (C)", 0.01, 10.0, 1.0, 0.05)
            with c_p2:
                hyperparams["max_iter"] = st.slider("Max Iterations", 100, 1000, 500, 50)

        elif selected_algo_key == "knn":
            hyperparams["n_neighbors"] = st.slider("Number of Neighbors (K)", 1, 25, 5, 1)

        elif selected_algo_key == "svm":
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                hyperparams["C"] = st.slider("Regularization Parameter (C)", 0.1, 10.0, 1.0, 0.1)
            with c_p2:
                hyperparams["kernel"] = st.selectbox("Kernel Function", ["rbf", "linear", "poly", "sigmoid"])

        elif selected_algo_key == "kmeans":
            hyperparams["n_clusters"] = st.slider("Number of Clusters (K)", 2, 12, 3, 1)

        elif selected_algo_key == "isolation_forest":
            hyperparams["contamination"] = st.slider("Contamination Outlier Ratio", 0.01, 0.25, 0.05, 0.01)

        elif selected_algo_key == "pca":
            hyperparams["n_components"] = st.slider("Principal Components Count", 1, min(len(feature_cols), 10), min(len(feature_cols), 2), 1)

        st.json(hyperparams)

    st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Launch Real Training
    # -------------------------------------------------------------
    col_info, col_launch = st.columns([7, 3])

    with col_info:
        st.markdown(f"""
        <div style="font-size: 0.78rem; color: var(--text-secondary); padding: 8px 12px; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 6px;">
            <strong style="color: var(--text-primary);">Execution Pipeline:</strong> Dataset <code style="font-family: var(--font-mono); color: var(--accent-primary);">{selected_ds_id}</code> (v{current_ver}) &nbsp;•&nbsp; 
            Features: <code style="font-family: var(--font-mono);">{len(feature_cols)}</code> &nbsp;•&nbsp; 
            Target: <code style="font-family: var(--font-mono);">{target_col or 'Unsupervised'}</code> &nbsp;•&nbsp; 
            Model: <code style="font-family: var(--font-mono);">{supported_models.get(selected_algo_key)}</code>
        </div>
        """, unsafe_allow_html=True)

    with col_launch:
        start_btn = st.button("Start Model Training", type="primary", use_container_width=True)

    if start_btn:
        if not feature_cols:
            st.error("Select at least one feature column.")
            return

        with st.spinner(f"Training {supported_models.get(selected_algo_key)} on {len(df)} samples..."):
            try:
                exp = TrainingEngine.train_model(
                    project_id=project_id,
                    dataset_id=selected_ds_id,
                    problem_type=problem_type,
                    algorithm_key=selected_algo_key,
                    target_column=target_col,
                    feature_columns=feature_cols,
                    hyperparameters=hyperparams,
                    test_split_ratio=test_split,
                    random_state=int(random_seed),
                    cv_folds=int(cv_folds),
                    dataset_version=current_ver
                )

                st.success(f"Model trained successfully in {exp['training_duration_sec']}s! Experiment ID: `{exp['id']}`")
                st.session_state["selected_experiment_id"] = exp["id"]

                # Quick metrics summary
                metrics = exp.get("metrics", {})
                m_cols = st.columns(len(metrics))
                for i, (m_name, m_val) in enumerate(metrics.items()):
                    with m_cols[i]:
                        val_str = f"{m_val*100:.2f}%" if "acc" in m_name or "f1" in m_name else str(m_val)
                        render_kpi_card(m_name.replace("_", " ").upper(), val_str, "Benchmark", icon_name="activity", badge_variant="success")

                col_go_eval, col_go_err = st.columns(2)
                with col_go_eval:
                    if st.button("Open in Model Evaluation Center", type="primary", use_container_width=True):
                        st.session_state["active_page"] = "evaluation"
                        st.rerun()
                with col_go_err:
                    if st.button("Open in Error Analysis Workbench", use_container_width=True):
                        st.session_state["active_page"] = "error_analysis"
                        st.rerun()

            except Exception as e:
                st.error(f"Training failed: {str(e)}")
