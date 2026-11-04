import os
import shutil
import streamlit as st
import pandas as pd

import config
from core.database import get_db_session
from core.models import Project, Dataset, Experiment, ImageItem, Annotation
from core.demo_data import reset_demo_workspace
from components.metric_cards import render_kpi_card
from components.icons import get_svg_icon


def render(project_id: str):
    """Renders the System Settings, Project Manager, and Workspace Diagnostics."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">System Settings & Workspace Administration</div>
            <div class="card-subtitle-clean">Workspace provisioning, disk storage footprint diagnostics, and offline runtime telemetry</div>
        </div>
        <span class="badge badge-accent">Diagnostics</span>
    </div>
    """, unsafe_allow_html=True)

    tab_proj, tab_storage, tab_reset = st.tabs(["Projects & Workspaces", "Storage & Runtime Diagnostics", "Reset Workspace"])

    # -------------------------------------------------------------
    # TAB 1: PROJECTS & WORKSPACES
    # -------------------------------------------------------------
    with tab_proj:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("folder", size=14)} Active Workspace Projects
        </div>
        """, unsafe_allow_html=True)
        with get_db_session() as session:
            projects = session.query(Project).all()
            proj_data = [p.to_dict() for p in projects]

        st.dataframe(pd.DataFrame(proj_data), use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("plus", size=14)} Provision New Project
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_create_project"):
            new_p_name = st.text_input("Project Name *", placeholder="e.g. Autonomous Vision QA")
            new_p_desc = st.text_area("Description", placeholder="Project goals, dataset links...")
            create_submitted = st.form_submit_button("Create Project", type="primary")

            if create_submitted:
                if not new_p_name:
                    st.error("Project name is required.")
                else:
                    import uuid
                    with get_db_session() as session:
                        p_id = f"proj_{uuid.uuid4().hex[:8]}"
                        p = Project(id=p_id, name=new_p_name, description=new_p_desc, is_active=True)
                        session.add(p)
                        session.commit()
                    st.success(f"Project '{new_p_name}' created.")
                    st.session_state["selected_project_id"] = p_id
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 2: STORAGE & RUNTIME DIAGNOSTICS
    # -------------------------------------------------------------
    with tab_storage:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("server", size=14)} Local Storage Footprint
        </div>
        """, unsafe_allow_html=True)

        def get_dir_size(path):
            total = 0
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):
                            total += os.path.getsize(fp)
            return total

        db_size_kb = round(os.path.getsize(config.DB_PATH) / 1024, 2) if os.path.exists(config.DB_PATH) else 0
        ds_size_mb = round(get_dir_size(config.DATASETS_DIR) / (1024 * 1024), 2)
        img_size_mb = round(get_dir_size(config.IMAGES_DIR) / (1024 * 1024), 2)
        mod_size_mb = round(get_dir_size(config.MODELS_DIR) / (1024 * 1024), 2)
        rep_size_mb = round(get_dir_size(config.REPORTS_DIR) / (1024 * 1024), 2)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("SQLite Database", f"{db_size_kb} KB", "storage/database", icon_name="server", badge_variant="neutral")
        with c2:
            render_kpi_card("Dataset Files", f"{ds_size_mb} MB", "storage/datasets", icon_name="database", badge_variant="neutral")
        with c3:
            render_kpi_card("Image Cache", f"{img_size_mb} MB", "storage/images", icon_name="image", badge_variant="neutral")
        with c4:
            render_kpi_card("Trained Models", f"{mod_size_mb} MB", "storage/models", icon_name="cpu", badge_variant="neutral")

        st.markdown("<hr style='border-color: var(--border-subtle); margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("shield", size=14)} Offline & Security Compliance
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        - **Air-Gapped Operation:** DATAVYRN executes 100% locally on your machine without external cloud API dependencies.
        - **Data Privacy:** Your uploaded datasets, images, annotations, and trained models never leave this workstation.
        - **Storage Isolation:** All artifacts reside in the designated local `storage/` directory.
        """)

    # -------------------------------------------------------------
    # TAB 3: RESET DEMO WORKSPACE
    # -------------------------------------------------------------
    with tab_reset:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("alert-triangle", size=14)} Reset Demo Workspace
        </div>
        """, unsafe_allow_html=True)
        st.warning(
            "This action wipes all existing datasets, models, annotations, and experiments, and reinitializes "
            "the clean default demo workspace (Scikit-Learn Wine Recognition dataset, 3 baseline models, and synthetic inspection images)."
        )

        with st.form("form_reset_demo"):
            confirm_check = st.checkbox("I understand that this will erase current workspace data and reload the demo state.")
            reset_btn = st.form_submit_button("Wipe & Reload Demo Workspace", type="primary")

            if reset_btn:
                if not confirm_check:
                    st.error("Please check the confirmation box to proceed.")
                else:
                    with st.spinner("Purging tables, rebuilding schema, and generating pristine demo workspace..."):
                        reset_demo_workspace()
                        st.success("Demo workspace restored successfully.")
                        st.session_state["active_page"] = "overview"
                        st.session_state["selected_project_id"] = "proj_alpha"
                        st.rerun()
