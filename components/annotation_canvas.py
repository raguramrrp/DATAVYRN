import io
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Check for canvas support
CANVAS_AVAILABLE = False
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except Exception:
    CANVAS_AVAILABLE = False


def render_annotated_image(
    image_path: str,
    annotations: List[Dict[str, Any]],
    class_colors: Dict[str, str],
    target_width: int = 700
) -> Image.Image:
    """Draws bounding boxes, labels, and confidence overlays onto an image."""
    with Image.open(image_path) as im:
        orig_w, orig_h = im.size
        scale = target_width / max(orig_w, 1)
        new_h = int(orig_h * scale)

        # Work on RGB copy
        canvas_img = im.convert("RGB").resize((target_width, new_h), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas_img)

        # Draw each box
        for ann in annotations:
            x = ann.get("bbox_x", 0) * scale
            y = ann.get("bbox_y", 0) * scale
            w = ann.get("bbox_w", 0) * scale
            h = ann.get("bbox_h", 0) * scale
            label = ann.get("label_name", "Object")
            conf = ann.get("confidence")

            color_hex = class_colors.get(label, "#36D9F2")

            # Draw outer rectangle
            draw.rectangle([x, y, x + w, y + h], outline=color_hex, width=3)

            # Draw label pill
            tag_text = f"{label} ({int(conf * 100)}%)" if conf is not None else label
            tag_w = len(tag_text) * 7 + 10
            tag_h = 18

            # Tag background
            draw.rectangle([x, max(0, y - tag_h), x + tag_w, max(0, y)], fill=color_hex)
            draw.text((x + 4, max(0, y - tag_h) + 2), tag_text, fill="#090C12")

        return canvas_img
