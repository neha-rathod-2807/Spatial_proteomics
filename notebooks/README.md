# Notebooks

Run the notebooks in this order:

| Step | Notebook | What it does |
|---|---|---|
| 1 | `03a_preprocess_segment.ipynb` | Masks, background subtraction, cell segmentation (Mesmer), cell QC, correction of non-specific signal |
| 2 | `03b_cluster.ipynb` | Filtering, z-score normalisation, noise removal, Leiden clustering |
| 3 | `03c_annotate.ipynb` | Subclustering and cell-type annotation (interactive), composition and spatial analyses |
| 4 | `06_vessel_segmentation.ipynb` | Vessel segmentation in the CD31 channel, artefact removal, linking cells to vessels |
| 5 | `07_vascular_features.ipynb` | Vessel features, cell-based features and vessel maturity (αSMA coverage) |

Steps 1–3 are run for every sample; steps 4 and 5 for all samples together.
Set the paths in the cells marked `# <-- EDIT` before running.
