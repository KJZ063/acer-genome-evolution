"""
用途 | Purpose:
- 从 other 同源基因组中提取所有唯一基因对，并生成后续点图检查所需的 BLAST 与配置文件。
- Extract all unique gene pairs from the other paralog groups and generate the BLAST and dotplot configuration files needed for downstream inspection.
输入 | Inputs:
- 5_filtered_paralogs/<sp>_other_paralogs.csv、全基因组 BLAST、WGDI 的 gff 与 lens 文件。
- 5_filtered_paralogs/<sp>_other_paralogs.csv, the genome-wide BLAST file, and WGDI gff/lens files.
输出 | Outputs:
- 6_pairs_from_other_paralogs/ 下的 pair 列表、裁剪 BLAST 和 dotplot 配置文件。
- Pair lists, sliced BLAST files, and dotplot configuration files under 6_pairs_from_other_paralogs/.
步骤 | Steps:
1. 汇总 other 组中的唯一基因对。 / Collect the unique gene pairs from the other groups.
2. 从全量 BLAST 结果中裁剪对应记录。 / Slice the matching records from the full BLAST file.
3. 写出 pair 级和全基因组级 dotplot 配置。 / Write pair-level and genome-wide dotplot configurations.
"""

import os

from path_config import (
    ensure_dir,
    get_blast_dir,
    get_species_list,
    get_wgdi_gff_dir,
    get_wgdi_lens_dir,
    get_wgt_work_path,
    relative_to_file,
)


def get_pairs_from_other_paralogs(sp, work_path, blast_dir, gff_dir, lens_dir):
    # 创建当前步骤输出目录 / Create the output directory for this step
    pair_dir = ensure_dir(f"{work_path}/6_pairs_from_other_paralogs")

    # 汇总 other 组中的唯一基因对 / Collect the unique gene pairs from other groups
    pair_list = []
    pair_csv = os.path.join(pair_dir, f"{sp}_pairs.csv")
    with open(pair_csv, "w", encoding="utf-8") as fw_pair:
        with open(f"{work_path}/5_filtered_paralogs/{sp}_other_paralogs.csv", "r", encoding="utf-8") as fr:
            for line in fr:
                paralog = line.strip().split(",")
                for i in range(len(paralog)):
                    for j in range(i + 1, len(paralog)):
                        pair = sorted([paralog[i], paralog[j]])
                        if pair not in pair_list:
                            pair_list.append(pair)
        for pair in sorted(pair_list):
            fw_pair.write(",".join(pair) + "\n")

    # 从全量 BLAST 结果中裁剪对应记录 / Slice the matching records from the full BLAST file
    pair_blast = os.path.join(pair_dir, f"{sp}_pairs.blast")
    blast_file = os.path.join(blast_dir, f"{sp}_chr.{sp}_chr_1e-5_top5.blast")
    with open(pair_blast, "w", encoding="utf-8") as fw_blast:
        with open(blast_file, "r", encoding="utf-8") as fr:
            for line in fr:
                gene_pair = sorted([line.split("\t")[0], line.split("\t")[1]])
                if gene_pair in pair_list:
                    fw_blast.write(line)

    gff_file = os.path.join(gff_dir, f"{sp}.gff")
    lens_file = os.path.join(lens_dir, f"{sp}.lens")

    # 写出 pair 级 dotplot 配置 / Write the pair-level dotplot configuration
    pair_conf = os.path.join(pair_dir, f"{sp}_pairs_dotplot.conf")
    with open(pair_conf, "w", encoding="utf-8") as fw_conf:
        fw_conf.write("[dotplot]\n")
        fw_conf.write(f"blast = {relative_to_file(pair_blast, pair_conf)}\n")
        fw_conf.write("blast_reverse = false\n")
        fw_conf.write(f"gff1 = {relative_to_file(gff_file, pair_conf)}\n")
        fw_conf.write(f"gff2 = {relative_to_file(gff_file, pair_conf)}\n")
        fw_conf.write(f"lens1 = {relative_to_file(lens_file, pair_conf)}\n")
        fw_conf.write(f"lens2 = {relative_to_file(lens_file, pair_conf)}\n")
        fw_conf.write(f"genome1_name = {sp}\n")
        fw_conf.write(f"genome2_name = {sp}\n")
        fw_conf.write("multiple = 1\n")
        fw_conf.write("score = 100\n")
        fw_conf.write("evalue = 1e-5\n")
        fw_conf.write("repeat_number = 10\n")
        fw_conf.write("position = order\n")
        fw_conf.write("ancestor_left = none\n")
        fw_conf.write("ancestor_top = none\n")
        fw_conf.write("markersize = 2\n")
        fw_conf.write("figsize = 10,10\n")
        fw_conf.write(f"savefig = {relative_to_file(os.path.join(pair_dir, f'{sp}_pairs_dotplot.png'), pair_conf)}\n")

    # 写出全基因组 dotplot 配置 / Write the genome-wide dotplot configuration
    all_conf = os.path.join(pair_dir, f"{sp}_dotplot.conf")
    with open(all_conf, "w", encoding="utf-8") as fw_conf:
        fw_conf.write("[dotplot]\n")
        fw_conf.write(f"blast = {relative_to_file(blast_file, all_conf)}\n")
        fw_conf.write("blast_reverse = false\n")
        fw_conf.write(f"gff1 = {relative_to_file(gff_file, all_conf)}\n")
        fw_conf.write(f"gff2 = {relative_to_file(gff_file, all_conf)}\n")
        fw_conf.write(f"lens1 = {relative_to_file(lens_file, all_conf)}\n")
        fw_conf.write(f"lens2 = {relative_to_file(lens_file, all_conf)}\n")
        fw_conf.write(f"genome1_name = {sp}\n")
        fw_conf.write(f"genome2_name = {sp}\n")
        fw_conf.write("multiple = 1\n")
        fw_conf.write("score = 100\n")
        fw_conf.write("evalue = 1e-5\n")
        fw_conf.write("repeat_number = 10\n")
        fw_conf.write("position = order\n")
        fw_conf.write("ancestor_left = none\n")
        fw_conf.write("ancestor_top = none\n")
        fw_conf.write("markersize = 2\n")
        fw_conf.write("figsize = 10,10\n")
        fw_conf.write(f"savefig = {relative_to_file(os.path.join(pair_dir, f'{sp}_dotplot.png'), all_conf)}\n")


def main():
    work_path = get_wgt_work_path()
    blast_dir = get_blast_dir()
    gff_dir = get_wgdi_gff_dir()
    lens_dir = get_wgdi_lens_dir()
    sp_list = get_species_list()
    for sp in sp_list:
        get_pairs_from_other_paralogs(sp, work_path, blast_dir, gff_dir, lens_dir)


if __name__ == "__main__":
    main()
