"""
用途 | Purpose:
- 统一管理 WGT triad 相关脚本使用的物种列表、工作目录和输入数据路径。
- Centralize the species list, work directory, and input-data paths used by the WGT triad scripts.
输入 | Inputs:
- ACER_SPECIES、ACER_WGT_WORK_PATH、ACER_DATA_ROOT 及其相关环境变量。
- ACER_SPECIES, ACER_WGT_WORK_PATH, ACER_DATA_ROOT, and related environment variables.
输出 | Outputs:
- 返回规范化后的路径对象或相对路径字符串，供各步骤脚本直接调用。
- Return normalized path objects or relative-path strings that can be used directly by the step scripts.
步骤 | Steps:
1. 优先读取环境变量。 / Read environment variables first.
2. 若未提供则回退到发布目录中的默认路径。 / Fall back to the default release-directory paths when no override is provided.
3. 为各步骤脚本提供统一的路径解析接口。 / Provide a consistent path-resolution interface to the step scripts.
"""

import os
from pathlib import Path


DEFAULT_SPECIES = ["Acat", "Aneg", "Apal", "Apse", "Asac", "Atru", "Ayan", "Ddye", "Dsin"]

SCRIPT_DIR = Path(__file__).resolve().parent
RELEASE_ROOT = Path(os.environ.get("ACER_RELEASE_ROOT", SCRIPT_DIR.parent)).expanduser().resolve()


def resolve_path(env_name, default_path):
    value = os.environ.get(env_name)
    if value:
        return Path(value).expanduser().resolve()
    return Path(default_path).expanduser().resolve()


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_species_list():
    species_env = os.environ.get("ACER_SPECIES", "")
    species = [item.strip() for item in species_env.split(",") if item.strip()]
    return species or list(DEFAULT_SPECIES)


def get_wgt_work_path():
    return resolve_path("ACER_WGT_WORK_PATH", SCRIPT_DIR)


def get_data_root():
    return resolve_path("ACER_DATA_ROOT", RELEASE_ROOT)


def get_cds_dir():
    return resolve_path("ACER_CDS_DIR", get_data_root() / "01_Genome" / "cds" / "chr_only")


def get_pep_dir():
    return resolve_path("ACER_PEP_DIR", get_data_root() / "01_Genome" / "pep" / "chr_only")


def get_blast_dir():
    return resolve_path("ACER_BLAST_DIR", get_data_root() / "01_Genome" / "blastp" / "01_for_collinearity")


def get_wgdi_gff_dir():
    return resolve_path("ACER_WGDI_GFF_DIR", get_wgt_work_path() / "wgdi" / "0_gff")


def get_wgdi_lens_dir():
    return resolve_path("ACER_WGDI_LENS_DIR", get_wgt_work_path() / "wgdi" / "0_lens")


def relative_to_file(target_path, file_path):
    return os.path.relpath(
        str(Path(target_path).expanduser().resolve()),
        start=str(Path(file_path).expanduser().resolve().parent),
    )
