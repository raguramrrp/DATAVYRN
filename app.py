import streamlit as st
from pathlib import Path

# Streamlit 1.40+ backward compatibility patch for streamlit_drawable_canvas
try:
    import streamlit.elements.image as st_image
    import streamlit.elements.lib.image_utils as image_utils
    if not hasattr(st_image, "image_to_url"):
        st_image.image_to_url = image_utils.image_to_url
except Exception:
    pass

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="DATAVYRN — Data Intelligence & Training Workbench",
    page_icon="DV",
    layout="wide",
    initial_sidebar_state="expanded"
)

import config
from core.database import init_db, get_db_session
from core.models import Project
from core.demo_data import initialize_demo_workspace
from components.navigation import render_sidebar
from components.header import render_header

# Import all page views
from pages_app import (
    overview,
    datasets,
    annotation_studio,
    data_preparation,
    training_lab,
    evaluation,
    error_analysis,
    experiments,
    reports,
    settings
)


def load_custom_css():
    """Injects custom enterprise developer styling (Pure Light Theme)."""
    css_path = config.CSS_DIR / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_code = f.read()
            st.markdown(f"<style>{css_code}</style>", unsafe_allow_html=True)


def ensure_initialized():
    """Ensures database tables exist and seeds demo data on first launch."""
    init_db()
    with get_db_session() as session:
        has_proj = session.query(Project).first()
        if not has_proj:
            initialize_demo_workspace()


def main():
    # 1. Apply global enterprise styles
    load_custom_css()

    # 2. Guarantee demo state exists
    ensure_initialized()

    # 3. Render left navigation sidebar
    active_page, selected_proj_id = render_sidebar()

    # 4. Render top enterprise header bar with breadcrumb
    page_title_display = active_page.replace("_", " ").title()
    render_header(page_title_display, selected_proj_id)

    # 5. Route to active page module
    if active_page == "overview":
        overview.render(selected_proj_id)
    elif active_page == "datasets":
        datasets.render(selected_proj_id)
    elif active_page == "annotation_studio":
        annotation_studio.render(selected_proj_id)
    elif active_page == "data_preparation":
        data_preparation.render(selected_proj_id)
    elif active_page == "training_lab":
        training_lab.render(selected_proj_id)
    elif active_page == "evaluation":
        evaluation.render(selected_proj_id)
    elif active_page == "error_analysis":
        error_analysis.render(selected_proj_id)
    elif active_page == "experiments":
        experiments.render(selected_proj_id)
    elif active_page == "reports":
        reports.render(selected_proj_id)
    elif active_page == "settings":
        settings.render(selected_proj_id)
    else:
        overview.render(selected_proj_id)


if __name__ == "__main__":
    main()
