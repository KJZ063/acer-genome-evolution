"""
用途 | Purpose:
- 将保留的 2-copy、3-copy 组与人工筛回的基因对合并，重建最终同源基因组结果。
- Merge the retained 2-copy and 3-copy groups with manually rescued pairs to reconstruct the final paralog groups.
输入 | Inputs:
- 5_filtered_paralogs/ 中的 2-copy、3-copy 结果，以及 6_pairs_from_other_paralogs/filtered_<sp>_pairs.csv。
- The 2-copy and 3-copy results in 5_filtered_paralogs/ plus 6_pairs_from_other_paralogs/filtered_<sp>_pairs.csv.
输出 | Outputs:
- 7_final_paralogs/ 下的 2-copy、3-copy 与 other 最终结果文件。
- Final 2-copy, 3-copy, and other result files under 7_final_paralogs/.
步骤 | Steps:
1. 读取已保留和补回的基因对。 / Read the retained and rescued gene pairs.
2. 用图连通分量重建最终分组。 / Rebuild the final groups with graph connected components.
3. 按拷贝数分类输出结果。 / Export the groups by copy-number class.
"""

import networkx as nx

from path_config import ensure_dir, get_species_list, get_wgt_work_path


def get_paralogs_from_filtered_pairs(sp, work_path):
    # 创建最终结果目录 / Create the final-output directory
    ensure_dir(f"{work_path}/7_final_paralogs")

    gene_pairs = []
    two_paralogs = []
    three_paralogs = []
    other_paralogs = []

    # 读取 2-copy 同源基因组 / Read the 2-copy paralog groups
    with open(f"{work_path}/5_filtered_paralogs/{sp}_2_paralogs.csv", "r") as fr:
        for line in fr:
            gene1 = line.split(",")[0].strip()
            gene2 = line.split(",")[1].strip()
            gene_pairs.append(sorted([gene1, gene2]))

    # 读取筛回的基因对 / Read the rescued gene pairs
    with open(f"{work_path}/6_pairs_from_other_paralogs/filtered_{sp}_pairs.csv", "r") as fr:
        for line in fr:
            gene1 = line.split(",")[0].strip()
            gene2 = line.split(",")[1].strip()
            gene_pairs.append(sorted([gene1, gene2]))

    # 读取 3-copy 同源基因组 / Read the 3-copy paralog groups
    with open(f"{work_path}/5_filtered_paralogs/{sp}_3_paralogs.csv", "r") as fr:
        for line in fr:
            genes = line.strip().split(",")
            three_paralogs.append(sorted(genes))

    # 根据保留和补回的基因对重建连通分量 / Rebuild connected components from retained and rescued pairs
    G = nx.Graph()
    G.add_edges_from(gene_pairs)
    connected_components = list(nx.connected_components(G))

    # 按拷贝数分类输出组别 / Split groups by copy number
    for cc in connected_components:
        if len(cc) == 2:
            two_paralogs.append(cc)
        elif len(cc) == 3:
            three_paralogs.append(cc)
        else:
            other_paralogs.append(cc)

    # 输出当前物种统计摘要 / Print the summary for the current species
    print(f"{sp}\t{len(two_paralogs)}\t{len(three_paralogs)}\t{len(other_paralogs)}")
    print(other_paralogs)

    data_files = [("2", two_paralogs), ("3", three_paralogs), ("other", other_paralogs)]
    for prefix, paralogs in data_files:
        with open(f"{work_path}/7_final_paralogs/{sp}_{prefix}_paralogs.csv", "w") as fw:
            if paralogs != []:
                for paralog in sorted(paralogs, key=lambda x: sorted(list(x))):
                    fw.write(",".join(sorted(list(paralog))) + "\n")


def main():
    work_path = get_wgt_work_path()
    sp_list = get_species_list()
    for sp in sp_list:
        get_paralogs_from_filtered_pairs(sp, work_path)


if __name__ == "__main__":
    main()
