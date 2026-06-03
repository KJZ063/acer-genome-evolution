# 用途 | Purpose:
# - 为 Acer yangbiense 准备 MaxEnt 输入数据，并按脚本设置补充额外 occurrence 点，不执行建模。
# - Prepare MaxEnt input data for Acer yangbiense and add extra occurrence points as configured, without running the modeling step.
# 输入 | Inputs:
# - 原始 occurrence CSV、环境栅格，以及本目录脚本使用的路径环境变量。
# - The original occurrence CSV, environmental rasters, and the path environment variables used by the scripts in this directory.
# 输出 | Outputs:
# - 在 results/maxent_input 下输出 occurrence 与 background 数据，供后续 MaxEnt 运行使用。
# - Write occurrence and background data under results/maxent_input for subsequent MaxEnt runs.
# 使用提示 | Usage Notes:
# 1. 运行当前脚本可生成后续分析所需的输入数据。 / Run this script to generate the input data needed for later analyses.
# 2. 如需调整数据范围，可修改物种、缓冲距离和额外 occurrence 点选项。 / To adjust data coverage, edit the species, buffer distance, and extra occurrence-point option.
# 3. 本脚本不执行建模与相关性分析。 / This script does not run modeling or correlation analysis.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg) > 0) {
  normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/", mustWork = FALSE)
} else {
  normalizePath(getwd(), winslash = "/", mustWork = FALSE)
}
source(file.path(dirname(script_path), "single_species_maxent_common.R"))

run_single_species_maxent(get_single_species_config(
  sp = "Ayan",
  buffer_km = 50,
  background_n = 20000,
  background_sample_n = 10000,
  output_subdir = "Ayan_add30",
  output_root_env = "MAXENT_INPUT_OUTPUT_ROOT",
  output_root_default = "results/maxent_input",
  run_modeling = FALSE,
  run_correlation = FALSE,
  add_extra_points = TRUE
))
