from __future__ import annotations

import os
import shutil
from pathlib import Path


RELEASE_ROOT = Path(__file__).resolve().parent
PYTHON_REQUIREMENTS_FILE = RELEASE_ROOT / "requirements-python-minimal.txt"
R_REQUIREMENTS_FILE = RELEASE_ROOT / "requirements-r-maxent.txt"
MIN_PYTHON_VERSION = (3, 9)

PROFILE_LABELS = {
    "python": "Python 基础脚本",
    "maxent": "02_MaxEnt 工作流",
    "wgt": "03_WGT_triad 工作流",
    "all": "全部检查项",
}

TOOL_DISPLAY_NAMES = {
    "rscript": "R / Rscript",
    "powershell": "PowerShell",
    "java": "Java",
    "mafft": "MAFFT",
    "blastp": "BLASTP",
    "makeblastdb": "makeblastdb",
    "mcscanx": "MCScanX",
    "wgdi": "WGDI CLI",
}

COMMAND_CANDIDATES = {
    "rscript": ["Rscript", "Rscript.exe", "R", "R.exe"],
    "powershell": ["pwsh", "pwsh.exe", "powershell", "powershell.exe"],
    "java": ["java", "java.exe"],
    "mafft": ["mafft", "mafft.bat", "mafft.exe"],
    "blastp": ["blastp", "blastp.exe"],
    "makeblastdb": ["makeblastdb", "makeblastdb.exe"],
    "mcscanx": ["MCScanX", "MCScanX.exe", "mcscanx", "mcscanx.exe"],
    "wgdi": ["wgdi", "wgdi.exe"],
}

PROFILE_EXTERNAL_TOOLS = {
    "python": [],
    "maxent": ["powershell", "java"],
    "wgt": ["mafft", "blastp", "makeblastdb", "mcscanx", "wgdi"],
}

TOOL_INSTALL_HINTS = {
    "rscript": "请先安装 R，并确保 `Rscript` 或 `R` 已加入 PATH。",
    "powershell": "Windows 通常自带 `powershell`；跨平台环境建议安装 `pwsh` 并加入 PATH。",
    "java": "请安装可用的 Java Runtime/JDK，并确保 `java` 在 PATH 中。",
    "mafft": "请安装 MAFFT，并将可执行文件加入 PATH。",
    "blastp": "请安装 NCBI BLAST+，并将 `blastp` 加入 PATH。",
    "makeblastdb": "请安装 NCBI BLAST+，并将 `makeblastdb` 加入 PATH。",
    "mcscanx": "请单独安装或编译 MCScanX，并将其可执行文件加入 PATH。",
    "wgdi": "请安装 WGDI，并确认命令行入口 `wgdi` 可直接调用。",
}


def resolve_env_path(env_name: str, default_path: Path) -> Path:
    value = os.environ.get(env_name)
    if value:
        return Path(value).expanduser().resolve()
    return Path(default_path).expanduser().resolve()


def get_maxent_project_root_default() -> Path:
    return RELEASE_ROOT.parent.resolve()


def get_maxent_root_default() -> Path:
    return resolve_env_path("MAXENT_ROOT", get_maxent_project_root_default() / "data" / "maxent")


def get_maxent_occ_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_OCC_ROOT",
        get_maxent_project_root_default() / "data" / "occurrence" / "for_maxent",
    )


def get_maxent_map_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_MAP_ROOT",
        get_maxent_root_default() / "wc2.1_30s_bio_elev_tiff",
    )


def get_maxent_results_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_RESULTS_ROOT",
        get_maxent_project_root_default() / "results" / "maxent",
    )


def get_maxent_input_output_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_INPUT_OUTPUT_ROOT",
        get_maxent_project_root_default() / "results" / "maxent_input",
    )


def get_maxent_jar_default() -> Path:
    return resolve_env_path("MAXENT_JAR", get_maxent_root_default() / "maxent.jar")


def get_maxent_input_root_default() -> Path:
    return resolve_env_path("MAXENT_INPUT_ROOT", get_maxent_root_default())


def get_maxent_projection_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_PROJECTION_ROOT",
        get_maxent_input_root_default() / "maps",
    )


def get_maxent_output_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_OUTPUT_ROOT",
        get_maxent_project_root_default() / "results" / "maxent_future",
    )


def get_maxent_widespread_input_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_WIDESPREAD_INPUT_ROOT",
        get_maxent_project_root_default() / "data" / "maxent_future",
    )


def get_maxent_widespread_output_root_default() -> Path:
    return resolve_env_path(
        "MAXENT_WIDESPREAD_OUTPUT_ROOT",
        get_maxent_project_root_default() / "results" / "acer_widespread_future",
    )


def get_acer_release_root_default() -> Path:
    return resolve_env_path("ACER_RELEASE_ROOT", RELEASE_ROOT)


def get_acer_data_root_default() -> Path:
    return resolve_env_path("ACER_DATA_ROOT", get_acer_release_root_default())


def get_acer_wgt_work_path_default() -> Path:
    return resolve_env_path("ACER_WGT_WORK_PATH", get_acer_release_root_default() / "03_WGT_triad")


def get_acer_cds_dir_default() -> Path:
    return resolve_env_path(
        "ACER_CDS_DIR",
        get_acer_data_root_default() / "01_Genome" / "cds" / "chr_only",
    )


def get_acer_pep_dir_default() -> Path:
    return resolve_env_path(
        "ACER_PEP_DIR",
        get_acer_data_root_default() / "01_Genome" / "pep" / "chr_only",
    )


def get_acer_blast_dir_default() -> Path:
    return resolve_env_path(
        "ACER_BLAST_DIR",
        get_acer_data_root_default() / "01_Genome" / "blastp" / "01_for_collinearity",
    )


def get_acer_wgdi_gff_dir_default() -> Path:
    return resolve_env_path(
        "ACER_WGDI_GFF_DIR",
        get_acer_wgt_work_path_default() / "wgdi" / "0_gff",
    )


def get_acer_wgdi_lens_dir_default() -> Path:
    return resolve_env_path(
        "ACER_WGDI_LENS_DIR",
        get_acer_wgt_work_path_default() / "wgdi" / "0_lens",
    )


ENVIRONMENT_REQUIREMENTS = {
    "maxent": [
        {
            "env_name": "MAXENT_PROJECT_ROOT",
            "purpose": "MaxEnt 项目根目录（供 R 与 PowerShell 脚本推导数据和结果路径）",
            "default_path": get_maxent_project_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project",
            "powershell_example": r"D:\acer_project",
        },
        {
            "env_name": "MAXENT_ROOT",
            "purpose": "MaxEnt 主输入目录（含 maxent.jar、环境图层或 MaxEnt 相关输入）",
            "default_path": get_maxent_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/data/maxent",
            "powershell_example": r"D:\acer_project\data\maxent",
        },
        {
            "env_name": "MAXENT_OCC_ROOT",
            "purpose": "单物种 MaxEnt occurrence CSV 输入目录",
            "default_path": get_maxent_occ_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/data/occurrence/for_maxent",
            "powershell_example": r"D:\acer_project\data\occurrence\for_maxent",
        },
        {
            "env_name": "MAXENT_MAP_ROOT",
            "purpose": "单物种 MaxEnt 环境变量栅格目录",
            "default_path": get_maxent_map_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/data/maxent/wc2.1_30s_bio_elev_tiff",
            "powershell_example": r"D:\acer_project\data\maxent\wc2.1_30s_bio_elev_tiff",
        },
        {
            "env_name": "MAXENT_RESULTS_ROOT",
            "purpose": "单物种 MaxEnt 建模结果输出根目录",
            "default_path": get_maxent_results_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/results/maxent",
            "powershell_example": r"D:\acer_project\results\maxent",
        },
        {
            "env_name": "MAXENT_INPUT_OUTPUT_ROOT",
            "purpose": "Ayan occurrence/background 预处理输出目录",
            "default_path": get_maxent_input_output_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/results/maxent_input",
            "powershell_example": r"D:\acer_project\results\maxent_input",
        },
        {
            "env_name": "MAXENT_JAR",
            "purpose": "PowerShell 批处理调用的 maxent.jar 文件路径",
            "default_path": get_maxent_jar_default,
            "path_kind": "file",
            "linux_example": "/data/acer_project/data/maxent/maxent.jar",
            "powershell_example": r"D:\acer_project\data\maxent\maxent.jar",
        },
        {
            "env_name": "MAXENT_INPUT_ROOT",
            "purpose": "PowerShell 批处理的 occurrence/background 输入目录",
            "default_path": get_maxent_input_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/data/maxent",
            "powershell_example": r"D:\acer_project\data\maxent",
        },
        {
            "env_name": "MAXENT_PROJECTION_ROOT",
            "purpose": "PowerShell 批处理的 projection layers 根目录",
            "default_path": get_maxent_projection_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/data/maxent/maps",
            "powershell_example": r"D:\acer_project\data\maxent\maps",
        },
        {
            "env_name": "MAXENT_OUTPUT_ROOT",
            "purpose": "PowerShell 批处理未来情景输出根目录",
            "default_path": get_maxent_output_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/results/maxent_future",
            "powershell_example": r"D:\acer_project\results\maxent_future",
        },
        {
            "env_name": "MAXENT_WIDESPREAD_INPUT_ROOT",
            "purpose": "广布种未来适生区汇总脚本的输入目录",
            "default_path": get_maxent_widespread_input_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/data/maxent_future",
            "powershell_example": r"D:\acer_project\data\maxent_future",
        },
        {
            "env_name": "MAXENT_WIDESPREAD_OUTPUT_ROOT",
            "purpose": "广布种未来适生区汇总脚本的输出目录",
            "default_path": get_maxent_widespread_output_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_project/results/acer_widespread_future",
            "powershell_example": r"D:\acer_project\results\acer_widespread_future",
        },
    ],
    "wgt": [
        {
            "env_name": "ACER_RELEASE_ROOT",
            "purpose": "代码发布目录根目录",
            "default_path": get_acer_release_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release",
            "powershell_example": r"D:\acer_release",
        },
        {
            "env_name": "ACER_DATA_ROOT",
            "purpose": "WGT 数据根目录",
            "default_path": get_acer_data_root_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release",
            "powershell_example": r"D:\acer_release",
        },
        {
            "env_name": "ACER_WGT_WORK_PATH",
            "purpose": "03_WGT_triad 工作目录",
            "default_path": get_acer_wgt_work_path_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release/03_WGT_triad",
            "powershell_example": r"D:\acer_release\03_WGT_triad",
        },
        {
            "env_name": "ACER_CDS_DIR",
            "purpose": "WGT 所需 CDS FASTA 输入目录",
            "default_path": get_acer_cds_dir_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release/01_Genome/cds/chr_only",
            "powershell_example": r"D:\acer_release\01_Genome\cds\chr_only",
        },
        {
            "env_name": "ACER_PEP_DIR",
            "purpose": "WGT 所需 PEP FASTA 输入目录",
            "default_path": get_acer_pep_dir_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release/01_Genome/pep/chr_only",
            "powershell_example": r"D:\acer_release\01_Genome\pep\chr_only",
        },
        {
            "env_name": "ACER_BLAST_DIR",
            "purpose": "WGT 所需 BLASTP 输入目录",
            "default_path": get_acer_blast_dir_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release/01_Genome/blastp/01_for_collinearity",
            "powershell_example": r"D:\acer_release\01_Genome\blastp\01_for_collinearity",
        },
        {
            "env_name": "ACER_WGDI_GFF_DIR",
            "purpose": "WGDI GFF 目录",
            "default_path": get_acer_wgdi_gff_dir_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release/03_WGT_triad/wgdi/0_gff",
            "powershell_example": r"D:\acer_release\03_WGT_triad\wgdi\0_gff",
        },
        {
            "env_name": "ACER_WGDI_LENS_DIR",
            "purpose": "WGDI lens 目录",
            "default_path": get_acer_wgdi_lens_dir_default,
            "path_kind": "dir",
            "linux_example": "/data/acer_release/03_WGT_triad/wgdi/0_lens",
            "powershell_example": r"D:\acer_release\03_WGT_triad\wgdi\0_lens",
        },
    ],
}


def read_name_list(file_path: Path) -> list[str]:
    if not file_path.exists():
        return []

    items: list[str] = []
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        items.append(line)
    return items


PYTHON_IMPORT_NAMES = read_name_list(PYTHON_REQUIREMENTS_FILE)
R_PACKAGE_NAMES = read_name_list(R_REQUIREMENTS_FILE)


def detect_command(tool_name: str) -> str | None:
    for candidate in COMMAND_CANDIDATES.get(tool_name, [tool_name]):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def get_tool_candidates(tool_name: str) -> list[str]:
    return list(COMMAND_CANDIDATES.get(tool_name, [tool_name]))


def get_selected_profiles(profile: str) -> list[str]:
    if profile == "all":
        return ["python", "maxent", "wgt"]
    if profile not in PROFILE_LABELS:
        raise ValueError(f"Unsupported profile: {profile}")
    return [profile]
