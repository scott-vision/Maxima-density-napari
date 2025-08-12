from __future__ import annotations

from pathlib import Path
from typing import List
import pathlib

import numpy as np
import pandas as pd
from magicgui import magic_factory
from skimage.draw import polygon2mask
from skimage.feature import peak_local_max


@magic_factory(
    call_button="Analyze",
    pixel_spacing={"min": 0.0, "value": 0.4475},
    threshold={"min": 0.0, "value": 100.0},
    min_distance={"min": 1, "value": 5},
)
def counter_widget(
    viewer: "napari.viewer.Viewer",
    hippo: "napari.layers.Image",
    hippo_rois: "napari.layers.Shapes",
    thalamus: "napari.layers.Image",
    thalamus_rois: "napari.layers.Shapes",
    output: "pathlib.Path" = Path("results.csv"),
    pixel_spacing: float = 0.4475,
    threshold: float = 100.0,
    min_distance: int = 5,
) -> "pandas.DataFrame":
    """Analyze ROIs and write results to ``output``.

    Parameters
    ----------
    viewer : napari.viewer.Viewer
        The napari viewer instance.
    hippo, thalamus : napari.layers.Image
        Three-channel images with Nuclei, GOB, GOA channels.
    hippo_rois, thalamus_rois : napari.layers.Shapes
        Polygon ROIs drawn on the corresponding images. ``hippo_rois`` should
        contain three polygons representing CA1, CA3, and DG in that order;
        ``thalamus_rois`` should contain a single polygon representing the
        thalamus.
    output : pathlib.Path
        Location where results will be written as CSV.
    pixel_spacing : float
        Microns per pixel.
    threshold : float
        Absolute intensity threshold for peak detection.
    min_distance : int
        Minimum distance between peaks.
    """

    results: List[dict] = []

    def _analyze(img_data, rois_data, region_names):
        for verts, region_name in zip(rois_data, region_names):
            mask = polygon2mask(img_data.shape[1:], verts)
            area_um2 = float(mask.sum()) * pixel_spacing ** 2
            for ch_idx, ch_name in enumerate(["GOB", "GOA"], start=1):
                channel_img = img_data[ch_idx, :, :]  # 2D slice
                coords = peak_local_max(
                    channel_img,
                    threshold_abs=threshold,
                    min_distance=min_distance,
                    labels=mask,
                )
                if coords.size:
                    viewer.add_points(
                        coords,
                        name=f"{region_name}_{ch_name}",
                        face_color="cyan" if ch_idx == 1 else "magenta",
                        size=4,
                    )
                    intensities = channel_img[coords[:, 0], coords[:, 1]]
                    mean_intensity = float(np.mean(intensities))
                else:
                    mean_intensity = 0.0
                results.append(
                    {
                        "region": region_name,
                        "channel": ch_name,
                        "count": int(len(coords)),
                        "mean_intensity": mean_intensity,
                        "area_um2": area_um2,
                        "density": float(len(coords)) / area_um2 if area_um2 else 0.0,
                    }
                )

    # Hippocampus regions CA1, CA3, DG
    hippo_names = ["CA1", "CA3", "DG"]
    # ``hippo_rois`` is expected to contain three polygons in this order.
    _analyze(hippo.data, hippo_rois.data, hippo_names)

    # Thalamus region
    _analyze(thalamus.data, thalamus_rois.data, ["Thalamus"])

    df = pd.DataFrame(results)
    df.to_csv(output, index=False)
    return df
