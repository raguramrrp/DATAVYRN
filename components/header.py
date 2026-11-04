import streamlit as st
from typing import Optional
from core.database import get_db_session
from core.models import Project
from components.icons import get_svg_icon


def render_header(current_page: str, project_id: Optional[str] = None):
    """
    Renders the top enterprise header bar with breadcrumb navigation and workspace telemetry.
    Pure Light Theme — clean, high-contrast, free of unnecessary toggles.
    """
    with get_db_session() as session:
        projects = session.query(Project).all()
        active_proj = session.query(Project).filter(Project.id == project_id).first() if project_id else (projects[0] if projects else None)
        proj_name = active_proj.name if active_proj else "Default Workspace"

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0;">
        <div class="breadcrumb-nav">
            <span class="breadcrumb-root">DATAVYRN</span>
            <span class="breadcrumb-divider">/</span>
            <span class="breadcrumb-project">{proj_name}</span>
            <span class="breadcrumb-divider">/</span>
            <span class="breadcrumb-current">{current_page}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span class="badge badge-neutral" style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; padding: 3px 8px;">
                <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#10b981;"></span>
                Online
            </span>
            <span class="badge badge-neutral font-mono" style="font-size: 0.72rem; padding: 3px 8px;">v2.0 Local</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
