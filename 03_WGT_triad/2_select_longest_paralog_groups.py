"""
用途 | Purpose:
- 为每个基因保留其所在的最长同源基因组，并去除重复基因占用的较短组合。
- Keep the longest paralog group for each gene and remove shorter overlapping groups that reuse the same genes.
输入 | Inputs:
- <sp>_<sp>_paralog.csv。
- <sp>_<sp>_paralog.csv.
输出 | Outputs:
- conf/<sp>_<sp>_longest_paralog.csv。
- conf/<sp>_<sp>_longest_paralog.csv.
步骤 | Steps:
1. 读取原始同源基因组。 / Read the original paralog groups.
2. 标记每个基因所属的最长组合。 / Mark the longest group associated with each gene.
3. 输出去重后的最长组合列表。 / Write the filtered longest-group list.
"""

import csv

from path_config import ensure_dir, get_species_list, get_wgt_work_path


def get_longest_paralogs(sp, work_path):
    # 读取原始同源基因组 / Read the source paralog groups
    with open(f'{work_path}/{sp}_{sp}_paralog.csv', 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        paralogs = [row for row in reader]

    # 为每个基因记录最长组合 / Track the longest group linked to each gene
    gene_to_longest_paralog = {}

    # 优先保留最长同源基因组 / Prefer the longest paralog group
    for paralog in paralogs:
        for gene in paralog:
            if gene not in gene_to_longest_paralog or len(paralog) > len(gene_to_longest_paralog[gene]):
                gene_to_longest_paralog[gene] = paralog

    # 去除重复占用的基因 / Remove genes already assigned elsewhere
    unique_paralogs = []
    seen_genes = set()
    for paralog in paralogs:
        new_paralog = []
        for gene in paralog:
            if gene_to_longest_paralog[gene] == paralog:
                if gene not in seen_genes:
                    new_paralog.append(gene)
                    seen_genes.add(gene)
        if new_paralog:
            unique_paralogs.append(new_paralog)

    # 输出筛选后的同源基因组 / Write the filtered paralog groups
    paralog_count = {"2": 0, "3": 0, "other": 0}
    unique_gene_list = []
    ensure_dir(f"{work_path}/conf")
    with open(f'{work_path}/conf/{sp}_{sp}_longest_paralog.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        for paralog in unique_paralogs:
            if len(paralog) > 1:
                writer.writerow(paralog)
                if len(paralog) == 2:
                    paralog_count["2"] += 1
                    for gene in paralog:
                        if gene not in unique_gene_list:
                            unique_gene_list.append(gene)
                elif len(paralog) == 3:
                    paralog_count["3"] += 1
                    for gene in paralog:
                        if gene not in unique_gene_list:
                            unique_gene_list.append(gene)
                else:
                    paralog_count["other"] += 1
    print(f"{sp}\t{paralog_count['2']}\t{paralog_count['3']}\t{paralog_count['other']}\t{len(unique_gene_list)}")


def main():
    sp_list = get_species_list()
    work_path = get_wgt_work_path()
    for sp in sp_list:
        get_longest_paralogs(sp, work_path)


if __name__ == "__main__":
    main()
