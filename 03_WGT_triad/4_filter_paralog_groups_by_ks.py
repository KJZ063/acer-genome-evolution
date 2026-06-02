"""
用途 | Purpose:
- 结合 Ks 范围和 BLAST 支持度，筛选 2-copy、3-copy 与 other 同源基因组。
- Filter 2-copy, 3-copy, and other paralog groups by combining a Ks range with BLAST support.
输入 | Inputs:
- WGDI Ks 结果、BLAST 结果，以及最长同源基因组列表。
- WGDI Ks results, BLAST results, and the longest-paralog list.
输出 | Outputs:
- 5_filtered_paralogs/ 下的 2-copy、3-copy 与 other 分组文件。
- The 2-copy, 3-copy, and other group files under 5_filtered_paralogs/.
步骤 | Steps:
1. 建立 Ks 与 BLAST 的基因对查询表。 / Build gene-pair lookup tables for Ks and BLAST.
2. 按阈值筛选可保留的基因对。 / Filter retainable gene pairs by threshold.
3. 用图连通分量重建分组并输出分类结果。 / Rebuild groups with graph connected components and export the classified results.
"""

import networkx as nx
import os

from path_config import ensure_dir, get_blast_dir, get_species_list, get_wgt_work_path


def filter_paralog_by_ks(sp, work_path, blast_dir, ks_range, blast_score_min):
    # 创建当前步骤输出目录 / Create the output directory for this step
    ensure_dir(f"{work_path}/5_filtered_paralogs")

    # 构建 Ks 查询表 / Build the Ks lookup table
    ks_dict = {}
    with open(f"{work_path}/4_wgdi_ks_output/{sp}_ks.tsv", "r") as fr:
        for line in fr.readlines()[1:]:
            gene_id1 = line.strip().split("\t")[0]
            gene_id2 = line.strip().split("\t")[1]
            ks = line.strip().split("\t")[-1]
            pair = ",".join(sorted([gene_id1, gene_id2]))
            if pair not in ks_dict.keys():
                ks_dict[pair] = ks
    print(f"{sp} ks pair dict finished.")

    # 收集 BLAST 支持的基因对 / Collect BLAST-supported gene pairs
    blast_pairs = []
    blast_file = os.path.join(blast_dir, f"{sp}_chr.{sp}_chr_1e-5_top5.blast")
    with open(blast_file, "r") as fr:
        for line in fr:
            blast_pair = sorted([line.split("\t")[0], line.split("\t")[1]])
            blast_score = float(line.strip().split("\t")[-1])
            if blast_pair not in blast_pairs and blast_score >= blast_score_min:
                blast_pairs.append(blast_pair)
    print(f"{sp} blast pair list finished.")

    # 按 Ks 和 BLAST 条件收集基因对 / Collect gene pairs that pass the Ks and BLAST filters
    min_ks = ks_range[0]
    max_ks = ks_range[1]
    gene_pairs = []
    with open(f"{work_path}/1_longest_paralogs/{sp}_{sp}_longest_paralog.csv", "r") as fr:
        for line in fr:
            paralog = line.strip().split(",")
            for i in range(len(paralog)):
                for j in range(i + 1, len(paralog)):
                    pair = ",".join(sorted([paralog[i], paralog[j]]))
                    if min_ks < float(ks_dict.get(pair, 0)) < max_ks:
                        if sorted([paralog[i], paralog[j]]) in blast_pairs:
                            gene_pairs.append(sorted([paralog[i], paralog[j]]))
    print(f"{sp} filtered gene pairs finished.")

    # 根据保留基因对重建连通分量 / Rebuild connected components from the retained gene pairs
    G = nx.Graph()
    G.add_edges_from(gene_pairs)
    connected_components = list(nx.connected_components(G))

    # 按拷贝数和染色体位置分类 / Classify groups by copy number and chromosome location
    two_paralogs = []
    three_paralogs = []
    other_paralogs = []

    for cc in connected_components:
        chromosomes = {gene[4:6] for gene in cc}  # 染色体编号 / Chromosome tag
        if len(chromosomes) == len(cc):  # 位于不同染色体 / On distinct chromosomes
            if len(cc) == 2:
                two_paralogs.append(cc)
            elif len(cc) == 3:
                three_paralogs.append(cc)
            else:
                other_paralogs.append(cc)
        else:
            other_paralogs.append(cc)  # 同染色体的组合归入 other / Groups on the same chromosome are moved to other

    # 输出当前物种统计摘要 / Print the summary for the current species
    print(f"{sp}\t{len(two_paralogs)}\t{len(three_paralogs)}\t{len(other_paralogs)}")

    data_files = [("2", two_paralogs), ("3", three_paralogs), ("other", other_paralogs)]
    for prefix, paralogs in data_files:
        with open(f"{work_path}/5_filtered_paralogs/{sp}_{prefix}_paralogs.csv", "w") as fw:
            for paralog in sorted(paralogs):
                fw.write(",".join(sorted(paralog)) + "\n")


def main():
    work_path = get_wgt_work_path()
    blast_dir = get_blast_dir()
    sp_list = get_species_list()
    ks_range = [1.0, 2.8]
    blast_score_min = float(100)
    for sp in sp_list:
        filter_paralog_by_ks(sp, work_path, blast_dir, ks_range, blast_score_min)


if __name__ == "__main__":
    main()
