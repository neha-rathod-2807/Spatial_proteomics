"""Run notebooks 03a and 03b for every sample listed in samples.csv.

Each row of samples.csv is one sample. For every sample, 03a_preprocess_segment.ipynb runs first and
03b_cluster.ipynb directly after it, with the values of the row filled into the cell tagged `parameters`
(papermill). The executed notebooks are saved in the sample's output folder, so every figure and printout of the
run can be checked later. Annotation (03c) is done by hand afterwards; notebooks 06 and 07 then run on all samples.

Usage:
    python run_batch.py samples.csv --output-root path/to/output
    python run_batch.py samples.csv --output-root path/to/output --samples ss1 ss3     # only these samples
    python run_batch.py samples.csv --output-root path/to/output --steps 03b           # only clustering
    python run_batch.py samples.csv --output-root path/to/output --dry-run             # show the parameters only

Columns of samples.csv (see samples_example.csv):
    sample             sample ID, e.g. ss1 (name of the output sub-folder)
    condition          e.g. primary_monophasic, metastasis_biphasic
    region             region name of the CODEX run, e.g. reg001
    raw_image          path of the raw OME-TIFF
    channel_file       path of the channel-name file (optional if --channel-file is given)
    geojson            QuPath outline of the region to analyse (required)
    failed_markers     antibodies that did not stain in this sample, comma-separated
    membrane_channels  membrane channel(s) for whole-cell segmentation, e.g. CD68 (empty = nuclei only)
    ring_markers       markers measured in the cytoplasm ring instead of the nucleus, e.g. CD68,CD206
"""
import argparse
import csv
import sys
import time
from pathlib import Path

REQUIRED = ['sample', 'condition', 'region', 'raw_image', 'geojson']
OPTIONAL = ['channel_file', 'failed_markers', 'membrane_channels', 'ring_markers']
NOTEBOOKS = {'03a': '03a_preprocess_segment.ipynb', '03b': '03b_cluster.ipynb'}


def read_samples(path):
    """Rows of samples.csv as dictionaries; empty cells become ''."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f'{path}: no samples')
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        sys.exit(f'{path}: missing column(s) {missing}; required: {REQUIRED}')
    return [{k.strip(): (v or '').strip() for k, v in r.items() if k} for r in rows]


def parameters(step, row, args):
    """Values for the `parameters` cell of the notebook of this step."""
    if step == '03a':
        return dict(SAMPLE=row['sample'], CONDITION=row['condition'], REGION=row['region'],
                    RAW_IMAGE=row['raw_image'], CHANNEL_FILE=row.get('channel_file') or args.channel_file,
                    OUTPUT_ROOT=args.output_root, FAILED_MARKERS=row.get('failed_markers', ''),
                    MEMBRANE_CHANNELS=row.get('membrane_channels', ''), RING_MARKERS=row.get('ring_markers', ''),
                    REGION_GEOJSON=row['geojson'])
    if step == '03b':
        return dict(SAMPLE=row['sample'], OUTPUT_ROOT=args.output_root, REGION_GEOJSON='',   # '' = outline of 03a
                    PIXEL_SIZE_UM=args.pixel_size)
    raise ValueError(step)


def check(row, args):
    """Problems that would stop 03a (missing files or values)."""
    problems = []
    for col in ('raw_image', 'geojson'):
        if not row.get(col):
            problems.append(f'{col} is empty')
        elif not Path(row[col]).exists():
            problems.append(f'{col} not found: {row[col]}')
    channel_file = row.get('channel_file') or args.channel_file
    if not channel_file:
        problems.append('no channel file (column channel_file or --channel-file)')
    elif not Path(channel_file).exists():
        problems.append(f'channel file not found: {channel_file}')
    return problems


def main():
    ap = argparse.ArgumentParser(description='Run 03a and 03b for every sample in samples.csv (papermill).')
    ap.add_argument('samples_csv', help='table with one row per sample (see samples_example.csv)')
    ap.add_argument('--output-root', required=True, help='output folder; one sub-folder per sample is created')
    ap.add_argument('--notebooks', default=str(Path(__file__).parent / 'notebooks'), help='folder with the notebooks')
    ap.add_argument('--channel-file', default='', help='channel-name file for samples without a channel_file value')
    ap.add_argument('--pixel-size', type=float, default=0.5, help='µm per pixel (default 0.5)')
    ap.add_argument('--samples', nargs='*', help='only these sample IDs (default: all rows)')
    ap.add_argument('--steps', nargs='*', default=['03a', '03b'], choices=list(NOTEBOOKS), help='steps to run')
    ap.add_argument('--kernel', default='spacec', help='Jupyter kernel of the analysis environment')
    ap.add_argument('--dry-run', action='store_true', help='print the parameters and checks, run nothing')
    args = ap.parse_args()

    rows = read_samples(args.samples_csv)
    if args.samples:
        unknown = set(args.samples) - {r['sample'] for r in rows}
        if unknown:
            sys.exit(f'not in {args.samples_csv}: {sorted(unknown)}')
        rows = [r for r in rows if r['sample'] in args.samples]
    steps = [s for s in NOTEBOOKS if s in args.steps]                 # always in the order 03a -> 03b
    nb_dir = Path(args.notebooks)

    if not args.dry_run:
        import papermill as pm                                          # imported here so --dry-run needs nothing

    failed = []
    for i, row in enumerate(rows, 1):
        s = row['sample']
        print(f'\n[{i}/{len(rows)}] {s} ({row["condition"]})', flush=True)
        if '03a' in steps:
            problems = check(row, args)
            if problems:
                failed.append((s, '03a', '; '.join(problems)))
                if not args.dry_run:
                    print('   skipped: ' + '; '.join(problems), flush=True)
                    continue
                print('   would be skipped: ' + '; '.join(problems), flush=True)
        out_dir = Path(args.output_root) / s
        for step in steps:
            params = parameters(step, row, args)
            executed = out_dir / f'{s}_{NOTEBOOKS[step]}'                # executed copy with all outputs
            if args.dry_run:
                print(f'   {step}: {NOTEBOOKS[step]} -> {executed}')
                for k, v in params.items():
                    print(f'      {k} = {v!r}')
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            t0 = time.time()
            print(f'   {step}: running {NOTEBOOKS[step]} ...', flush=True)
            try:
                pm.execute_notebook(str(nb_dir / NOTEBOOKS[step]), str(executed), parameters=params,
                                    kernel_name=args.kernel, cwd=str(nb_dir), progress_bar=False)
                print(f'   {step}: done in {(time.time() - t0) / 60:.1f} min; executed notebook: {executed}', flush=True)
            except Exception as e:                                       # keep going with the next sample
                print(f'   {step}: FAILED ({type(e).__name__}); see {executed}', flush=True)
                failed.append((s, step, type(e).__name__))
                break                                                    # 03b needs the output of 03a

    print('\n' + '=' * 60)
    print(f'{len(rows) - len({f[0] for f in failed})} of {len(rows)} samples completed')
    for s, step, why in failed:
        print(f'   {s}: {step} - {why}')
    print('next: annotate each sample in 03c_annotate.ipynb')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
