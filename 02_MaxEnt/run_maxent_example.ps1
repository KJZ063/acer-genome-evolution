<#
用途 | Purpose:
- 批量运行当前配置中的未来情景 MaxEnt 投影。
- Batch-run the configured future-scenario MaxEnt projections.
输入 | Inputs:
- occurrence 与 background CSV、未来情景环境层目录、maxent.jar，以及脚本中读取的路径环境变量。
- Occurrence and background CSV files, future-scenario environmental layers, maxent.jar, and the path environment variables read by the script.
输出 | Outputs:
- 为每个物种与情景组合创建独立输出目录，并写出 MaxEnt 结果文件与图件。
- Create one output directory per species/scenario combination and write the MaxEnt result files and figures.
步骤 | Steps:
1. 解析项目、输入、投影层和输出目录。 / Resolve the project, input, projection-layer, and output directories.
2. 按脚本中的物种或情景列表逐项组织参数。 / Assemble parameters for each species or scenario listed in the script.
3. 调用 java density.MaxEnt 执行原始 MaxEnt 命令。 / Call java density.MaxEnt to run the original MaxEnt command.
#>

$ErrorActionPreference = "Stop"

# 输入与输出路径 / Input and output paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = if ($env:MAXENT_PROJECT_ROOT) { $env:MAXENT_PROJECT_ROOT } else { (Resolve-Path (Join-Path $scriptDir "..\..")).Path }
$maxentRoot = if ($env:MAXENT_ROOT) { $env:MAXENT_ROOT } else { Join-Path $projectRoot "data\maxent" }
$maxentJar = if ($env:MAXENT_JAR) { $env:MAXENT_JAR } else { Join-Path $maxentRoot "maxent.jar" }
$inputRoot = if ($env:MAXENT_INPUT_ROOT) { $env:MAXENT_INPUT_ROOT } else { $maxentRoot }
$projectionRoot = if ($env:MAXENT_PROJECTION_ROOT) { $env:MAXENT_PROJECTION_ROOT } else { Join-Path $inputRoot "maps" }
$outputRoot = if ($env:MAXENT_OUTPUT_ROOT) { $env:MAXENT_OUTPUT_ROOT } else { Join-Path $projectRoot "results\maxent_future" }

# 运行物种与情景列表 / Species and scenario list
$runs = @(
    @{
        Species = "Acat"
        Scenario = "wc2.1_30s_bioc_ACCESS-CM2_ssp245_2081-2100"
    }
)

foreach ($run in $runs) {
    $outDir = Join-Path $outputRoot ("{0}_{1}_output" -f $run.Species, $run.Scenario)
    if (!(Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }

    $projectionLayers = Join-Path $projectionRoot $run.Scenario
    $samplesFile = Join-Path $inputRoot ("{0}_occurrences_filtered_factors.csv" -f $run.Species)
    $backgroundFile = Join-Path $inputRoot ("{0}_bg_filtered_factors.csv" -f $run.Species)

    # MaxEnt 运行参数 / MaxEnt runtime arguments
    $arguments = @(
        "-Xmx80G", "-cp", $maxentJar, "density.MaxEnt",
        "nowarnings", "noprefixes",
        "responsecurves", "jackknife",
        "outputdirectory=$outDir",
        "projectionlayers=$projectionLayers",
        "samplesfile=$samplesFile",
        "environmentallayers=$backgroundFile",
        "replicates=10", "writeplotdata", "appendtoresultsfile", "autorun", "threads=12"
    )

    & java @arguments
}
