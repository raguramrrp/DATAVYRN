import streamlit as st
import json
from pathlib import Path
from PIL import Image

# Streamlit 1.40+ backward compatibility patch for streamlit_drawable_canvas
try:
    import streamlit.elements.image as st_image
    import streamlit.elements.lib.image_utils as image_utils
    if not hasattr(st_image, "image_to_url"):
        st_image.image_to_url = image_utils.image_to_url
except Exception:
    pass

import config
from core.database import get_db_session
from core.models import Dataset, ImageItem, Annotation, AnnotationClass
from core.dataset_manager import DatasetManager
from core.annotation_engine import AnnotationEngine
from components.annotation_canvas import render_annotated_image
from components.icons import get_svg_icon

try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_READY = True
except Exception:
    CANVAS_READY = False


def render(project_id: str):
    """Renders the comprehensive Image Annotation Studio with interactive bounding boxes and multi-format export."""
    st.markdown(f"""
    <div class="card-header-clean" style="margin-bottom: 20px;">
        <div>
            <div class="card-title-clean">Annotation Studio — Computer Vision Workspace</div>
            <div class="card-subtitle-clean">Interactive bounding box annotation, class hierarchy management, and standard vision format exports</div>
        </div>
        <span class="badge badge-accent">Interactive Canvas</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Fetch available image datasets
    datasets = DatasetManager.list_datasets(project_id=project_id, dataset_type="image")
    if not datasets:
        st.markdown(f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">{get_svg_icon("image", size=24)}</div>
            <div class="empty-state-title">No Image Datasets Available</div>
            <div class="empty-state-desc">Upload or import an image dataset in the Datasets module to start annotating with bounding boxes.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    col_ds, col_exp = st.columns([7, 3])
    with col_ds:
        ds_map = {d["id"]: f"{d['name']} ({d['image_count']} images)" for d in datasets}
        current_ds_id = st.session_state.get("selected_dataset_id")
        if current_ds_id not in ds_map:
            current_ds_id = datasets[0]["id"]

        selected_ds_id = st.selectbox(
            "Active Image Dataset",
            options=list(ds_map.keys()),
            format_func=lambda x: ds_map.get(x, x),
            key="studio_dataset_select"
        )
        st.session_state["selected_dataset_id"] = selected_ds_id

    # Export trigger popover
    with col_exp:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        with st.popover("Export Annotations", use_container_width=True):
            st.markdown("##### Export Dataset Annotations")
            export_fmt = st.selectbox("Select Format", ["COCO JSON", "YOLO TXT", "Pascal VOC XML"])
            if st.button("Generate & Download Export", type="primary", use_container_width=True):
                with st.spinner(f"Exporting in {export_fmt}..."):
                    if export_fmt == "COCO JSON":
                        res = AnnotationEngine.export_coco(selected_ds_id)
                        with open(res["file_path"], "r") as f:
                            st.download_button(
                                "Download COCO JSON",
                                data=f.read(),
                                file_name=f"{selected_ds_id}_coco.json",
                                mime="application/json"
                            )
                    elif export_fmt == "YOLO TXT":
                        res = AnnotationEngine.export_yolo(selected_ds_id)
                        st.success(f"Exported {res['annotations_count']} boxes to {res['dir_path']}")
                    elif export_fmt == "Pascal VOC XML":
                        res = AnnotationEngine.export_voc(selected_ds_id)
                        st.success(f"Exported {res['annotations_count']} VOC XML files to {res['dir_path']}")

    # 2. Classes and Colors for this dataset
    classes_list = AnnotationEngine.get_classes(selected_ds_id)
    if not classes_list:
        AnnotationEngine.add_class(selected_ds_id, "Object", "#2563eb")
        classes_list = AnnotationEngine.get_classes(selected_ds_id)

    class_names = [c["name"] for c in classes_list]
    class_colors = {c["name"]: c["color_hex"] for c in classes_list}

    # -------------------------------------------------------------
    # Studio Workspace Layout (3-Column Architecture)
    # Left: Image Queue (2.5) | Center: Canvas & Controls (6) | Right: Class Manager & Box Props (3.5)
    # -------------------------------------------------------------
    col_queue, col_canvas, col_props = st.columns([2.5, 6.0, 3.5])

    # -------------------------------------------------------------
    # LEFT PANEL: IMAGE QUEUE & FILTERS
    # -------------------------------------------------------------
    with col_queue:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("folder", size=14)} Image Queue
        </div>
        """, unsafe_allow_html=True)
        status_filter = st.selectbox(
            "Filter Status",
            ["all", "pending", "in_progress", "completed", "needs_review"],
            format_func=lambda x: x.replace("_", " ").title(),
            key="studio_status_filter"
        )
        search_q = st.text_input("Search filename", "", placeholder="e.g. sample_01", key="studio_search")

        images = AnnotationEngine.get_images(selected_ds_id, status_filter=status_filter, search_query=search_q)

        if not images:
            st.markdown(f"""
            <div style="padding: 16px; border: 1px dashed var(--border-subtle); border-radius: 6px; text-align: center; color: var(--text-muted); font-size: 0.78rem;">
                No matching images in queue.
            </div>
            """, unsafe_allow_html=True)
            return

        # Maintain selected image ID in state
        if "selected_image_id" not in st.session_state or not any(img["id"] == st.session_state["selected_image_id"] for img in images):
            st.session_state["selected_image_id"] = images[0]["id"]

        current_img_idx = next(i for i, img in enumerate(images) if img["id"] == st.session_state["selected_image_id"])
        selected_img = images[current_img_idx]

        st.markdown(f"<div style='font-size: 0.72rem; color: var(--text-muted); margin-bottom: 8px; font-family: var(--font-mono);'>{len(images)} images in queue</div>", unsafe_allow_html=True)

        # Image list items
        for i, img in enumerate(images[:15]):  # show first 15 for responsiveness
            is_active = (img["id"] == selected_img["id"])
            status_badge_class = "badge-success" if img["status"] == "completed" else ("badge-warning" if img["status"] == "needs_review" else "badge-neutral")

            col_thumb_btn, col_thumb_text = st.columns([3, 7])
            with col_thumb_btn:
                try:
                    with Image.open(img["file_path"]) as pil_im:
                        pil_im.thumbnail((60, 60))
                        st.image(pil_im)
                except Exception:
                    st.markdown(f"<div style='display:flex; align-items:center; justify-content:center; width:50px; height:50px; background:var(--bg-card); border-radius:4px;'>{get_svg_icon('image', size=18)}</div>", unsafe_allow_html=True)

            with col_thumb_text:
                btn_type = "primary" if is_active else "secondary"
                if st.button(img["filename"], key=f"q_img_{img['id']}", type=btn_type, use_container_width=True):
                    st.session_state["selected_image_id"] = img["id"]
                    st.rerun()
                st.markdown(f"<span class='badge {status_badge_class}' style='font-size: 0.65rem;'>{img['status'].replace('_', ' ').upper()}</span> <span style='font-size: 0.68rem; color: var(--text-muted); font-family: var(--font-mono);'>({img['annotation_count']} boxes)</span>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # CENTER PANEL: LARGE ANNOTATION CANVAS
    # -------------------------------------------------------------
    with col_canvas:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("crosshair", size=14)} Canvas: <code style="font-family: var(--font-mono); color: var(--text-primary);">{selected_img['filename']}</code>
        </div>
        """, unsafe_allow_html=True)

        # Current annotations for selected image
        existing_anns = AnnotationEngine.get_annotations_for_image(selected_img["id"])

        # Display tools
        col_tool1, col_tool2, col_tool3 = st.columns([4, 4, 4])
        with col_tool1:
            active_class = st.selectbox("Active Drawing Class", class_names, key="studio_active_class")
        with col_tool2:
            stroke_color = class_colors.get(active_class, "#2563eb")
            st.markdown(f"<div style='margin-top: 28px; display: flex; align-items: center; gap: 8px;'><span style='display:inline-block; width:14px; height:14px; background:{stroke_color}; border-radius:3px;'></span><span style='font-size:0.75rem; color:var(--text-secondary);'>Active Color</span></div>", unsafe_allow_html=True)
        with col_tool3:
            stroke_width = st.slider("Stroke Width", 1, 6, 2, key="studio_stroke_w")

        # Load background image
        bg_image = Image.open(selected_img["file_path"])
        orig_w, orig_h = bg_image.size
        canvas_width = 620
        scale_factor = canvas_width / max(orig_w, 1)
        canvas_height = int(orig_h * scale_factor)

        # Interactive Canvas Drawing or Visualizer
        new_drawn_boxes = []
        canvas_success = False

        if CANVAS_READY:
            try:
                canvas_result = st_canvas(
                    fill_color="rgba(37, 99, 235, 0.12)",
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_image=bg_image.resize((canvas_width, canvas_height)),
                    update_streamlit=True,
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode="rect",
                    key=f"canvas_{selected_img['id']}",
                )
                canvas_success = True

                # Parse newly drawn objects from canvas
                if canvas_result is not None and canvas_result.json_data is not None:
                    objects = canvas_result.json_data.get("objects", [])
                    for obj in objects:
                        if obj.get("type") == "rect":
                            c_left = float(obj.get("left", 0))
                            c_top = float(obj.get("top", 0))
                            c_w = float(obj.get("width", 0)) * float(obj.get("scaleX", 1))
                            c_h = float(obj.get("height", 0)) * float(obj.get("scaleY", 1))

                            real_x = c_left / scale_factor
                            real_y = c_top / scale_factor
                            real_w = c_w / scale_factor
                            real_h = c_h / scale_factor

                            new_drawn_boxes.append({
                                "label_name": active_class,
                                "bbox_x": real_x,
                                "bbox_y": real_y,
                                "bbox_w": real_w,
                                "bbox_h": real_h,
                                "confidence": 1.0,
                                "annotation_source": "manual"
                            })
            except Exception:
                canvas_success = False

        if not canvas_success:
            rendered = render_annotated_image(selected_img["file_path"], existing_anns, class_colors, target_width=canvas_width)
            st.image(rendered, use_container_width=True)

        # ---------------------------------------------------------
        # BOTTOM CONTROLS & NAVIGATION
        # ---------------------------------------------------------
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_prev, col_save, col_next = st.columns([3, 4, 3])

        with col_prev:
            if st.button("Previous Image", use_container_width=True):
                prev_idx = (current_img_idx - 1) % len(images)
                st.session_state["selected_image_id"] = images[prev_idx]["id"]
                st.rerun()

        with col_save:
            if st.button("Save Annotations", type="primary", use_container_width=True):
                boxes_to_save = new_drawn_boxes if new_drawn_boxes else existing_anns
                res = AnnotationEngine.save_image_annotations(
                    selected_img["id"],
                    boxes_to_save,
                    mark_status="in_progress" if len(boxes_to_save) > 0 else "pending"
                )
                st.success(f"Saved {res['saved_count']} annotations.")
                st.rerun()

        with col_next:
            if st.button("Next Image", use_container_width=True):
                next_idx = (current_img_idx + 1) % len(images)
                st.session_state["selected_image_id"] = images[next_idx]["id"]
                st.rerun()

    # -------------------------------------------------------------
    # RIGHT PANEL: CLASS MANAGER & SELECTED BOX PROPERTIES
    # -------------------------------------------------------------
    with col_props:
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("tag", size=14)} Object Classes
        </div>
        """, unsafe_allow_html=True)
        for c in classes_list:
            c_name = c["name"]
            c_color = c["color_hex"]
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 10px; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:6px; margin-bottom:6px;">
                <span style="font-size:0.78rem; color:var(--text-primary); font-weight:500;">{c_name}</span>
                <span style="width:12px; height:12px; background:{c_color}; border-radius:3px;"></span>
            </div>
            """, unsafe_allow_html=True)

        with st.popover("Add New Class"):
            new_c_name = st.text_input("Class Name", placeholder="e.g. Helmet, Crack")
            new_c_color = st.color_picker("Class Color", "#2563eb")
            if st.button("Create Class", use_container_width=True):
                if new_c_name:
                    AnnotationEngine.add_class(selected_ds_id, new_c_name.strip(), new_c_color)
                    st.rerun()

        st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

        # Bounding Box Coordinate Editor
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("box", size=14)} Bounding Boxes ({len(existing_anns)})
        </div>
        """, unsafe_allow_html=True)
        if not existing_anns:
            st.markdown("<span style='font-size: 0.74rem; color: var(--text-muted);'>No bounding boxes recorded. Draw on canvas or add manually.</span>", unsafe_allow_html=True)
        else:
            for idx, box in enumerate(existing_anns):
                with st.expander(f"Box {idx+1}: {box['label_name']} ({int(box['bbox_w'])}x{int(box['bbox_h'])})", expanded=False):
                    c_box1, c_box2 = st.columns(2)
                    with c_box1:
                        new_lbl = st.selectbox(f"Class #{idx+1}", class_names, index=class_names.index(box["label_name"]) if box["label_name"] in class_names else 0, key=f"edit_lbl_{box['id']}")
                        new_x = st.number_input(f"X #{idx+1}", value=float(box["bbox_x"]), key=f"edit_x_{box['id']}")
                        new_w = st.number_input(f"Width #{idx+1}", value=float(box["bbox_w"]), key=f"edit_w_{box['id']}")
                    with c_box2:
                        new_conf = st.slider(f"Confidence #{idx+1}", 0.0, 1.0, float(box.get("confidence") or 1.0), key=f"edit_conf_{box['id']}")
                        new_y = st.number_input(f"Y #{idx+1}", value=float(box["bbox_y"]), key=f"edit_y_{box['id']}")
                        new_h = st.number_input(f"Height #{idx+1}", value=float(box["bbox_h"]), key=f"edit_h_{box['id']}")

                    if st.button(f"Update Box {idx+1}", key=f"update_box_btn_{box['id']}"):
                        existing_anns[idx]["label_name"] = new_lbl
                        existing_anns[idx]["bbox_x"] = new_x
                        existing_anns[idx]["bbox_y"] = new_y
                        existing_anns[idx]["bbox_w"] = new_w
                        existing_anns[idx]["bbox_h"] = new_h
                        existing_anns[idx]["confidence"] = new_conf
                        AnnotationEngine.save_image_annotations(selected_img["id"], existing_anns)
                        st.rerun()

                    if st.button(f"Delete Box {idx+1}", key=f"del_box_btn_{box['id']}"):
                        updated_list = [b for b in existing_anns if b["id"] != box["id"]]
                        AnnotationEngine.save_image_annotations(selected_img["id"], updated_list)
                        st.rerun()

        # Add Manual Bounding Box
        with st.popover("Add Box Manually"):
            man_lbl = st.selectbox("Label", class_names, key="man_box_lbl")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                man_x = st.number_input("X coordinate", min_value=0, max_value=orig_w, value=50)
                man_w = st.number_input("Box Width", min_value=5, max_value=orig_w, value=120)
            with c_m2:
                man_y = st.number_input("Y coordinate", min_value=0, max_value=orig_h, value=50)
                man_h = st.number_input("Box Height", min_value=5, max_value=orig_h, value=100)

            if st.button("Add Box", type="primary", use_container_width=True):
                existing_anns.append({
                    "label_name": man_lbl,
                    "bbox_x": man_x,
                    "bbox_y": man_y,
                    "bbox_w": man_w,
                    "bbox_h": man_h,
                    "confidence": 1.0,
                    "annotation_source": "manual"
                })
                AnnotationEngine.save_image_annotations(selected_img["id"], existing_anns)
                st.rerun()

        st.markdown("<hr style='border-color: var(--border-subtle); margin: 16px 0;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # QA / REVIEW WORKFLOW CONTROLS
        # ---------------------------------------------------------
        st.markdown(f"""
        <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            {get_svg_icon("shield", size=14)} Quality Review Workflow
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.75rem; margin-bottom: 8px;'>Current Status: <span class='badge badge-neutral font-mono'>{selected_img['status'].replace('_', ' ').upper()}</span></div>", unsafe_allow_html=True)
        if selected_img.get("rejection_reason"):
            st.error(f"Rejection Note: {selected_img['rejection_reason']}")

        col_rv1, col_rv2 = st.columns(2)
        with col_rv1:
            if st.button("Approve", use_container_width=True):
                AnnotationEngine.review_annotation(selected_img["id"], status="approved", reviewer="Lead Reviewer", comment="Approved bounding boxes")
                st.success("Task marked Approved & Completed.")
                st.rerun()
        with col_rv2:
            with st.popover("Reject"):
                rej_reason = st.text_input("Reason for Rejection", placeholder="e.g., Loose bounds, missing label")
                if st.button("Confirm Rejection", type="primary", use_container_width=True):
                    AnnotationEngine.review_annotation(selected_img["id"], status="rejected", rejection_reason=rej_reason, reviewer="Lead Reviewer")
                    st.warning("Task marked Needs Review.")
                    st.rerun()
