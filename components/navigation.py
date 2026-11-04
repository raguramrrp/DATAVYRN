import streamlit as st
from typing import Tuple, List, Optional
from core.database import get_db_session
from core.models import Project
from components.icons import get_svg_icon


NAV_ITEMS = [
    ("overview", "Overview", "layout-dashboard"),
    ("datasets", "Datasets", "database"),
    ("annotation_studio", "Annotation Studio", "crosshair"),
    ("data_preparation", "Data Preparation", "sliders"),
    ("training_lab", "Training Lab", "cpu"),
    ("evaluation", "Model Evaluation", "line-chart"),
    ("error_analysis", "Error Analysis", "alert-triangle"),
    ("experiments", "Experiments", "git-compare"),
    ("reports", "Reports", "file-text"),
    ("settings", "Settings", "settings"),
]


def render_sidebar() -> Tuple[str, str]:
    """
    Renders the production-grade enterprise sidebar matching Linear / Vercel developer standards:
    - Compact geometric brand badge
    - Clean project selector
    - Clean menu list with SVG icons & zero circular radio bullets
    - Low-profile status footer component
    """
    with st.sidebar:
        # 1. Compact Header / Branding
        st.markdown("""
        <div class="sidebar-branding">
            <div class="brand-badge">DV</div>
            <div>
                <div class="brand-title">DATAVYRN</div>
                <div class="brand-subtitle">Data Intelligence Platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Enterprise Project Selector
        with get_db_session() as session:
            projects = session.query(Project).filter(Project.is_active == True).all()
            if not projects:
                proj_options = {"proj_alpha": "Project Alpha: Workbench"}
            else:
                proj_options = {p.id: p.name for p in projects}

        current_proj_id = st.session_state.get("selected_project_id", list(proj_options.keys())[0])
        if current_proj_id not in proj_options:
            current_proj_id = list(proj_options.keys())[0]

        selected_proj_id = st.selectbox(
            "PROJECT WORKSPACE",
            options=list(proj_options.keys()),
            format_func=lambda x: proj_options.get(x, x),
            key="nav_project_select",
            label_visibility="visible"
        )
        st.session_state["selected_project_id"] = selected_proj_id

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 3. Clean Module Navigation
        if "active_page" not in st.session_state:
            st.session_state["active_page"] = "overview"

        keys = [item[0] for item in NAV_ITEMS]
        labels = [item[1] for item in NAV_ITEMS]

        current_idx = keys.index(st.session_state["active_page"]) if st.session_state["active_page"] in keys else 0

        selected_label = st.radio(
            "MODULES",
            options=labels,
            index=current_idx,
            label_visibility="collapsed"
        )

        selected_key = keys[labels.index(selected_label)]
        st.session_state["active_page"] = selected_key

        # 4. Compact Runtime Status Footer
        st.markdown("""
        <div class="sidebar-footer">
            <div class="sidebar-footer-row">
                <span class="sidebar-footer-label">Engine</span>
                <span class="sidebar-footer-val" style="display:inline-flex; align-items:center; gap:4px;">
                    <span style="display:inline-block; width:5px; height:5px; border-radius:50%; background:#10b981;"></span>
                    Active
                </span>
            </div>
            <div class="sidebar-footer-row">
                <span class="sidebar-footer-label">Database</span>
                <span class="sidebar-footer-val">SQLite 3.x</span>
            </div>
            <div class="sidebar-footer-row">
                <span class="sidebar-footer-label">Runtime</span>
                <span class="sidebar-footer-val">Local CPU</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        return selected_key, selected_proj_id
