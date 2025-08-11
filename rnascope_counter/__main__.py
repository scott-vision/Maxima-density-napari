from __future__ import annotations

import argparse
from pathlib import Path

import tifffile
import napari
from napari.utils.colormaps import AVAILABLE_COLORMAPS


def main(argv: "list[str]" | None = None) -> None:
    parser = argparse.ArgumentParser(description="RNAScope spot counting in napari")
    parser.add_argument("--hippocampus", type=Path, help="Path to hippocampus image")
    parser.add_argument("--thalamus", type=Path, help="Path to thalamus image")
    args = parser.parse_args(argv)

    from .widget import counter_widget

    viewer = napari.Viewer()

    def load_image(path: Path, name: str):
    
        arr = tifffile.imread(str(path))  # shape should be (C, Y, X)
        if arr.ndim != 3:
            raise ValueError(f"{name} must have shape (channels, y, x)")
    
        cmap_list = ["gray", "cyan", "magenta"]
        return viewer.add_image(
            arr,
            name=name,
            channel_axis=0,
            colormap=[AVAILABLE_COLORMAPS[c] for c in cmap_list],
            blending="additive",
            metadata={"channel_names": ["Nuclei", "GOB", "GOA"]},
        )


    # Load images
    if args.hippocampus:
        load_image(args.hippocampus, "hippocampus")
    
    if args.thalamus:
        load_image(args.thalamus, "thalamus")

    # Auto-create ROI layers
    for roi_name in ["CA1_rois", "CA3_rois", "DG_rois", "Thalamus_rois"]:
        viewer.add_shapes(
            name=roi_name,
            shape_type="polygon",
            edge_color="yellow",
            face_color="transparent",
        )

    # Add dock widget
    viewer.window.add_dock_widget(
        counter_widget(viewer={"value": viewer, "visible": False}),
        name="RNAScope Counter",
        area="right",
    )

    napari.run()


if __name__ == "__main__":
    main()
