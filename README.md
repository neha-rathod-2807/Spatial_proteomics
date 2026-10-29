# Phenotyping and vascular characterization of synovial sarcoma (CODEX)

Analysis code for the Master's thesis *Phenotyping and Vascular Characterization of Synovial Sarcoma*
(Neha Rathod, Institute of Pathology, Technical University of Munich).

The notebooks analyse multiplexed immunofluorescence images (CODEX / PhenoCycler-Fusion, 28-marker panel)
of FFPE synovial sarcoma sections: denoising, cell segmentation, clustering and cell-type annotation,
vessel segmentation in the CD31 channel, and vascular features including vessel maturity.

## Pipeline

| Notebook | What it does | Main input | Main output |
|---|---|---|---|
| `03a_preprocess_segment.ipynb` | Tissue and artefact masks, background subtraction, cell segmentation (Mesmer via SPACEc), per-cell quantification, cell quality control, cell-level correction of residual background and non-specific signal (failed antibodies as internal negative controls) | Raw OME-TIFF, channel names, QuPath outline (GeoJSON) | `<sample>_cells_corrected.csv` |
| `03b_cluster.ipynb` | Filtering, z-score normalisation, noise removal and Leiden clustering (SPACEc tutorials 03.1 and 04) | Output of 03a | `<sample>_adata_clustered.h5ad` |
| `03c_annotate.ipynb` | Subclustering, cell-type annotation (interactive), composition, Ki67/HIF1A, neighbourhoods, distances | Output of 03b | `<sample>_adata_annotated.h5ad` |
| `06_vessel_segmentation.ipynb` | Vessel segmentation in the CD31 channel with two thresholds (hysteresis), removal of manually annotated artefacts, linking of cells to vessels | Raw image, outputs of 03a and 03c | Vessel tables, outlines (GeoJSON, VeSpA contour format), label images |
| `07_vascular_features.ipynb` | Vessel features (area, length density, width, distance, poorly supplied tissue, heterogeneity), cell-based features, vessel maturity from αSMA coverage, comparisons | Outputs of 06 and 03c | Feature tables and figures |

Run the notebooks in this order for every sample: **03a → 03b → 03c**, then **06** and **07** for all samples together.
03a and 03b can run unattended for all samples with `run_batch.py` (papermill), which reads one row per sample from
`samples.csv`; 03c needs manual annotation.

## Installation

Python 3.10. Create an environment and install the packages:

```bash
conda create -n spacec python=3.10
conda activate spacec
pip install -r requirements.txt
```

SPACEc (https://github.com/yuqiyuqitan/SPACEc) brings Mesmer/DeepCell for segmentation; follow its installation
instructions if the plain `pip install` fails.

## Usage

1. Set the paths in the cells marked `# <-- EDIT` (all paths in this repository are placeholders such as `path/to/output`).
2. For each sample, provide the raw image, the channel-name file and a QuPath outline of the region to analyse (GeoJSON).
3. Run 03a and 03b (by hand or with `run_batch.py`), annotate in 03c, then run 06 and 07.

## Data

The images and patient data are not part of this repository.

## Acknowledgements

Segmentation, preprocessing and clustering use [SPACEc](https://github.com/yuqiyuqitan/SPACEc), [Scanpy](https://scanpy.readthedocs.io)
and Mesmer (DeepCell). The vessel segmentation is adapted from VeSpA.
