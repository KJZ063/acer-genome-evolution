# 用途 | Purpose:
# - 运行 Acer truncatum 的单物种 MaxEnt 分析。
# - Run the single-species MaxEnt analysis for Acer truncatum.
# 输入 | Inputs:
# - 物种分布点 CSV、环境栅格，以及本目录脚本使用的路径环境变量。
# - Species occurrence CSV, environmental rasters, and the path environment variables used by the scripts in this directory.
# 输出 | Outputs:
# - 在 Atru_300kmBuffer 下输出背景点、occurrence 表、MaxEnt 评估结果和图件。
# - Write background points, occurrence tables, MaxEnt evaluation results, and figures under Atru_300kmBuffer.
# 使用提示 | Usage Notes:
# 1. 直接运行当前脚本即可载入同目录函数并开始分析。 / Run this script directly to load the functions in the same directory and start the analysis.
# 2. 如需调整参数，可修改物种代码、缓冲距离、背景点数量和输出目录。 / To change settings, edit the species code, buffer distance, background point counts, and output directory.
# 3. 运行前确认输入数据与环境变量路径已准备完成。 / Before running, confirm that the input data and environment-variable paths are ready.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg) > 0) {
  normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/", mustWork = FALSE)
} else {
  normalizePath(getwd(), winslash = "/", mustWork = FALSE)
}
source(file.path(dirname(script_path), "single_species_maxent_common.R"))

run_single_species_maxent(get_single_species_config(
  sp = "Atru",
  buffer_km = 300,
  background_n = 20000,
  background_sample_n = 10000,
  output_subdir = "Atru_300kmBuffer"
))