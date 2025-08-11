from __future__ import annotations

import argparse
from pathlib import Path




def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="RNAScope spot counting in napari")
    parser.add_argument("--hippocampus", type=Path, help="Path to hippocampus image")
    parser.add_argument("--thalamus", type=Path, help="Path to thalamus image")
    parser.add_argument("--max-projected", action="store_true", help="Images are already max projected")
    args = parser.parse_args(argv)
    import napari

    from .widget import counter_widget
    viewer = napari.Viewer()
    if args.hippocampus:
        viewer.open(str(args.hippocampus), channel_axis=0, name="hippocampus")
    if args.thalamus:
        viewer.open(str(args.thalamus), channel_axis=0, name="thalamus")

    viewer.window.add_dock_widget(
        counter_widget(viewer={"value": viewer, "visible": False}),
        name="RNAScope Counter",
        area="right",
    )
    napari.run()


if __name__ == "__main__":
    main()
