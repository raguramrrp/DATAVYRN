import streamlit as st
from typing import Optional, List, Dict, Any
from components.icons import get_svg_icon


def render_kpi_card(
    label: str,
    value: str,
    subtext: Optional[str] = None,
    icon_name: str = "activity",
    badge_variant: str = "neutral"  # 'neutral', 'success', 'warning', 'danger'
):
    """
    Renders an enterprise developer metric card matching Vercel / Linear / AWS CloudWatch standards.
    - Top row: Subtle uppercase label + monochrome 16px SVG icon
    - Middle: Crisp font-mono primary metric value
    - Bottom: Contextual sub-metric / subtle badge without neon effects
    """
    icon_svg = get_svg_icon(icon_name, size=15, stroke_width=1.75)
    
    badge_html = ""
    if subtext:
        badge_html = f'<div class="kpi-subtext"><span class="kpi-badge">{subtext}</span></div>'

    html = f"""
    <div class="kpi-card">
        <div class="kpi-top-row">
            <span class="kpi-title">{label}</span>
            <span class="kpi-icon">{icon_svg}</span>
        </div>
        <div class="kpi-value">{value}</div>
        {badge_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
