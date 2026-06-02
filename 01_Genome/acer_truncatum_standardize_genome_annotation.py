"""
用途 | Purpose:
- 说明 Acer truncatum（Atru）基因组注释标准化所需的输入、输出与使用提示。
- Describe the inputs, outputs, and usage notes for Acer truncatum (Atru) genome-annotation standardization.
输入 | Inputs:
- 原始 GFF3、genome FASTA、CDS FASTA、pep FASTA 应位于 inputs 目录，或位于 GENOME_DATA_ROOT 指定的目录中。
- The original GFF3, genome FASTA, CDS FASTA, and peptide FASTA should be placed in the inputs directory or in a directory specified by GENOME_DATA_ROOT.
输出 | Outputs:
- 输出文件与本目录其他物种脚本保持一致，包括标准化 GFF3、genome、CDS、pep 以及 ID 映射表。
- Output files follow the same structure as the other species scripts in this directory, including standardized GFF3, genome, CDS, peptide files, and ID mapping tables.
使用提示 | Usage Notes:
1. 运行前确认输入根目录及所需原始文件名称无误。 / Before running, confirm the input root and required raw filenames.
2. 处理结果应包含标准化序列文件与对应的 ID 映射表。 / The results should include standardized sequence files and the corresponding ID mapping tables.
3. 可通过 GENOME_DATA_ROOT 环境变量指定自定义输入目录。 / You can set a custom input directory with the GENOME_DATA_ROOT environment variable.
"""

import os
from pathlib import Path

# Resolve input paths / 解析输入路径
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ["GENOME_DATA_ROOT"]).expanduser() if os.environ.get("GENOME_DATA_ROOT") else SCRIPT_DIR / "inputs"


def resolve_input_path(*parts):
    return str((DATA_ROOT.joinpath(*parts)).resolve())

