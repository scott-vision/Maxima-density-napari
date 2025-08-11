from __future__ import annotations

import argparse
from pathlib import Path

import tifffile
import napari


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
