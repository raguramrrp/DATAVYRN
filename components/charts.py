import streamlit as st
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def get_light_theme_layout() -> Dict[str, Any]:
    """Generates standard enterprise Plotly layout parameters for a crisp, high-contrast light theme."""
    return dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Inter', 'Geist', 'Segoe UI', Roboto, sans-serif",
            color="#475569",
            size=12
        ),
        margin=dict(l=35, r=25, t=38, b=35),
        xaxis=dict(
            gridcolor="#f1f5f9",
            zerolinecolor="#e2e8f0",
            linecolor="#e2e8f0",
            tickfont=dict(color="#64748b", size=11)
        ),
        yaxis=dict(
            gridcolor="#f1f5f9",
            zerolinecolor="#e2e8f0",
            linecolor="#e2e8f0",
            tickfont=dict(color="#64748b", size=11)
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(color="#0f172a", size=11)
        ),
        title_font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Inter', 'Geist', 'Segoe UI', Roboto, sans-serif",
            color="#0f172a",
            size=13
        )
    )


def plot_confusion_matrix(cm_list: List[List[int]], class_names: Optional[List[str]] = None) -> go.Figure:
    """Renders a clean, high-contrast heatmap for confusion matrix evaluation."""
    cm = np.array(cm_list)
    labels = class_names if class_names and len(class_names) == len(cm) else [f"Class {i}" for i in range(len(cm))]

    annotations = []
    for i in range(len(cm)):
        for j in range(len(cm[0])):
            val = int(cm[i, j])
            text_color = "#ffffff" if val > (cm.max() * 0.55) else "#0f172a"
            annotations.append(dict(
                x=labels[j],
                y=labels[i],
                text=str(val),
                font=dict(color=text_color, size=13, family="ui-monospace, 'JetBrains Mono', monospace"),
                showarrow=False
            ))

    colorscale = [[0.0, "#eff6ff"], [0.45, "#93c5fd"], [1.0, "#1d4ed8"]]

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels,
        y=labels,
        colorscale=colorscale,
        showscale=False
    ))

    layout = get_light_theme_layout()
    layout.update(
        title=dict(text="Confusion Matrix (Validation)", font=layout["title_font"]),
        xaxis=dict(
            title=dict(text="Predicted Label", font=dict(size=11, color="#475569")),
            gridcolor=layout["xaxis"]["gridcolor"],
            tickfont=layout["xaxis"]["tickfont"]
        ),
        yaxis=dict(
            title=dict(text="Actual Ground Truth", font=dict(size=11, color="#475569")),
            gridcolor=layout["yaxis"]["gridcolor"],
            autorange="reversed",
            tickfont=layout["yaxis"]["tickfont"]
        ),
        annotations=annotations,
        height=320
    )
    fig.update_layout(layout)
    return fig


def plot_roc_curves(curves: List[Dict[str, Any]]) -> go.Figure:
    """Renders multi-class or binary ROC curves with smooth, crisp strokes."""
    layout = get_light_theme_layout()
    fig = go.Figure()

    # Diagonal random baseline
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        line=dict(color="#cbd5e1", dash="dash", width=1.2),
        name="Baseline (AUC = 0.50)"
    ))

    palette = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#db2777", "#0891b2"]

    for idx, c in enumerate(curves):
        color = palette[idx % len(palette)]
        auc_val = c.get("auc", 0.0)
        cname = c.get("class_name", f"Class {idx}")
        fig.add_trace(go.Scatter(
            x=c.get("fpr", []),
            y=c.get("tpr", []),
            mode="lines",
            line=dict(color=color, width=1.75),
            name=f"{cname} (AUC {auc_val:.3f})"
        ))

    layout.update(
        title=dict(text="ROC Curves (Multi-Class OvR)", font=layout["title_font"]),
        xaxis=dict(title=dict(text="False Positive Rate", font=dict(size=11, color="#475569")), range=[-0.01, 1.01]),
        yaxis=dict(title=dict(text="True Positive Rate", font=dict(size=11, color="#475569")), range=[-0.01, 1.03]),
        height=320
    )
    fig.update_layout(layout)
    return fig


def plot_feature_importance(importance_dict: Dict[str, float], top_n: int = 10) -> go.Figure:
    """Renders a ranked horizontal bar chart for feature importances."""
    layout = get_light_theme_layout()
    sorted_items = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features = [item[0] for item in reversed(sorted_items)]
    scores = [item[1] for item in reversed(sorted_items)]

    fig = go.Figure(data=go.Bar(
        x=scores,
        y=features,
        orientation="h",
        marker=dict(
            color="#2563eb",
            line=dict(width=0)
        )
    ))

    layout.update(
        title=dict(text=f"Feature Importances (Top {len(features)})", font=layout["title_font"]),
        xaxis=dict(title=dict(text="Relative Score", font=dict(size=11, color="#475569"))),
        yaxis=dict(title=""),
        height=320
    )
    fig.update_layout(layout)
    return fig


def plot_actual_vs_predicted(y_true: List[float], y_pred: List[float]) -> go.Figure:
    """Scatter plot of actual versus predicted values for regression."""
    layout = get_light_theme_layout()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=y_true,
        y=y_pred,
        mode="markers",
        marker=dict(color="#2563eb", size=6, opacity=0.8),
        name="Observations"
    ))

    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode="lines",
        line=dict(color="#059669", dash="dash", width=1.5),
        name="1:1 Parity"
    ))

    layout.update(
        title=dict(text="Actual vs. Predicted", font=layout["title_font"]),
        xaxis=dict(title=dict(text="Actual Value", font=dict(size=11, color="#475569"))),
        yaxis=dict(title=dict(text="Predicted Value", font=dict(size=11, color="#475569"))),
        height=320
    )
    fig.update_layout(layout)
    return fig


def plot_residuals_distribution(residuals: List[float]) -> go.Figure:
    """Distribution histogram of regression residuals."""
    layout = get_light_theme_layout()
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=residuals,
        nbinsx=24,
        marker=dict(color="#2563eb"),
        opacity=0.85
    ))

    layout.update(
        title=dict(text="Residuals Distribution", font=layout["title_font"]),
        xaxis=dict(title=dict(text="Residual (y_true - y_pred)", font=dict(size=11, color="#475569"))),
        yaxis=dict(title=dict(text="Count", font=dict(size=11, color="#475569"))),
        height=320
    )
    fig.update_layout(layout)
    return fig


def plot_task_distribution(status_counts: Dict[str, int]) -> go.Figure:
    """Refined light theme donut chart for annotation task statuses."""
    layout = get_light_theme_layout()
    color_map = {
        "completed": "#059669",
        "in_progress": "#2563eb",
        "needs_review": "#d97706",
        "pending": "#94a3b8"
    }

    labels = [k.replace("_", " ").title() for k in status_counts.keys()]
    values = list(status_counts.values())
    colors_list = [color_map.get(k.lower(), "#2563eb") for k in status_counts.keys()]

    fig = go.Figure(data=go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        marker=dict(colors=colors_list, line=dict(color="#ffffff", width=2)),
        textinfo="label+value",
        textfont=dict(size=11, family=layout["font"]["family"], color="#0f172a")
    ))

    layout.update(
        title=dict(text="Annotation Queue Status", font=layout["title_font"]),
        height=280,
        showlegend=False
    )
    fig.update_layout(layout)
    return fig


def plot_quality_trend(trend_records: List[Dict[str, Any]]) -> go.Figure:
    """Line chart of quality review scores over time."""
    layout = get_light_theme_layout()
    dates = [r.get("date", f"T-{i}") for i, r in enumerate(trend_records)]
    scores = [r.get("score", 100.0) for r in trend_records]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=scores,
        mode="lines+markers",
        line=dict(color="#2563eb", width=2),
        marker=dict(size=6, color="#059669"),
        name="Review Agreement"
    ))

    layout.update(
        title=dict(text="Annotation Review Agreement Trend", font=layout["title_font"]),
        xaxis=dict(title=dict(text="Review Batch", font=dict(size=11, color="#475569"))),
        yaxis=dict(title=dict(text="Agreement Rate (%)", font=dict(size=11, color="#475569")), range=[60, 105]),
        height=280
    )
    fig.update_layout(layout)
    return fig
