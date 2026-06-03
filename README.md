# Acer Research Release

## Overview

This directory provides the public code release and selected example resources for Acer-related analyses. It is intended for users who want to inspect, reproduce, or extend the workflows locally.

## What Is Included

- `01_Genome/`: genome annotation utilities, GFF3 files, and identifier mapping tables.
- `02_MaxEnt/`: R scripts and PowerShell batch scripts for MaxEnt-related analyses.
- `03_WGT_triad/`: WGT/triad analysis scripts intended to be run in numeric order.
- `requirements-python-minimal.txt`: minimal Python dependency list.
- `requirements-r-maxent.txt`: R package list for the MaxEnt workflow.
- `check_dependencies.py`: dependency and environment checker.
- `install_minimal_dependencies.py`: installer for minimal Python dependencies.

## What Is Not Included

- This public release does not bundle all raw inputs, large intermediate files, third-party databases, or restricted resources.
- Users must prepare `maxent.jar`, MaxEnt input data, WGT-related external results, and any other non-distributed files on their own.

## Requirements

### Python

- Python 3.9+
- Minimal dependency list: `requirements-python-minimal.txt`

Install minimal Python dependencies:

```bash
python install_minimal_dependencies.py
```

Preview without installing:

```bash
python install_minimal_dependencies.py --dry-run
```

### R and External Tools

- Scripts in `02_MaxEnt/` depend on the R packages listed in `requirements-r-maxent.txt`.
- Some workflows also require external tools such as Java, PowerShell, MAFFT, BLAST+, MCScanX, and WGDI.

## Quick Start

### 1. Check Dependencies

```bash
python check_dependencies.py --profile all
```

Check specific workflow groups:

```bash
python check_dependencies.py --profile python
python check_dependencies.py --profile maxent
python check_dependencies.py --profile wgt
```

### 2. Prepare Your Data

- Place input files in the expected locations, or override those locations with environment variables.
- Make sure required external tools are installed and available on the command line.

### 3. Run the Analyses

Scripts in `03_WGT_triad/` are typically run in numeric order:

```bash
python 0_summarize_mcscanx_collinearity.py
python 1_extract_paralog_groups_from_mcscanx.py
python 2_select_longest_paralog_groups.py
python 3_generate_wgdi_ks_config.py
python 4_filter_paralog_groups_by_ks.py
python 5_extract_pairs_from_other_paralog_groups.py
python 6_reconstruct_paralog_groups_from_filtered_pairs.py
python 7_summarize_final_paralog_groups.py
```

Run these scripts from the `03_WGT_triad/` directory when possible.

## Common Environment Variables

Use these environment variables if your data or output locations differ from the defaults:

- MaxEnt: `MAXENT_PROJECT_ROOT`, `MAXENT_ROOT`, `MAXENT_OCC_ROOT`, `MAXENT_MAP_ROOT`, `MAXENT_RESULTS_ROOT`, `MAXENT_JAR`
- WGT: `ACER_RELEASE_ROOT`, `ACER_DATA_ROOT`, `ACER_WGT_WORK_PATH`, `ACER_CDS_DIR`, `ACER_PEP_DIR`, `ACER_BLAST_DIR`, `ACER_WGDI_GFF_DIR`, `ACER_WGDI_LENS_DIR`

Linux/macOS example:

```bash
export ACER_DATA_ROOT=/path/to/acer_release
export ACER_CDS_DIR=/path/to/acer_release/01_Genome/cds/chr_only
export ACER_PEP_DIR=/path/to/acer_release/01_Genome/pep/chr_only
```

PowerShell example:

```powershell
$env:ACER_DATA_ROOT = "D:\acer_release"
$env:ACER_CDS_DIR = "D:\acer_release\01_Genome\cds\chr_only"
$env:ACER_PEP_DIR = "D:\acer_release\01_Genome\pep\chr_only"
```

## Release Notes

- This release provides code, dependency lists, and essential usage notes for public users, but it does not automatically fetch external resources.
- If you plan to cite, reproduce, or extend the workflows, record the versions of Python, R, and external tools you used.
- For large datasets or outputs, use a long-term archive service and publish the download links separately.
