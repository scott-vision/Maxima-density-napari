from __future__ import annotations

import argparse
from pathlib import Path

import tifffile
import napari
from napari.utils.notifications import show_info


def main(argv: "list[str]" | None = None) -> None:
    parser = argparse.ArgumentParser(description="RNAScope spot counting in napari")
    parser.add_argument("--hippocampus", type=Path, help="Path to hippocampus image")
    parser.add_argument("--thalamus", type=Path, help="Path to thalamus image")
    args = parser.parse_args(argv)

    from .widget import counter_widget

    viewer = napari.Viewer()

    def load_image(path: Path, name: str):
    
        arr = tifffile.imread(str(path))  # expected shape (C, Y, X)
        if arr.ndim != 3:
            raise ValueError(f"{name} must have shape (channels, y, x)")

        layer = viewer.add_image(
            arr,
            name=name,
            colormap="gray",
            metadata={"channel_names": ["Nuclei", "GOB", "GOA"]},
        )
        # Ensure the first axis is labeled as channels so a slider appears.
        viewer.dims.axis_labels = ["channel", "y", "x"]
        return layer


    # Load images
    hippo_layer = None
    thalamus_layer = None
    if args.hippocampus:
        hippo_layer = load_image(args.hippocampus, "hippocampus")

    if args.thalamus:
        thalamus_layer = load_image(args.thalamus, "thalamus")

    # Auto-create ROI layers
    # ``hippo_rois`` is expected to contain three polygons corresponding to
    # hippocampal regions CA1, CA3, and DG in that order. ``thalamus_rois``
    # should contain a single polygon covering the thalamus.
    hippo_rois = viewer.add_shapes(
        name="hippo_rois",
        shape_type="polygon",
        edge_color="yellow",
        face_color="transparent",
    )
    thalamus_rois = viewer.add_shapes(
        name="thalamus_rois",
        shape_type="polygon",
        edge_color="yellow",
        face_color="transparent",
    )

    # Start with thalamus hidden so user focuses on hippocampus
    if thalamus_layer is not None:
        thalamus_layer.visible = False
        thalamus_rois.visible = False

    show_info("Draw polygon around CA1 in hippo_rois")

    def _on_hippo_roi_change(event):
        n = len(hippo_rois.data)
        if n == 1:
            show_info("Draw polygon around CA3")
        elif n == 2:
            show_info("Draw polygon around DG")
        elif n == 3:
            show_info("Draw polygon around the thalamus")
            if hippo_layer is not None:
                hippo_layer.visible = False
            hippo_rois.visible = False
            if thalamus_layer is not None:
                thalamus_layer.visible = True
                thalamus_rois.visible = True
            hippo_rois.events.data.disconnect(_on_hippo_roi_change)

    hippo_rois.events.data.connect(_on_hippo_roi_change)

    # Add dock widget
    viewer.window.add_dock_widget(
        counter_widget(viewer={"value": viewer, "visible": False}),
        name="RNAScope Counter",
        area="right",
    )

    napari.run()


if __name__ == "__main__":
    main()
