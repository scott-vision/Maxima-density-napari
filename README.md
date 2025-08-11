# RNAScope-counter

User interface for spot counting and intensity calculation for RNAScope analysis.

Napari interface to open 3-channel large montages, define a ROI for each section of the brain, then uses local peak detection to find spots.

The three channels should be:
- Nuclei, 488 nm, DAPI
- GOB, 560 nm, Opal 570
- GOA, 650 nm, Opal 650

Takes in the paths to 2 montage images (hippocampus and thalamus) and allows the user to select ROIs. The first image displayed is of the hippocampus and allows the user to define 3 ROIs:
- CA1
- CA3
- DG
Second montage is of the thalamus and the user defines one region (Thalamus).

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
Draw polygon ROIs on each image before pressing **Analyze**.
