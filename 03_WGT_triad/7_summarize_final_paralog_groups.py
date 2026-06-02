"""
用途 | Purpose:
- 统计每个物种最终 2-copy 和 3-copy 同源基因组涉及的唯一基因数量。
- Count the number of unique genes represented in the final 2-copy and 3-copy paralog groups for each species.
输入 | Inputs:
- 7_final_paralogs/<sp>_2_paralogs.csv 与 7_final_paralogs/<sp>_3_paralogs.csv。
- 7_final_paralogs/<sp>_2_paralogs.csv and 7_final_paralogs/<sp>_3_paralogs.csv.
输出 | Outputs:
- 标准输出中的统计表头与每个物种的结果行。
- A header line and one result line per species printed to standard output.
步骤 | Steps:
1. 读取每个物种的 2-copy 与 3-copy 结果。 / Read the 2-copy and 3-copy results for each species.
2. 去重统计参与基因。 / Count unique participating genes.
3. 输出汇总表。 / Print the summary table.
"""

from path_config import get_species_list, get_wgt_work_path


def paralog_stat(sp_list, work_path):
    sp_dict = {}
    for sp in sp_list:
        sp_dict[sp] = {"2": [], "3": []}
        with open(f"{work_path}/7_final_paralogs/{sp}_2_paralogs.csv", "r", encoding="utf-8") as fr:
            for line in fr:
                genes = line.strip().split(",")
                for gene in genes:
                    if gene not in sp_dict[sp]["2"]:
                        sp_dict[sp]["2"].append(gene)
        with open(f"{work_path}/7_final_paralogs/{sp}_3_paralogs.csv", "r", encoding="utf-8") as fr:
            for line in fr:
                genes = line.strip().split(",")
                for gene in genes:
                    if gene not in sp_dict[sp]["3"]:
                        sp_dict[sp]["3"].append(gene)

    print("sp\t2_paralogs\t3_paralogs")
    for sp in sorted(sp_list):
        print(f"{sp}\t{len(sp_dict[sp]['2'])}\t{len(sp_dict[sp]['3'])}")


def main():
    paralog_stat(get_species_list(), get_wgt_work_path())


if __name__ == "__main__":
    main()
