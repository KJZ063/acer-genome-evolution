"""
用途 | Purpose:
- 为每个物种生成 WGDI Ks 计算配置文件，连接 CDS、pep 与基因对输入。
- Generate WGDI Ks configuration files for each species by linking CDS, peptide, and gene-pair inputs.
输入 | Inputs:
- 染色体级 CDS、pep 文件，以及 <sp>_<sp>_gene_pair.tsv。
- Chromosome-level CDS and peptide files plus <sp>_<sp>_gene_pair.tsv.
输出 | Outputs:
- conf/<sp>_gamma_2_ks.conf。
- conf/<sp>_gamma_2_ks.conf.
步骤 | Steps:
1. 解析工作目录与序列目录。 / Resolve the work and sequence directories.
2. 为当前物种写入 WGDI Ks 配置字段。 / Write the WGDI Ks configuration entries for the current species.
3. 将结果保存到 conf/。 / Save the result under conf/.
"""

import os

from path_config import (
    ensure_dir,
    get_cds_dir,
    get_pep_dir,
    get_species_list,
    get_wgt_work_path,
    relative_to_file,
)


def create_wgdi_ks_conf(sp, cds_path, pep_path, work_path):
    cds_file = os.path.join(cds_path, f"{sp}_chr.cds.fa")
    pep_file = os.path.join(pep_path, f"{sp}_chr.pep.fa")
    conf_path = ensure_dir(os.path.join(work_path, "conf"))
    result_path = ensure_dir(os.path.join(work_path, "wgdi_ks_output"))
    conf_file = os.path.join(conf_path, f"{sp}_gamma_2_ks.conf")
    with open(conf_file, "w", encoding="utf-8") as fw_2:
        fw_2.write("[ks]\n")
        fw_2.write(f"cds_file = {relative_to_file(cds_file, conf_file)}\n")
        fw_2.write(f"pep_file = {relative_to_file(pep_file, conf_file)}\n")
        fw_2.write("align_software = mafft\n")
        fw_2.write(
            f"pairs_file = {relative_to_file(os.path.join(work_path, f'{sp}_{sp}_gene_pair.tsv'), conf_file)}\n"
        )
        fw_2.write(f"ks_file = {relative_to_file(os.path.join(result_path, f'{sp}_ks.tsv'), conf_file)}")


def main():
    sp_list = get_species_list()
    cds_path = get_cds_dir()
    pep_path = get_pep_dir()
    work_path = get_wgt_work_path()
    for sp in sp_list:
        create_wgdi_ks_conf(sp, cds_path, pep_path, work_path)


if __name__ == "__main__":
    main()
