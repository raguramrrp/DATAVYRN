import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

import config
from core.database import get_db_session
from core.models import Dataset, DatasetVersion, ImageItem
from core.dataset_manager import DatasetManager
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the comprehensive Dataset Management, Profiling, and Quality Assessment Studio."""
    st.markdown("""
    <div class="card-header-clean">
        <div class="card-title-clean">Dataset Intelligence & Ingestion Hub</div>
        <span class="card-action-badge">Version Controlled</span>
    </div>
    """, unsafe_allow_html=True)

    tab_explore, tab_import, tab_versions = st.tabs(["Explorer & Profiler", "Import Dataset", "Version History & Diff"])

    # -----------------------------------------------------------------
    # TAB 1: DATASET EXPLORER & PROFILER
    # -----------------------------------------------------------------
    with tab_explore:
        datasets = DatasetManager.list_datasets(project_id=project_id)

        if not datasets:
            empty_svg = get_svg_icon("database", size=24)
            st.markdown(f"""
            <div class="empty-state-card">
                <div class="empty-state-icon">{empty_svg}</div>
                <div class="empty-state-title">No Datasets Found</div>
                <div class="empty-state-desc">Import tabular (CSV, XLSX, JSON) or image sets to begin profiling and model training.</div>
            </div>
            """, unsafe_allow_html=True)
            return

        dataset_options = {d["id"]: f"{d['name']} ({d['dataset_type'].upper()} • v{d['current_version']})" for d in datasets}

        selected_ds_id = st.selectbox(
            "SELECT DATASET TO INSPECT",
            options=list(dataset_options.keys()),
            format_func=lambda x: dataset_options.get(x, x),
            key="datasets_selected_ds"
        )
        st.session_state["selected_dataset_id"] = selected_ds_id

        selected_ds = next(d for d in datasets if d["id"] == selected_ds_id)

        # Overview Metadata Cards
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi_card("TYPE", selected_ds["dataset_type"].upper(), selected_ds["original_filename"][:18], "database")
        with c2:
            count_label = "RECORDS" if selected_ds["dataset_type"] == "tabular" else "IMAGES"
            count_val = selected_ds["record_count"] if selected_ds["dataset_type"] == "tabular" else selected_ds["image_count"]
            render_kpi_card(count_label, str(count_val), f"v{selected_ds['current_version']}", "layers")
        with c3:
            features_label = "FEATURES" if selected_ds["dataset_type"] == "tabular" else "FORMATS"
            feat_val = str(selected_ds["feature_count"]) if selected_ds["dataset_type"] == "tabular" else "JPG/PNG"
            render_kpi_card(features_label, feat_val, "Dimensions", "box")
        with c4:
            size_mb = round(selected_ds["file_size_bytes"] / (1024 * 1024), 2)
            render_kpi_card("FILE SIZE", f"{size_mb} MB", "Local Storage", "server")
        with c5:
            q_score = selected_ds["quality_score"]
            render_kpi_card("QUALITY SCORE", f"{q_score}/100", "Audited Health", "shield")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # Tabular Dataset Details
        # -------------------------------------------------------------
        if selected_ds["dataset_type"] == "tabular":
            df, current_ver = DatasetManager.load_tabular_dataframe(selected_ds_id)

            st.markdown(f"##### Data Preview (Version {current_ver} — First 100 Rows)")
            st.dataframe(df.head(100), use_container_width=True)

            col_prof, col_qual = st.columns([6, 4])

            with col_prof:
                st.markdown("##### Feature Profiling & Distribution")
                quality_rep = selected_ds.get("quality_report", {})
                profiling = quality_rep.get("profiling", {})
                cols_meta = profiling.get("columns", [])

                if cols_meta:
                    prof_df = pd.DataFrame(cols_meta)
                    display_cols = [c for c in ["column", "dtype", "missing_count", "missing_pct", "unique_count", "mean", "std", "min", "max", "skew"] if c in prof_df.columns]
                    st.dataframe(prof_df[display_cols], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df.describe().T, use_container_width=True)

            with col_qual:
                st.markdown("##### Explainable Quality Assessment")
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.8125rem; font-weight: 600; color: #0f172a;">AUDITED SCORE</span>
                        <span class="badge badge-neutral">{q_score} / 100.0</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #475569; margin-top: 6px; line-height: 1.4;">
                        Deductions evaluated: Missing cell ratio, duplicate rows, constant zero-variance features, statistical outlier presence, and target imbalance.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                deductions = quality_rep.get("deductions", [])
                if deductions:
                    d_df = pd.DataFrame(deductions)
                    st.table(d_df[["rule", "finding", "deduction"]])
                else:
                    st.success("No quality penalties identified. Dataset passed all validation checks.")

                # Quick action buttons
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Prepare & Clean Data ↗", use_container_width=True, type="primary"):
                        st.session_state["selected_dataset_id"] = selected_ds_id
                        st.session_state["active_page"] = "data_preparation"
                        st.rerun()
                with col_b2:
                    if st.button("Train Model ↗", use_container_width=True):
                        st.session_state["selected_dataset_id"] = selected_ds_id
                        st.session_state["active_page"] = "training_lab"
                        st.rerun()

        # -------------------------------------------------------------
        # Image Dataset Details
        # -------------------------------------------------------------
        elif selected_ds["dataset_type"] == "image":
            with get_db_session() as session:
                images = session.query(ImageItem).filter(ImageItem.dataset_id == selected_ds_id).all()
                total_imgs = len(images)
                annotated_imgs = sum(1 for img in images if len(img.annotations) > 0)
                corrupt_imgs = sum(1 for img in images if img.is_corrupted)
                total_boxes = sum(len(img.annotations) for img in images)

            col_img_stat, col_img_act = st.columns([7, 3])
            with col_img_stat:
                st.markdown("##### Image Set Profiling")
                stat_df = pd.DataFrame([
                    {"Metric": "Total Images", "Value": str(total_imgs)},
                    {"Metric": "Annotated Images", "Value": str(annotated_imgs)},
                    {"Metric": "Unannotated / Pending", "Value": str(total_imgs - annotated_imgs)},
                    {"Metric": "Total Bounding Boxes", "Value": str(total_boxes)},
                    {"Metric": "Corrupted Files", "Value": str(corrupt_imgs)},
                ])
                st.table(stat_df)

            with col_img_act:
                st.markdown("##### Annotation Studio")
                st.markdown("Open this image dataset directly in the Annotation Studio to inspect, draw bounding boxes, or export.")
                if st.button("Open in Annotation Studio ↗", type="primary", use_container_width=True):
                    st.session_state["selected_dataset_id"] = selected_ds_id
                    st.session_state["active_page"] = "annotation_studio"
                    st.rerun()

    # -----------------------------------------------------------------
    # TAB 2: IMPORT NEW DATASET
    # -----------------------------------------------------------------
    with tab_import:
        st.markdown("##### Import Dataset into Project")
        import_type = st.radio("INGESTION FORMAT", ["Tabular (CSV, XLSX, JSON)", "Image Dataset (JPG, PNG, WEBP)"], horizontal=True)

        if "Tabular" in import_type:
            with st.form("form_import_tabular", clear_on_submit=False):
                dataset_name = st.text_input("Dataset Name *", placeholder="e.g. Customer Churn Analysis")
                dataset_desc = st.text_area("Description", placeholder="Describe features, domain, source...")
                uploaded_file = st.file_uploader("Upload CSV, XLSX, or JSON File", type=["csv", "xlsx", "xls", "json"])
                submitted = st.form_submit_button("Ingest & Profile Tabular Dataset", type="primary")

                if submitted:
                    if not dataset_name or not uploaded_file:
                        st.error("Please provide a dataset name and select a valid file.")
                    else:
                        with st.spinner("Parsing file, calculating statistics, and generating quality report..."):
                            try:
                                ds = DatasetManager.import_tabular_file(
                                    project_id=project_id,
                                    file_path_or_buffer=uploaded_file,
                                    filename=uploaded_file.name,
                                    name=dataset_name,
                                    description=dataset_desc
                                )
                                st.success(f"Dataset '{ds.name}' imported successfully! Quality Score: {ds.quality_score}/100")
                                st.session_state["selected_dataset_id"] = ds.id
                                st.rerun()
                            except Exception as e:
                                st.error(f"Import failed: {str(e)}")

        else:
            with st.form("form_import_images", clear_on_submit=False):
                dataset_name = st.text_input("Image Dataset Name *", placeholder="e.g. Drone Solar Panel Inspection")
                dataset_desc = st.text_area("Description", placeholder="Image resolution, camera angle, target objects...")
                classes_input = st.text_input("Object Class Labels (comma-separated)", "Defect, Component, Surface_Crack")
                uploaded_images = st.file_uploader("Upload Image Files (Select Multiple)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
                submitted_img = st.form_submit_button("Ingest Image Dataset", type="primary")

                if submitted_img:
                    if not dataset_name or not uploaded_images:
                        st.error("Please provide a dataset name and select at least one image file.")
                    else:
                        with st.spinner(f"Ingesting {len(uploaded_images)} images and verifying integrity..."):
                            try:
                                classes = [c.strip() for c in classes_input.split(",") if c.strip()]
                                files_data = [(f.name, f.getvalue()) for f in uploaded_images]
                                ds = DatasetManager.import_image_files(
                                    project_id=project_id,
                                    files_data=files_data,
                                    name=dataset_name,
                                    description=dataset_desc,
                                    initial_classes=classes
                                )
                                st.success(f"Image dataset '{ds.name}' imported with {ds.image_count} images!")
                                st.session_state["selected_dataset_id"] = ds.id
                                st.session_state["active_page"] = "annotation_studio"
                                st.rerun()
                            except Exception as e:
                                st.error(f"Import failed: {str(e)}")

    # -----------------------------------------------------------------
    # TAB 3: VERSION HISTORY & DIFF
    # -----------------------------------------------------------------
    with tab_versions:
        st.markdown("##### Dataset Version Lineage")
        if not datasets:
            st.info("No datasets to trace.")
            return

        with get_db_session() as session:
            ds = session.query(Dataset).filter(Dataset.id == st.session_state.get("selected_dataset_id", datasets[0]["id"])).first()
            if not ds:
                return
            versions = ds.versions

        st.markdown(f"**Tracking Lineage for:** `{ds.name}` ({len(versions)} Versions Saved)")

        ver_records = []
        for v in versions:
            ver_records.append({
                "Version": f"v{v.version_number}",
                "Records": v.record_count,
                "Features": v.feature_count,
                "Summary of Changes": v.change_summary,
                "Timestamp": v.created_at.strftime("%Y-%m-%d %H:%M:%S") if v.created_at else "N/A"
            })

        st.dataframe(pd.DataFrame(ver_records), use_container_width=True, hide_index=True)

        if len(versions) >= 2:
            st.markdown("##### Compare Versions (Diff)")
            c_v1, c_v2 = st.columns(2)
            v_nums = [v.version_number for v in versions]
            with c_v1:
                base_ver = st.selectbox("Base Version", v_nums, index=0)
            with c_v2:
                comp_ver = st.selectbox("Comparison Version", v_nums, index=len(v_nums)-1)

            if base_ver != comp_ver and ds.dataset_type == "tabular":
                df_base, _ = DatasetManager.load_tabular_dataframe(ds.id, base_ver)
                df_comp, _ = DatasetManager.load_tabular_dataframe(ds.id, comp_ver)

                row_diff = len(df_comp) - len(df_base)
                col_diff = len(df_comp.columns) - len(df_base.columns)

                st.markdown(f"""
                - **Row Delta:** `{row_diff:+d}` ({len(df_base)} → {len(df_comp)})
                - **Column Delta:** `{col_diff:+d}` ({len(df_base.columns)} → {len(df_comp.columns)})
                - **Added Columns:** `{set(df_comp.columns) - set(df_base.columns) or 'None'}`
                - **Removed Columns:** `{set(df_base.columns) - set(df_comp.columns) or 'None'}`
                """)
