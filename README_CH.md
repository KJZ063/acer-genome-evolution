# Acer-genome-evolution release

## 简介

本目录提供与相关研究分析配套的公开代码与部分示例数据，面向需要查看、复现或在本地继续分析的用户。

## 内容概览

- `01_Genome/`：基因组注释整理脚本、GFF3 文件和编号对应表。
- `02_MaxEnt/`：MaxEnt 相关 R 脚本与 PowerShell 批处理脚本。
- `03_WGT_triad/`：WGT/triad 分析脚本，按编号顺序执行。
- `requirements-python-minimal.txt`：最小 Python 依赖清单。
- `requirements-r-maxent.txt`：MaxEnt 工作流所需 R 包清单。
- `check_dependencies.py`：依赖与关键环境配置检查工具。
- `install_minimal_dependencies.py`：最小 Python 依赖安装工具。

## 不包含的内容

- 公开版本不随附全部原始输入数据、大体积中间结果、第三方数据库或受许可限制的资源。
- 用户需要自行准备 `maxent.jar`、MaxEnt 输入数据、WGT 所需外部结果，以及其他未随仓库发布的文件。
- 为保持发布包简洁且适合公开传播，投稿往来文件、回复信和稿件草稿等非代码材料不包含在本次公开版本中。

## 环境要求

### Python

- Python 3.9+
- 最小依赖清单：`requirements-python-minimal.txt`

安装最小 Python 依赖：

```bash
python install_minimal_dependencies.py
```

仅查看安装命令：

```bash
python install_minimal_dependencies.py --dry-run
```

### R 和外部工具

- `02_MaxEnt/` 脚本依赖 `requirements-r-maxent.txt` 中列出的 R 包。
- 部分流程还需要外部工具，例如 Java、PowerShell、MAFFT、BLAST+、MCScanX 和 WGDI。

## 快速开始

### 1. 检查依赖

```bash
python check_dependencies.py --profile all
```

按模块检查：

```bash
python check_dependencies.py --profile python
python check_dependencies.py --profile maxent
python check_dependencies.py --profile wgt
```

### 2. 准备数据

- 将输入数据放入脚本默认查找的位置，或通过环境变量覆盖默认路径。
- 确保外部工具已安装并可在命令行中直接调用。

### 3. 运行分析

`03_WGT_triad/` 中的脚本通常按编号顺序运行：

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

建议在 `03_WGT_triad/` 目录中执行这些脚本。

## 常用环境变量

如果数据或结果文件不在默认位置，可按需设置以下环境变量：

- MaxEnt: `MAXENT_PROJECT_ROOT`, `MAXENT_ROOT`, `MAXENT_OCC_ROOT`, `MAXENT_MAP_ROOT`, `MAXENT_RESULTS_ROOT`, `MAXENT_JAR`
- WGT: `ACER_RELEASE_ROOT`, `ACER_DATA_ROOT`, `ACER_WGT_WORK_PATH`, `ACER_CDS_DIR`, `ACER_PEP_DIR`, `ACER_BLAST_DIR`, `ACER_WGDI_GFF_DIR`, `ACER_WGDI_LENS_DIR`

Linux/macOS 示例：

```bash
export ACER_DATA_ROOT=/path/to/acer_release
export ACER_CDS_DIR=/path/to/acer_release/01_Genome/cds/chr_only
export ACER_PEP_DIR=/path/to/acer_release/01_Genome/pep/chr_only
```

PowerShell 示例：

```powershell
$env:ACER_DATA_ROOT = "D:\acer_release"
$env:ACER_CDS_DIR = "D:\acer_release\01_Genome\cds\chr_only"
$env:ACER_PEP_DIR = "D:\acer_release\01_Genome\pep\chr_only"
```

## 发布说明

- 本仓库面向公开使用者提供代码、依赖清单和必要说明，不承诺自动下载外部资源。
- 如果你计划引用、复现或继续开发，建议记录所使用的 Python、R 和外部工具版本。
- 如需共享大体积数据或结果，建议使用长期存档平台并在发布页面中提供链接。
