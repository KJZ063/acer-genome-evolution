# 用途 | Purpose:
# - 批量处理未来分布预测结果中的 *_avg.asc 文件，并输出分类地图、点表和汇总。
# - Batch-process *_avg.asc files from future distribution predictions and export classified maps, point tables, and summaries.
# 输入 | Inputs:
# - 递归位于 MAXENT_WIDESPREAD_INPUT_ROOT 下的 *_avg.asc 栅格，以及世界陆地边界数据。
# - *_avg.asc rasters found recursively under MAXENT_WIDESPREAD_INPUT_ROOT, plus world land-boundary data.
# 输出 | Outputs:
# - transparent_overlay、white_global_png、plot_points_csv、logs 和汇总表。
# - transparent_overlay, white_global_png, plot_points_csv, logs, and summary tables.
# 步骤 | Steps:
# 1. 解析输入输出目录并加载底图。 / Resolve input and output directories and load the base map.
# 2. 查找所有 *_avg.asc 文件并按阈值分类。 / Find all *_avg.asc files and classify values by threshold.
# 3. 输出 PNG、点位 CSV 和整体汇总。 / Export PNG files, point CSV files, and overall summaries.
# ============================================================

cat("0. Loading packages and setting up environment...\n")
options(repos = c(CRAN = "https://cloud.r-project.org"))

packages <- c(
  "terra", "sf", "classInt", "ggplot2",
  "rnaturalearth", "rnaturalearthdata", "dplyr"
)

for (p in packages) {
  if (!require(p, character.only = TRUE)) {
    install.packages(p)
    library(p, character.only = TRUE)
  }
}

# ============================================================
# 1. 输入输出路径 / Input and output paths
# ============================================================
args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg) > 0) {
  normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/", mustWork = FALSE)
} else {
  normalizePath(getwd(), winslash = "/", mustWork = FALSE)
}
script_dir <- dirname(script_path)
project_root <- normalizePath(Sys.getenv("MAXENT_PROJECT_ROOT", file.path(script_dir, "..", "..")), winslash = "/", mustWork = FALSE)

input_root <- normalizePath(
  Sys.getenv("MAXENT_WIDESPREAD_INPUT_ROOT", file.path(project_root, "data", "maxent_future")),
  winslash = "/",
  mustWork = FALSE
)
output_root <- normalizePath(
  Sys.getenv("MAXENT_WIDESPREAD_OUTPUT_ROOT", file.path(project_root, "results", "acer_widespread_future")),
  winslash = "/",
  mustWork = FALSE
)

dir_transparent <- file.path(output_root, "transparent_overlay")
dir_white       <- file.path(output_root, "white_global_png")
dir_points      <- file.path(output_root, "plot_points_csv")
dir_logs        <- file.path(output_root, "logs")
dir_scripts     <- file.path(output_root, "scripts")

for (d in c(output_root, dir_transparent, dir_white, dir_points, dir_logs, dir_scripts)) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE)
}

threshold <- 0.3
set.seed(114514)

# ============================================================
# 2. 读取全球陆地边界 / Load world land boundaries
# Use EQC with central meridian 150E / 使用以 150E 为中央经线的等距圆柱投影
# ============================================================
cat("\n1. Loading world land boundary...\n")

sf::sf_use_s2(FALSE)

world <- ne_countries(scale = "medium", returnclass = "sf")
world <- st_make_valid(world)
world <- st_transform(world, 4326)

# 合并陆地边界以减少伪影 / Merge land polygons to reduce edge artifacts
world_land <- world |>
  summarise(geometry = st_union(geometry)) |>
  st_make_valid()

# 矩形世界图并以太平洋居中 / Use a rectangular world map centered on the Pacific
proj_world <- "+proj=eqc +lon_0=150 +datum=WGS84 +units=m +no_defs"

world_land_proj <- st_transform(world_land, crs = proj_world)

# ============================================================
# 3. 查找 avg.asc 文件 / Discover avg.asc files
# ============================================================
cat("\n2. Searching for all *_avg.asc files under input_root / 在 input_root 下查找 *_avg.asc ...\n")

asc_files <- list.files(
  path = input_root,
  pattern = "avg\\.asc$",
  recursive = TRUE,
  full.names = TRUE,
  ignore.case = TRUE
)

cat("   Found", length(asc_files), "files.\n")

if (length(asc_files) == 0) {
  stop(sprintf("No avg.asc files found under input_root: %s", input_root))
}

# ============================================================
# 4. 结果处理函数 / Result-processing helper functions
# ============================================================
get_prefix <- function(filepath) {
  gsub("\\.asc$", "", basename(filepath), ignore.case = TRUE)
}

calc_breaks <- function(v, n = 3) {
  v <- v[is.finite(v)]
  if (length(v) < 3) stop("Not enough valid values for classification.")
  
  uv <- unique(v)
  
  if (length(uv) < 3) {
    qs <- quantile(v, probs = c(0, 0.5, 0.9, 1), na.rm = TRUE)
    brks <- as.numeric(qs)
    brks <- unique(brks)
    if (length(brks) < 4) {
      mn <- min(v, na.rm = TRUE)
      mx <- max(v, na.rm = TRUE)
      brks <- c(mn, mn + (mx - mn) / 3, mn + 2 * (mx - mn) / 3, mx)
    }
    return(brks)
  }
  
  out <- try(classIntervals(v, n = n, style = "fisher")$brks, silent = TRUE)
  
  if (inherits(out, "try-error") || length(unique(out)) < 4) {
    qs <- quantile(v, probs = c(0, 0.5, 0.9, 1), na.rm = TRUE)
    brks <- as.numeric(qs)
    brks <- unique(brks)
    if (length(brks) < 4) {
      mn <- min(v, na.rm = TRUE)
      mx <- max(v, na.rm = TRUE)
      brks <- c(mn, mn + (mx - mn) / 3, mn + 2 * (mx - mn) / 3, mx)
    }
    return(brks)
  }
  
  out
}

calc_stats <- function(r_class_sub, class_value) {
  freq_tab <- terra::freq(r_class_sub, digits = 0)
  point_n <- 0
  
  if (!is.null(freq_tab)) {
    freq_tab <- as.data.frame(freq_tab)
    if ("value" %in% colnames(freq_tab) && any(freq_tab$value == class_value)) {
      point_n <- freq_tab$count[freq_tab$value == class_value][1]
    }
  }
  
  area_r <- cellSize(r_class_sub, unit = "km")
  area_mask <- ifel(r_class_sub == class_value, area_r, NA)
  area_km2 <- global(area_mask, "sum", na.rm = TRUE)[1, 1]
  if (is.na(area_km2)) area_km2 <- 0
  
  list(point_n = point_n, area_km2 = area_km2)
}

# ============================================================
# 5. 主处理循环 / Main processing loop
# ============================================================
cat("\n3. Start processing files...\n")

summary_list <- list()
error_log <- c()

for (i in seq_along(asc_files)) {
  f <- asc_files[i]
  prefix <- get_prefix(f)
  
  cat("\n--------------------------------------------------\n")
  cat(sprintf("[%d/%d] Processing: %s\n", i, length(asc_files), f))
  
  res <- try({
    
    # --------------------------------------------------------
    # 5.1 读栅格
    # --------------------------------------------------------
    r <- rast(f)
    
    if (is.na(crs(r)) || crs(r) == "") {
      crs(r) <- "EPSG:4326"
    }
    
    # --------------------------------------------------------
    # 5.2 采样并计算 breaks
    # --------------------------------------------------------
    cat("   Sampling raster values...\n")
    v_sample <- spatSample(
      r,
      size = 500000,
      method = "regular",
      na.rm = TRUE,
      as.df = FALSE
    )
    
    v_high <- v_sample[v_sample >= threshold]
    
    if (length(v_high) < 3) {
      stop("Not enough values >= threshold for classification.")
    }
    
    if (length(v_high) > 10000) {
      v_high_sample <- sample(v_high, 10000)
    } else {
      v_high_sample <- v_high
    }
    
    cat("   Calculating Fisher breaks...\n")
    brks <- calc_breaks(v_high_sample, n = 3)
    
    if (length(brks) < 4) {
      stop("Break calculation failed: less than 4 break points.")
    }
    
    brks <- sort(unique(as.numeric(brks)))
    
    if (length(brks) < 4) {
      mn <- min(v_high_sample, na.rm = TRUE)
      mx <- max(v_high_sample, na.rm = TRUE)
      brks <- c(mn, mn + (mx - mn) / 3, mn + 2 * (mx - mn) / 3, mx)
    }
    
    b1 <- brks[2]
    b2 <- brks[3]
    bmax <- max(brks, na.rm = TRUE)
    
    if (b1 >= b2) {
      stop("Invalid breaks: b1 >= b2")
    }
    
    cat(
      "   Breaks:",
      paste(round(c(brks[1], b1, b2, bmax), 4), collapse = ", "),
      "\n"
    )
    
    # --------------------------------------------------------
    # 5.3 重分类
    # --------------------------------------------------------
    rcl_mat <- matrix(
      c(
        0,  b1,   1,
        b1, b2,   2,
        b2, bmax, 3
      ),
      ncol = 3,
      byrow = TRUE
    )
    
    r_class <- classify(r, rcl_mat, include.lowest = TRUE, right = TRUE)
    r_class[r < threshold] <- NA
    r_class[r_class < 2] <- NA
    
    # --------------------------------------------------------
    # 5.4 统计
    # --------------------------------------------------------
    cat("   Calculating global stats...\n")
    stats_suit <- calc_stats(r_class, 2)
    stats_high <- calc_stats(r_class, 3)
    
    # --------------------------------------------------------
    # 5.5 提取点
    # --------------------------------------------------------
    r_stack <- c(r_class, r)
    names(r_stack) <- c("class_id", "value")
    
    pts_global <- as.data.frame(r_stack, xy = TRUE, na.rm = TRUE)
    
    if (nrow(pts_global) == 0) {
      stop("No suitable / highly suitable cells after classification.")
    }
    
    pts_global$class_label <- factor(
      pts_global$class_id,
      levels = c(2, 3),
      labels = c("Suitable", "Highly Suitable")
    )
    
    # Keep suitable cells only for redraw / 仅保留适生点以便后续重绘
    pts_csv_df <- pts_global |>
      dplyr::transmute(
        longitude = x,
        latitude = y,
        class_label = as.character(class_label),
        value = value
      )
    
    points_csv <- file.path(dir_points, paste0(prefix, "_plot_points.csv"))
    write.csv(pts_csv_df, points_csv, row.names = FALSE)
    
    # --------------------------------------------------------
    # 5.6 点投影到中央经线 150E 的矩形世界图
    # --------------------------------------------------------
    cat("   Projecting points...\n")
    
    pts_sf <- st_as_sf(pts_global, coords = c("x", "y"), crs = 4326)
    pts_proj <- st_transform(pts_sf, crs = proj_world)
    
    coords_proj <- st_coordinates(pts_proj)
    
    pts_proj_df <- pts_proj
    pts_proj_df$x_proj <- coords_proj[, 1]
    pts_proj_df$y_proj <- coords_proj[, 2]
    pts_proj_df <- st_drop_geometry(pts_proj_df)
    
    # --------------------------------------------------------
    # 5.7 透明背景全球图（无图例）
    # --------------------------------------------------------
    cat("   Plotting transparent global overlay...\n")
    
    p_trans <- ggplot() +
      geom_sf(
        data = world_land_proj,
        fill = "transparent",
        color = "transparent",
        linewidth = 0.2
      ) +
      geom_point(
        data = pts_proj_df,
        aes(x = x_proj, y = y_proj, color = class_label),
        size = 0.3
      ) +
      scale_color_manual(
        values = c(
          "Suitable" = "#5FA2FF",
          "Highly Suitable" = "#09479B"
        )
      ) +
      theme_void() +
      theme(
        legend.position = "none",
        panel.background = element_rect(fill = "transparent", color = NA),
        plot.background  = element_rect(fill = "transparent", color = NA)
      )
    
    png_trans <- file.path(dir_transparent, paste0(prefix, "_transparent.png"))
    pdf_trans <- file.path(dir_transparent, paste0(prefix, "_transparent.pdf"))
    
    ggsave(
      png_trans, plot = p_trans,
      width = 12, height = 6, dpi = 300, bg = "transparent"
    )
    ggsave(
      pdf_trans, plot = p_trans,
      width = 12, height = 6, bg = "transparent"
    )
    
    # --------------------------------------------------------
    # 5.8 白底全球图（无图例）
    # --------------------------------------------------------
    cat("   Plotting white-background global map...\n")
    
    p_white <- ggplot() +
      geom_sf(
        data = world_land_proj,
        fill = "white",
        color = "grey40",
        linewidth = 0.25
      ) +
      geom_point(
        data = pts_proj_df,
        aes(x = x_proj, y = y_proj, color = class_label),
        size = 0.3
      ) +
      scale_color_manual(
        values = c(
          "Suitable" = "#5FA2FF",
          "Highly Suitable" = "#09479B"
        )
      ) +
      theme_void() +
      theme(
        legend.position = "none",
        panel.background = element_rect(fill = "white", color = NA),
        plot.background  = element_rect(fill = "white", color = NA)
      )
    
    png_white <- file.path(dir_white, paste0(prefix, "_white_global.png"))
    
    ggsave(
      png_white, plot = p_white,
      width = 12, height = 6, dpi = 300, bg = "white"
    )
    
    # --------------------------------------------------------
    # 5.9 汇总结果
    # --------------------------------------------------------
    data.frame(
      file_id = i,
      file_name = basename(f),
      input_path = f,
      
      break_min = round(brks[1], 3),
      break_b1  = round(b1, 3),
      break_b2  = round(b2, 3),
      break_max = round(bmax, 3),
      
      suitable_points = stats_suit$point_n,
      highly_suitable_points = stats_high$point_n,
      suitable_area_km2 = round(stats_suit$area_km2, 3),
      highly_suitable_area_km2 = round(stats_high$area_km2, 3),
      
      transparent_png = png_trans,
      transparent_pdf = pdf_trans,
      white_global_png = png_white,
      plot_points_csv = points_csv,
      
      stringsAsFactors = FALSE
    )
    
  }, silent = TRUE)
  
  if (inherits(res, "try-error")) {
    msg <- paste0("[ERROR] ", basename(f), " -> ", as.character(res))
    cat(msg, "\n")
    error_log <- c(error_log, msg)
  } else {
    summary_list[[length(summary_list) + 1]] <- res
    cat("   Done.\n")
  }
}

# ============================================================
# 6. 输出总表与日志 / Save summaries and logs
# ============================================================
cat("\n4. Saving summary tables...\n")

if (length(summary_list) > 0) {
  summary_df <- bind_rows(summary_list)
  summary_csv <- file.path(output_root, "summary_all_files.csv")
  write.csv(summary_df, summary_csv, row.names = FALSE)
  cat("   Summary saved to:\n   ", summary_csv, "\n")
} else {
  cat("   No successful results to save.\n")
}

if (length(error_log) > 0) {
  log_file <- file.path(dir_logs, "error_log.txt")
  writeLines(error_log, log_file)
  cat("   Error log saved to:\n   ", log_file, "\n")
} else {
  cat("   No errors.\n")
}

cat("\nAll finished.\n")
