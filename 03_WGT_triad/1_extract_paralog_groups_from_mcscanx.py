"""
用途 | Purpose:
- 从 MCScanX HTML 结果中提取每个物种的同源基因组，并同时导出唯一基因对列表。
- Extract paralog groups for each species from MCScanX HTML results and export the unique gene-pair list at the same time.
输入 | Inputs:
- mcscanx_output/<sp>_<sp>/<sp>_<sp>.html/ 目录中的 HTML 结果文件。
- HTML result files under mcscanx_output/<sp>_<sp>/<sp>_<sp>.html/.
输出 | Outputs:
- <sp>_<sp>_paralog.csv 与 <sp>_<sp>_gene_pair.tsv。
- <sp>_<sp>_paralog.csv and <sp>_<sp>_gene_pair.tsv.
步骤 | Steps:
1. 扫描 HTML 结果目录。 / Scan the HTML result directory.
2. 识别每个结果条目中的唯一基因集合。 / Identify the unique gene set in each result entry.
3. 输出同源基因组和去重后的基因对。 / Write the paralog groups and de-duplicated gene pairs.
"""

import re
import os

from path_config import get_species_list, get_wgt_work_path


def mcscanx_html2paralog(sp, work_path):
    prefix = f"{sp}_{sp}"
    pair_list = []
    paralog_list = []
    unique_gene_list = []
    paralog_count = {"2": 0, "3": 0, "other": 0}
    fw_paralog = open(f"{work_path}/{prefix}_paralog.csv", "w", encoding="utf-8")
    fw_pair = open(f"{work_path}/{prefix}_gene_pair.tsv", "w", encoding="utf-8")
    for root, dirs, files in os.walk(f"{work_path}/mcscanx_output/{prefix}/{prefix}.html/"):
        for file in files:
            file_path = f"{work_path}/mcscanx_output/{prefix}/{prefix}.html/{file}"
            with open(file_path, "r", encoding="utf-8") as fr:
                for line in fr.readlines()[1:]:
                    gene_list = []
                    paralog = []
                    items = re.split("<|>", line)
                    for gene in items:
                        if sp in gene:
                            if gene not in gene_list:
                                gene_list.append(gene)
                                paralog.append(gene)
                    if len(paralog) > 1:
                        paralog = sorted(paralog)
                        if paralog not in paralog_list:
                            paralog_list.append(paralog)
                            fw_paralog.write(",".join(paralog) + "\n")
                            for i in range(len(paralog)):
                                for j in range(i + 1, len(paralog)):
                                    # 每个唯一基因对只输出一次 / Write each unique gene pair once
                                    pair = sorted([paralog[i], paralog[j]])
                                    if pair not in pair_list:
                                        pair_list.append(pair)
                                        fw_pair.write("\t".join(pair) + "\n")
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
    fw_paralog.close()
    fw_pair.close()


def main():
    sp_list = get_species_list()
    work_path = get_wgt_work_path()
    for sp in sp_list:
        mcscanx_html2paralog(sp, work_path)


if __name__ == "__main__":
    main()
