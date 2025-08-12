from __future__ import annotations

from pathlib import Path
from typing import List
import pathlib
import json
import logging

import numpy as np
import pandas as pd
from magicgui import magic_factory
from skimage import io, exposure
from skimage.draw import polygon2mask
from skimage.feature import peak_local_max


@magic_factory(
    call_button="Analyze",
    pixel_spacing={"min": 0.0, "value": 0.4475},
    threshold={"min": 0.0, "value": 100.0},
    min_distance={"min": 1, "value": 5},
    output_dir={"mode": "d"},
    c1={"choices": ["DAPI", "GOB", "GOA"], "label": "Channel 1"},
    c2={"choices": ["DAPI", "GOB", "GOA"], "label": "Channel 2"},
    c3={"choices": ["DAPI", "GOB", "GOA"], "label": "Channel 3"},
)
def counter_widget(
    viewer: "napari.viewer.Viewer",
    hippo: "napari.layers.Image",
    hippo_rois: "napari.layers.Shapes",
    thalamus: "napari.layers.Image",
    thalamus_rois: "napari.layers.Shapes",
    output_dir: "pathlib.Path" = Path("results"),
    pixel_spacing: float = 0.4475,
    threshold: float = 100.0,
    min_distance: int = 5,
    c1: str = "DAPI",
    c2: str = "GOB",
    c3: str = "GOA",
) -> "pandas.DataFrame":
    """Analyze ROIs and write results to ``output_dir``.

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
    output_dir : pathlib.Path
        Directory where results and associated files will be written.
    pixel_spacing : float
        Microns per pixel.
    threshold : float
        Absolute intensity threshold for peak detection.
    min_distance : int
        Minimum distance between peaks.
    c1, c2, c3 : str
        Labels for the three image channels. Defaults are DAPI, GOB, GOA.
    """

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    logger.info(
        "Starting analysis with output_dir=%s, pixel_spacing=%s, threshold=%s, min_distance=%s",
        output_dir,
        pixel_spacing,
        threshold,
        min_distance,
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "pixel_spacing": pixel_spacing,
        "threshold": threshold,
        "min_distance": min_distance,
    }
    with (output_dir / "params.json").open("w") as f:
        json.dump(params, f, indent=2)

    results: List[dict] = []

    channel_labels = [c1, c2, c3]
    gob_idx = channel_labels.index("GOB")
    goa_idx = channel_labels.index("GOA")

    def _analyze(img_data, rois_data, region_names):
        for verts, region_name in zip(rois_data, region_names):
            logger.info("Analyzing region %s", region_name)
            np.save(output_dir / f"{region_name}_roi.npy", verts)
            mask = polygon2mask(img_data.shape[1:], verts)
            area_um2 = float(mask.sum()) * pixel_spacing ** 2
            ys, xs = np.where(mask)
            minr, maxr = ys.min(), ys.max() + 1
            minc, maxc = xs.min(), xs.max() + 1
            for ch_idx, ch_name in [(gob_idx, "GOB"), (goa_idx, "GOA")]:
                channel_img = img_data[ch_idx, :, :]
                coords = peak_local_max(
                    channel_img,
                    threshold_abs=threshold,
                    min_distance=min_distance,
                    labels=mask,
                )

                channel_masked = np.where(mask, channel_img, 0)
                cutout = channel_masked[minr:maxr, minc:maxc]
                cutout = exposure.rescale_intensity(cutout, out_range=(0, 255)).astype(
                    np.uint8
                )
                io.imsave(
                    output_dir / f"{region_name}_{ch_name}.png",
                    cutout,
                    check_contrast=False,
                )

                annotated = cutout.copy()
                for r, c in coords:
                    r -= minr
                    c -= minc
                    rr_start, rr_end = max(r - 1, 0), min(r + 2, annotated.shape[0])
                    cc_start, cc_end = max(c - 1, 0), min(c + 2, annotated.shape[1])
                    annotated[rr_start:rr_end, c] = 255
                    annotated[r, cc_start:cc_end] = 255
                io.imsave(
                    output_dir / f"{region_name}_{ch_name}_spots.png",
                    annotated,
                    check_contrast=False,
                )

                if coords.size:
                    viewer.add_points(
                        coords,
                        name=f"{region_name}_{ch_name}",
                        face_color="cyan" if ch_name == "GOB" else "magenta",
                        size=4,
                    )
                    intensities = channel_img[coords[:, 0], coords[:, 1]]
                    mean_intensity = float(np.mean(intensities))
                else:
                    mean_intensity = 0.0
                logger.info(
                    "\t%s: found %d spots", ch_name, len(coords)
                )
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
    df.to_csv(output_dir / "results.csv", index=False)
    logger.info("Analysis complete. Results written to %s", output_dir)
    return df
