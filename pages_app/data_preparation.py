import streamlit as st
import pandas as pd
from typing import List, Dict, Any

import config
from core.database import get_db_session
from core.models import Dataset, DatasetVersion
from core.dataset_manager import DatasetManager
from core.preprocessing import PreprocessingPipeline
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the comprehensive Tabular Data Preparation and Feature Engineering Studio."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Data Preparation Studio — Pipeline & Feature Engineering</div>
            <div class="card-subtitle-clean">Traceable transformation pipeline, data cleaning, outlier handling, and versioned feature engineering</div>
        </div>
        <span class="badge badge-accent">Traceable Pipeline</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Select Tabular Dataset
    datasets = DatasetManager.list_datasets(project_id=project_id, dataset_type="tabular")
    if not datasets:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("database", size=24)}</div>
            <div class="empty-state-title">No Tabular Datasets Available</div>
            <div class="empty-state-desc">Import a CSV, Excel, or JSON dataset in the Datasets module to begin data preparation and feature engineering.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    ds_map = {d["id"]: f"{d['name']} (v{d['current_version']} • {d['record_count']} rows)" for d in datasets}
    current_ds_id = st.session_state.get("selected_dataset_id")
    if current_ds_id not in ds_map:
        current_ds_id = datasets[0]["id"]

    col_ds, col_ver = st.columns([7, 3])
    with col_ds:
        selected_ds_id = st.selectbox(
            "Select Dataset to Prepare",
            options=list(ds_map.keys()),
            format_func=lambda x: ds_map.get(x, x),
            key="prep_dataset_select"
        )
        st.session_state["selected_dataset_id"] = selected_ds_id

    # Load baseline dataframe
    raw_df, current_ver = DatasetManager.load_tabular_dataframe(selected_ds_id)

    # Store working pipeline in session state
    if "prep_pipeline" not in st.session_state or st.session_state.get("prep_pipeline_ds_id") != selected_ds_id:
        st.session_state["prep_pipeline"] = PreprocessingPipeline(raw_df)
        st.session_state["prep_pipeline_ds_id"] = selected_ds_id

    pipeline: PreprocessingPipeline = st.session_state["prep_pipeline"]
    current_df = pipeline.get_df()

    with col_ver:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button(f"Reset to Original v{current_ver}", use_container_width=True):
            st.session_state["prep_pipeline"] = PreprocessingPipeline(raw_df)
            st.rerun()

    # Metrics comparison (Original vs Transformed)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        row_delta = f"{len(current_df) - len(raw_df):+d} rows"
        render_kpi_card("Total Rows", f"{len(current_df):,}", row_delta, icon_name="database")
    with c2:
        col_delta = f"{len(current_df.columns) - len(raw_df.columns):+d} cols"
        render_kpi_card("Columns", str(len(current_df.columns)), col_delta, icon_name="layers")
    with c3:
        null_count = int(current_df.isna().sum().sum())
        render_kpi_card("Missing Cells", str(null_count), "Zero Null Target" if null_count == 0 else f"{null_count} Remaining", icon_name="alert-triangle", badge_variant="warning" if null_count > 0 else "success")
    with c4:
        dup_count = int(current_df.duplicated().sum())
        render_kpi_card("Duplicate Rows", str(dup_count), "Deduplicated" if dup_count == 0 else f"{dup_count} Detected", icon_name="git-compare", badge_variant="warning" if dup_count > 0 else "success")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Interactive Transformation Controls
    # -------------------------------------------------------------
    col_tools, col_view = st.columns([5, 7])

    with col_tools:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("sliders", size=14)} Transformation Recipe
        </div>
        """, unsafe_allow_html=True)

        tool_category = st.radio(
            "Transformation Category",
            ["Data Cleaning", "Feature Engineering", "Column Management"],
            horizontal=True
        )

        if tool_category == "Data Cleaning":
            st.markdown("###### Missing Value & Duplicate Handling")
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("Drop Duplicate Rows", use_container_width=True):
                    pipeline.remove_duplicates()
                    st.rerun()
            with col_act2:
                if st.button("Drop Rows with Any Nulls", use_container_width=True):
                    pipeline.drop_missing_rows()
                    st.rerun()

            st.markdown("<hr style='border-color: var(--border-subtle); margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("###### Impute Missing Values")
            imp_col = st.selectbox("Select Column to Impute", current_df.columns, key="imp_col_sel")
            imp_strategy = st.selectbox("Imputation Strategy", ["mean", "median", "mode", "constant"], key="imp_strat_sel")
            imp_const = st.text_input("Constant Value (if constant selected)", "0", key="imp_const_val")

            if st.button("Apply Imputation", type="primary", use_container_width=True):
                pipeline.impute_missing(imp_col, strategy=imp_strategy, constant_value=imp_const)
                st.rerun()

            st.markdown("<hr style='border-color: var(--border-subtle); margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("###### Statistical Outlier Clipping (IQR Rule)")
            num_cols = current_df.select_dtypes(include=["number"]).columns.tolist()
            if num_cols:
                clip_cols = st.multiselect("Select Numeric Columns to Clip", num_cols, default=num_cols[:3], key="clip_cols_sel")
                clip_factor = st.slider("IQR Multiplier (Default 1.5)", 1.0, 3.0, 1.5, 0.1, key="clip_iqr_slider")
                if st.button("Clip Outliers", use_container_width=True):
                    pipeline.clip_outliers_iqr(clip_cols, factor=clip_factor)
                    st.rerun()

        elif tool_category == "Feature Engineering":
            st.markdown("###### Categorical Encoding")
            cat_cols = current_df.select_dtypes(include=["object", "category"]).columns.tolist()

            col_enc1, col_enc2 = st.columns(2)
            with col_enc1:
                st.markdown("**Label Encoding**")
                if cat_cols:
                    le_col = st.selectbox("Select Column to Label Encode", cat_cols, key="le_col_sel")
                    if st.button("Apply Label Encoding", use_container_width=True):
                        pipeline.label_encode([le_col])
                        st.rerun()
                else:
                    st.info("No categorical columns for label encoding.")

            with col_enc2:
                st.markdown("**One-Hot Encoding**")
                if cat_cols:
                    ohe_cols = st.multiselect("Select Categorical Columns", cat_cols, key="ohe_cols_sel")
                    if st.button("Apply One-Hot Encoding", use_container_width=True):
                        pipeline.one_hot_encode(ohe_cols)
                        st.rerun()
                else:
                    st.info("No categorical columns for one-hot encoding.")

            st.markdown("<hr style='border-color: var(--border-subtle); margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("###### Feature Scaling")
            num_cols = current_df.select_dtypes(include=["number"]).columns.tolist()
            if num_cols:
                scale_cols = st.multiselect("Select Columns to Scale", num_cols, default=num_cols[:5], key="scale_cols_sel")
                scaler_type = st.selectbox("Scaler Type", ["standard", "minmax", "robust"], key="scale_type_sel")
                if st.button("Apply Scaling", type="primary", use_container_width=True):
                    pipeline.scale_features(scale_cols, method=scaler_type)
                    st.rerun()

        elif tool_category == "Column Management":
            st.markdown("###### Drop & Rename Columns")
            drop_candidates = st.multiselect("Select Columns to Drop", current_df.columns.tolist(), key="drop_candidates_sel")
            if st.button("Drop Selected Columns", use_container_width=True):
                if drop_candidates:
                    pipeline.drop_columns(drop_candidates)
                    st.rerun()

            st.markdown("<hr style='border-color: var(--border-subtle); margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("###### Rename Column")
            old_name = st.selectbox("Select Column", current_df.columns.tolist(), key="ren_old_name")
            new_name = st.text_input("New Column Name", old_name, key="ren_new_name")
            if st.button("Rename Column", use_container_width=True):
                if new_name and new_name != old_name:
                    pipeline.rename_column(old_name, new_name)
                    st.rerun()

            st.markdown("<hr style='border-color: var(--border-subtle); margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("###### Cast Data Type")
            cast_col = st.selectbox("Select Column to Cast", current_df.columns.tolist(), key="cast_col_sel")
            target_type = st.selectbox("Target Type", ["int", "float", "string", "category"], key="cast_type_sel")
            if st.button("Convert Type", use_container_width=True):
                pipeline.cast_type(cast_col, target_type)
                st.rerun()

    # -------------------------------------------------------------
    # RIGHT PANEL: PREVIEW & PERSISTENCE
    # -------------------------------------------------------------
    with col_view:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("search", size=14)} Transformed Data Preview (First 50 Rows)
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(current_df.head(50), use_container_width=True)

        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("file-text", size=14)} Applied Transformation History
        </div>
        """, unsafe_allow_html=True)
        ops = pipeline.get_operations()
        if not ops:
            st.markdown("<span style='font-size: 0.75rem; color: var(--text-muted);'>No transformations applied yet. Select operations on the left panel.</span>", unsafe_allow_html=True)
        else:
            for i, op in enumerate(ops):
                st.markdown(f"""
                <div style="padding: 8px 12px; background: var(--bg-card); border-left: 3px solid var(--accent-primary); border: 1px solid var(--border-subtle); border-left-width: 3px; margin-bottom: 6px; border-radius: 4px; font-size: 0.78rem; display: flex; justify-content: space-between; align-items: center;">
                    <span><strong style="color: var(--text-primary); font-family: var(--font-mono);">Step {i+1}:</strong> <span style="color: var(--text-secondary);">{op.get('description', op.get('operation'))}</span></span>
                    <span class="badge badge-neutral" style="font-size: 0.65rem;">{op.get('operation')}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

        # Save as New Dataset Version
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("save", size=14)} Save as New Dataset Version
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_save_version"):
            summary_text = st.text_input(
                "Change Summary",
                value=f"Applied {len(ops)} transformations (imputation, cleaning, feature scaling)" if ops else "Preprocessed dataset"
            )
            col_save1, col_save2 = st.columns([6, 4])
            with col_save1:
                st.markdown(f"<div style='padding-top: 8px; font-size: 0.82rem;'>Target Version: <code style='font-family: var(--font-mono); font-weight: 600; color: var(--accent-primary);'>v{current_ver + 1}</code> <span style='color: var(--text-muted); font-size: 0.75rem;'>(Preserves baseline v{current_ver})</span></div>", unsafe_allow_html=True)
            with col_save2:
                save_submitted = st.form_submit_button("Create New Version", type="primary", use_container_width=True)

            if save_submitted:
                if len(current_df) == 0:
                    st.error("Cannot save empty dataset.")
                else:
                    with st.spinner("Persisting new dataset version and recalculating quality profile..."):
                        new_version = DatasetManager.create_dataset_version(
                            dataset_id=selected_ds_id,
                            new_df=current_df,
                            change_summary=summary_text,
                            operations_pipeline=ops
                        )
                        st.success(f"Successfully created Dataset Version {new_version.version_number}.")
                        st.session_state["prep_pipeline"] = PreprocessingPipeline(current_df)
                        st.rerun()
