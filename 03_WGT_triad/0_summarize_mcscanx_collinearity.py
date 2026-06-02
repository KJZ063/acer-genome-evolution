"""
用途 | Purpose:
- 汇总每个物种的 MCScanX .collinearity 文件，统计共线区块数、基因对数和参与基因数。
- Summarize each species-specific MCScanX .collinearity file and report the number of collinear blocks, gene pairs, and participating genes.
输入 | Inputs:
- 0_mcscanx_output/<sp>_<sp>/<sp>_<sp>.collinearity 文件，以及 ACER_SPECIES、ACER_WGT_WORK_PATH 指定的运行范围。
- The 0_mcscanx_output/<sp>_<sp>/<sp>_<sp>.collinearity file and the run scope specified by ACER_SPECIES and ACER_WGT_WORK_PATH.
输出 | Outputs:
- 标准输出中的制表统计结果，便于快速检查原始共线性结果规模。
- Tab-delimited summary lines printed to standard output for quick inspection of the raw collinearity results.
步骤 | Steps:
1. 读取物种列表和工作目录。 / Read the species list and work directory.
2. 逐个解析 .collinearity 文件中的区块与基因对。 / Parse blocks and gene pairs from each .collinearity file.
3. 输出每个物种的统计摘要。 / Print one summary line per species.
"""

from path_config import get_species_list, get_wgt_work_path


def stat_mcscanx_collinearity(sp, work_path):
    prefix = f"{sp}_{sp}"
    count_block = 0
    count_gene = 0
    count_gene_pair = 0
    gene_list = []
    with open(f"{work_path}/0_mcscanx_output/{prefix}/{prefix}.collinearity", "r", encoding="utf-8") as fr:
        for line in fr:
            if line.startswith("## Alignment"):
                count_block += 1
            elif line.startswith("#"):
                pass
            else:
                count_gene_pair += 1
                gene_id1 = line.split()[2]
                if gene_id1 not in gene_list:
                    gene_list.append(gene_id1)
                    count_gene += 1
                gene_id2 = line.split()[3]
                if gene_id2 not in gene_list:
                    gene_list.append(gene_id2)
                    count_gene += 1
    print(f"{sp}\t{count_block}\t{count_gene_pair}\t{count_gene}")


def main():
    sp_list = get_species_list()
    work_path = get_wgt_work_path()
    for sp in sp_list:
        stat_mcscanx_collinearity(sp, work_path)


if __name__ == "__main__":
    main()
