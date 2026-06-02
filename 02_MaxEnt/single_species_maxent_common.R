# 用途 | Purpose:
# - 提供单物种 MaxEnt 分析所需的路径解析、背景点准备、模型评估和环境变量相关性输出函数。
# - Provide the functions needed for single-species MaxEnt analyses, including path resolution, background-point preparation, model evaluation, and environmental-variable correlation export.
# 输入 | Inputs:
# - 物种分布点 CSV、环境栅格、MaxEnt 所需依赖包，以及可选的路径环境变量。
# - Species occurrence CSV files, environmental rasters, required MaxEnt packages, and optional path environment variables.
# 输出 | Outputs:
# - 背景点与 occurrence 表、模型 RDS、统计表、响应曲线图、贡献图和相关性矩阵。
# - Background and occurrence tables, model RDS files, statistics tables, response-curve plots, contribution plots, and correlation matrices.
# 使用提示 | Usage Notes:
# 1. 先在单物种脚本中设置物种代码、缓冲距离和输出目录。 / Set the species code, buffer distance, and output directory in a species script first.
# 2. 再运行对应脚本以调用本文件中的数据准备、建模和结果导出函数。 / Then run the target script to call the data-preparation, modeling, and export functions defined here.
# 3. 可通过环境变量覆盖项目根目录、输入目录和输出目录。 / You can override the project root, input directories, and output directory with environment variables.

library(ENMeval)
library(raster)
library(dismo)
library(ecospat)
library(dplyr)
library(sf)
library(kuenm)
library(ggplot2)

# 计算 pROC 评估指标 / Compute pROC evaluation metrics
proc <- function(vars) {
  proc_result <- kuenm::kuenm_proc(
    vars$occs.val.pred,
    c(vars$bg.train.pred, vars$bg.val.pred)
  )

  data.frame(
    proc_auc_ratio = proc_result$pROC_summary[1],
    proc_pval = proc_result$pROC_summary[2],
    row.names = NULL
  )
}

# 物种学名映射 / Species scientific-name lookup
sp_dict <- list(
  "Acat" = "Acer catalpifolium",
  "Aneg" = "Acer negundo",
  "Apal" = "Acer palmatum",
  "Apse" = "Acer pseudosieboldianum",
  "Asac" = "Acer saccharum",
  "Atru" = "Acer truncatum",
  "Ayan" = "Acer yangbiense",
  "Ddye" = "Dipteronia dyeriana",
  "Dsin" = "Dipteronia sinensis"
)

# 构建单物种运行配置 / Build the single-species run configuration
get_single_species_config <- function(
  sp,
  buffer_km,
  background_n,
  background_sample_n,
  output_subdir,
  output_root_env = "MAXENT_RESULTS_ROOT",
  output_root_default = "results/maxent",
  run_modeling = TRUE,
  run_correlation = TRUE,
  add_extra_points = FALSE
) {
  list(
    sp = sp,
    buffer_km = buffer_km,
    background_n = background_n,
    background_sample_n = background_sample_n,
    output_subdir = output_subdir,
    output_root_env = output_root_env,
    output_root_default = output_root_default,
    run_modeling = run_modeling,
    run_correlation = run_correlation,
    add_extra_points = add_extra_points
  )
}

# 定位当前脚本目录 / Locate the current script directory
get_maxent_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)

  script_path <- if (length(file_arg) > 0) {
    normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/", mustWork = FALSE)
  } else {
    normalizePath(getwd(), winslash = "/", mustWork = FALSE)
  }

  dirname(script_path)
}

# 解析项目输入输出路径 / Resolve project input and output paths
get_project_paths <- function(config) {
  script_dir <- get_maxent_script_dir()
  project_root <- normalizePath(
    Sys.getenv("MAXENT_PROJECT_ROOT", file.path(script_dir, "..", "..")),
    winslash = "/",
    mustWork = FALSE
  )
  maxent_root <- normalizePath(
    Sys.getenv("MAXENT_ROOT", file.path(project_root, "data", "maxent")),
    winslash = "/",
    mustWork = FALSE
  )
  occ_root <- normalizePath(
    Sys.getenv("MAXENT_OCC_ROOT", file.path(project_root, "data", "occurrence", "for_maxent")),
    winslash = "/",
    mustWork = FALSE
  )
  map_root <- normalizePath(
    Sys.getenv("MAXENT_MAP_ROOT", file.path(maxent_root, "wc2.1_30s_bio_elev_tiff")),
    winslash = "/",
    mustWork = FALSE
  )
  output_root <- normalizePath(
    Sys.getenv(config$output_root_env, file.path(project_root, config$output_root_default)),
    winslash = "/",
    mustWork = FALSE
  )

  list(
    script_dir = script_dir,
    project_root = project_root,
    maxent_root = maxent_root,
    occ_root = occ_root,
    map_root = map_root,
    output_root = output_root
  )
}

# 为 Ayan 生成额外 occurrence 点 / Generate extra occurrence points for Ayan
add_ayan_extra_points <- function(occs) {
  center_lon <- 102 + 33 / 60 + 35 / 3600
  center_lat <- 26 + 8 / 60 + 42 / 3600

  center_point <- st_sfc(st_point(c(center_lon, center_lat)), crs = 4326)
  buffer_20km <- st_transform(
    center_point,
    crs = "+proj=aeqd +lat_0=26.145 +lon_0=102.5597 +datum=WGS84"
  ) %>%
    st_buffer(dist = 20000) %>%
    st_transform(crs = 4326)

  extra_points <- st_sample(buffer_20km, size = 30, type = "random") %>%
    st_coordinates() %>%
    as.data.frame()
  colnames(extra_points) <- c("longitude", "latitude")

  rbind(occs, extra_points)
}

# 准备 occurrence 与背景点 / Prepare occurrence and background points
prepare_occurrence_background <- function(config) {
  paths <- get_project_paths(config)
  setwd(paths$maxent_root)

  occu_file <- file.path(paths$occ_root, sprintf("%s_for_maxent.csv", config$sp))
  occurrences <- read.csv(occu_file)
  occs <- occurrences[, c("longitude", "latitude")]

  if (isTRUE(config$add_extra_points)) {
    occs <- add_ayan_extra_points(occs)
  }

  files <- list.files(path = paths$map_root, pattern = "tif$", full.names = TRUE)
  envs <- stack(files)

  occs.sf <- st_as_sf(occs, coords = c("longitude", "latitude"), crs = crs(envs))

  eckertIV <- "+proj=eck4 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
  occs.sf <- st_transform(occs.sf, crs = eckertIV)

  occs.buf <- occs.sf %>%
    st_buffer(dist = config$buffer_km * 1000) %>%
    st_union() %>%
    st_sf() %>%
    st_transform(crs = crs(envs))

  envs.masked <- crop(envs, occs.buf)
  envs.masked <- mask(envs.masked, occs.buf)

  all_bg_points <- randomPoints(envs[[1]], n = config$background_n) %>% as.data.frame()
  colnames(all_bg_points) <- c("longitude", "latitude")

  all_bg_points.sf <- st_as_sf(
    all_bg_points,
    coords = c("longitude", "latitude"),
    crs = crs(envs)
  )
  outside_bg_points.sf <- all_bg_points.sf[
    !st_intersects(all_bg_points.sf, occs.buf, sparse = FALSE),
  ]

  set.seed(123)
  bg_points <- outside_bg_points.sf %>%
    sample_n(config$background_sample_n) %>%
    st_coordinates() %>%
    as.data.frame()
  colnames(bg_points) <- c("longitude", "latitude")

  bg_env_values <- extract(envs, bg_points)
  species_name <- sp_dict[[config$sp]]
  bg_data <- cbind(species = species_name, bg_points, bg_env_values)

  occ_env_values <- extract(envs, occs)
  occ_data <- cbind(species = species_name, occs, occ_env_values)

  output_path <- file.path(paths$output_root, config$output_subdir, "")
  if (!dir.exists(output_path)) {
    dir.create(output_path, recursive = TRUE)
  }

  write.csv(bg_data, paste0(output_path, "bg.csv"), row.names = FALSE)
  write.csv(occ_data, paste0(output_path, "occurrences.csv"), row.names = FALSE)

  png(
    filename = paste0(output_path, "background_and_occurrence_points.png"),
    width = 8,
    height = 8,
    units = "in",
    res = 300
  )
  plot(envs[[1]], main = paste("Background and Occurrence Points on", names(envs)[1]))
  points(bg_points, pch = 20, cex = 0.4, col = "black")
  points(occs, pch = 20, cex = 0.4, col = "red")
  dev.off()

  list(
    sp = config$sp,
    output_path = output_path,
    occu_path = file.path(paths$occ_root, ""),
    map_root = paths$map_root,
    results_root = paths$output_root,
    envs = envs,
    envs.bg = envs.masked,
    occs = occs,
    bg = bg_points,
    species_name = species_name
  )
}

# 根据物种数据量选择分区方式 / Choose the partition method based on species data volume
get_partitions <- function(context) {
  if (context$sp %in% c("Acat", "Ayan", "Ddye", "Dsin")) {
    partitions <- "jackknife"
    jack <- get.jackknife(context$occs, context$bg)
    png(
      filename = paste0(context$output_path, "jackknife_points.png"),
      width = 8,
      height = 8,
      units = "in",
      res = 300
    )
    evalplot.grps(pts = context$occs, pts.grp = jack$occs.grp, envs = context$envs.bg)
    dev.off()
  } else {
    partitions <- "block"
    block <- get.block(context$occs, context$bg, orientation = "lat_lon")
    png(
      filename = paste0(context$output_path, "block_points.png"),
      width = 8,
      height = 8,
      units = "in",
      res = 300
    )
    evalplot.grps(pts = context$occs, pts.grp = block$occs.grp, envs = context$envs.bg[[1]]) +
      ggplot2::ggtitle("Spatial block partitions: occurrences")
    dev.off()
  }

  partitions
}

# 运行单物种 MaxEnt 建模 / Run single-species MaxEnt modeling
run_single_species_model <- function(context) {
  partitions <- get_partitions(context)
  rm_values <- seq(from = 0.5, to = 4, by = 0.5)

  e.mx <- ENMevaluate(
    occs = context$occs,
    envs = context$envs,
    bg = context$bg,
    algorithm = "maxent.jar",
    partitions = partitions,
    tune.args = list(
      fc = c("L", "H", "LQ", "LQH", "LQT", "LQP", "LQHP", "LQHPT"),
      rm = rm_values
    ),
    user.eval = proc
  )

  rds_file <- sprintf("%s_5m_jar.rds", context$sp)
  saveRDS(e.mx, file = paste0(context$output_path, rds_file))

  png(filename = paste0(context$output_path, "auc_plot_1.png"), width = 8, height = 10, units = "in", res = 300)
  evalplot.stats(e = e.mx, stats = c("or.mtp", "auc.val"), color = "fc", x.var = "rm", dodge = 0.5)
  dev.off()

  png(filename = paste0(context$output_path, "auc_plot_2.png"), width = 8, height = 10, units = "in", res = 300)
  evalplot.stats(e = e.mx, stats = c("or.mtp", "auc.val"), color = "fc", x.var = "rm", error.bars = FALSE)
  dev.off()

  res <- eval.results(e.mx)
  write.csv(res, paste0(context$output_path, "maxent_result_stat.csv"))

  opt.seq <- res %>%
    filter(or.10p.avg == min(or.10p.avg)) %>%
    filter(auc.val.avg == max(auc.val.avg))

  png(filename = paste0(context$output_path, "response_curves.png"), width = 10, height = 10, units = "in", res = 300)
  dismo::response(eval.models(e.mx)[[opt.seq$tune.args]])
  dev.off()

  mod.seq <- eval.models(e.mx)[[opt.seq$tune.args]]
  png(filename = paste0(context$output_path, "variable_contributions.png"), width = 10, height = 10, units = "in", res = 300)
  plot(mod.seq, type = "cloglog")
  dev.off()

  png(filename = paste0(context$output_path, "predict_area.png"), width = 20, height = 10, units = "in", res = 300)
  pred.seq <- eval.predictions(e.mx)[[opt.seq$tune.args]]
  plot(pred.seq, main = paste0("Potential Suitable Habitat of ", sp_dict[[context$sp]]))
  dev.off()
}

# 输出环境变量相关性矩阵 / Export the environmental-variable correlation matrix
run_single_species_correlation <- function(context) {
  occu_file <- file.path(context$occu_path, sprintf("%s_for_maxent.csv", context$sp))
  occurrences <- read.csv(occu_file)
  occs <- occurrences[, c("longitude", "latitude")]

  coordinates(occs) <- ~longitude + latitude
  proj4string(occs) <- CRS("+proj=longlat +datum=WGS84")

  files <- list.files(path = context$map_root, pattern = "tif$", full.names = TRUE)
  envs_30s <- stack(files)

  points_data <- extract(envs_30s, occs)
  points_df <- as.data.frame(points_data)
  points_df_clean <- na.omit(points_df)
  spearman_corr <- cor(points_df_clean, method = "spearman", use = "complete.obs")

  correlation_output_path <- file.path(context$results_root, sprintf("%s_5m", context$sp), "")
  if (!dir.exists(correlation_output_path)) {
    dir.create(correlation_output_path, recursive = TRUE)
  }

  print(spearman_corr)
  write.csv(spearman_corr, file = paste0(correlation_output_path, "spearman_correlation.csv"))
}

# 执行单物种 MaxEnt 全部步骤 / Run all single-species MaxEnt steps
run_single_species_maxent <- function(config) {
  context <- prepare_occurrence_background(config)

  if (isTRUE(config$run_modeling)) {
    run_single_species_model(context)
  }

  if (isTRUE(config$run_correlation)) {
    run_single_species_correlation(context)
  }

  invisible(context)
}
