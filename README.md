# Phenotyping and vascular characterization of Multiplex IF(CODEX)

Analysis code for the Master's thesis *Phenotyping and Vascular Characterization of Synovial Sarcoma*
(Neha Rathod, Institute of Pathology, Technical University of Munich).

The notebooks analyse multiplexed immunofluorescence images (CODEX / PhenoCycler-Fusion)
: denoising, cell segmentation, clustering and cell-type annotation,
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

1. For each sample, provide the raw image, the channel-name file and a QuPath outline of the region to analyse (GeoJSON).
2. Make a `samples.csv` with one row per sample (copy `samples_example.csv`; columns below).
3. Run 03a and 03b for all samples:

   ```bash
   python run_batch.py samples.csv --output-root path/to/output
   python run_batch.py samples.csv --output-root path/to/output --dry-run        # check the table first
   python run_batch.py samples.csv --output-root path/to/output --samples ss1    # one sample only
   ```

   Each sample gets a folder `path/to/output/<sample>/` with the results, the figures and the executed copies of
   both notebooks. A sample that fails is reported at the end and the others continue.
4. Annotate each sample in `03c_annotate.ipynb` (set `SAMPLE` and `OUTPUT_ROOT`, fill in `cluster_to_ct_dict`).
5. Run `06_vessel_segmentation.ipynb` and `07_vascular_features.ipynb` for all samples
   (set the paths in the cells marked `# <-- EDIT`).

All paths in this repository are placeholders such as `path/to/output`.

### Columns of `samples.csv`

| Column | Meaning | Example |
|---|---|---|
| `sample` | Sample ID; name of the output folder | `ss1` |
| `condition` | Lesion and histology | `primary_monophasic` |
| `region` | Region name of the CODEX run | `reg001` |
| `raw_image` | Raw OME-TIFF | `path/to/raw/ss1.ome.tif` |
| `channel_file` | Channel names, one per line (or give `--channel-file` once for all samples) | `path/to/raw/channelnames.txt` |
| `geojson` | QuPath outline of the region to analyse (required) | `path/to/qupath/ss1_region.geojson` |
| `failed_markers` | Antibodies without specific staining in this sample, comma-separated | `FOXP3,VEGFA,CD4,CD163` |
| `membrane_channels` | Membrane channel(s) for whole-cell segmentation; empty = nuclei only | `CD68` |
| `ring_markers` | Markers measured in the cytoplasm ring instead of the nucleus | `CD68,CD206` |

## Data

The images and patient data are not part of this repository.

## Acknowledgements

Segmentation, preprocessing and clustering use [SPACEc](https://github.com/yuqiyuqitan/SPACEc), [Scanpy](https://scanpy.readthedocs.io)
and Mesmer (DeepCell). The vessel segmentation is adapted from VeSpA.
