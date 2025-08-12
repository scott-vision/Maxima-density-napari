# RNAScope-counter

User interface for spot counting and intensity calculation for RNAScope analysis.

Napari interface to open 3-channel large montages, define a ROI for each section of the brain, then uses local peak detection to find spots.

The three channels should be:
- Nuclei, 488 nm, DAPI
- GOB, 560 nm, Opal 570
- GOA, 650 nm, Opal 650

Takes in the paths to 2 montage images (hippocampus and thalamus) and allows the user to select ROIs. The application creates two empty shapes layers named ``hippo_rois`` and ``thalamus_rois``. When the viewer launches, it guides ROI creation: the thalamus layers are hidden and you are prompted to draw polygons on the hippocampus in this order:
- CA1
- CA3
- DG
After the three hippocampal regions are outlined, the viewer hides the hippocampus layers, reveals the thalamus, and prompts you to draw a single polygon representing the thalamus in ``thalamus_rois``.

Then provides analysis of each region defined, including:
- Number of spots in GOA/GOB channel
- Intensity of spots
- Average spot intensity
- Spots per square micron

Output is saved to CSV file.

## Usage

```bash
python -m rnascope_counter --hippocampus path/to/hippo.tif --thalamus path/to/thalamus.tif
```

After launching, use the docked *RNAScope Counter* widget to enter the pixel spacing (default `0.4475` µm/pixel), choose the output CSV location, and adjust the `threshold` and `min_distance` parameters that control spot detection.
Draw polygon ROIs on each image before pressing **Analyze**. In ``hippo_rois`` add three polygons in the order CA1, CA3, DG; ``thalamus_rois`` should contain one polygon for the thalamus.
