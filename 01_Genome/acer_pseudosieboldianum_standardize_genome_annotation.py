"""
用途 | Purpose:
- 标准化 Acer pseudosieboldianum（Apse）的基因组注释与序列命名，生成发布版 GFF3、genome、CDS、pep 及 ID 映射表。
- Standardize the annotation and sequence naming for Acer pseudosieboldianum (Apse) and generate release-ready GFF3, genome, CDS, peptide files, and ID mapping tables.
输入 | Inputs:
- 原始 GFF3、genome FASTA、CDS FASTA、pep FASTA；默认从脚本目录下 inputs 读取，也可通过 GENOME_DATA_ROOT 指定输入根目录。
- Original GFF3, genome FASTA, CDS FASTA, and peptide FASTA files; the script reads from inputs by default or from the root directory specified by GENOME_DATA_ROOT.
输出 | Outputs:
- ../015_replace/ 中的 seqid、gene、mRNA 映射表。
- Standardized mapping tables in ../015_replace/.
- ../011_genome/、../012_gff/、../013_cds/、../014_pep/ 中的全量文件与 chr-only 子集文件。
- Full and chr-only standardized files in ../011_genome/, ../012_gff/, ../013_cds/, and ../014_pep/.
步骤 | Steps:
1. 建立 seqid 重命名表。 / Build the seqid rename table.
2. 重写 genome FASTA，并拆分全量与 chr-only 输出。 / Rewrite the genome FASTA and split full and chr-only outputs.
3. 按基因位置生成 gene 与 mRNA 命名映射。 / Generate gene and mRNA naming maps by genomic position.
4. 重写 GFF3、CDS 和蛋白序列文件，并输出对应映射表。 / Rewrite GFF3, CDS, and peptide files and export the related mapping tables.
"""

import time

import os
from pathlib import Path

# Resolve public input paths / 解析公开发布用输入路径
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ["GENOME_DATA_ROOT"]).expanduser() if os.environ.get("GENOME_DATA_ROOT") else SCRIPT_DIR / "inputs"


def resolve_input_path(*parts):
    return str((DATA_ROOT.joinpath(*parts)).resolve())

# Species code / 物种缩写
sp = "Apse"
# Output mapping files / 输出映射文件
file_output_seqid_replace = f"../015_replace/{sp}.seqid_replace.txt"
file_output_gene_replace = f"../015_replace/{sp}.gene_replace.txt"
file_output_mrna_replace = f"../015_replace/{sp}.mrna_replace.txt"
# Input and output GFF3 / 输入输出 GFF3
file_input_gff3 = resolve_input_path("Apse", "original", "Apse.original.gff3")
file_output_gff3 = f"../012_gff/all/{sp}.gff3"
file_output_gff3_chr = f"../012_gff/chr_only/{sp}_chr.gff3"
# Input and output genome / 输入输出基因组
file_input_genome = resolve_input_path("Apse", "original", "Apse.original.genome.fa")
file_output_genome = f"../011_genome/all/{sp}.genome.fa"
file_output_genome_chr = f"../011_genome/chr_only/{sp}_chr.genome.fa"
# Input and output CDS / 输入输出 CDS
file_input_cds = resolve_input_path("Apse", "original", "Apse.original.cds.fa")
file_output_cds = f"../013_cds/primary/{sp}.cds.fa"
file_output_cds_chr = f"../013_cds/chr_only/{sp}_chr.cds.fa"
# Input and output peptides / 输入输出蛋白序列
file_input_pep = resolve_input_path("Apse", "original", "Apse.original.pep.fa")
file_output_pep = f"../014_pep/primary/{sp}.pep.fa"
file_output_pep_chr = f"../014_pep/chr_only/{sp}_chr.pep.fa"

# Build seqid rename map / 构建 seqid 重命名表
print(f"Building seq_id replace list.")
seqid_list = []
index_seqid = 0
index_scaffold = 0
seqid_replace_dict = {}
seq_length = {}
with open(file_input_genome, "r") as fr:
    for line in fr:
        if line.startswith(">"):
            old_seqid = line.strip().split()[0].replace(">", "")
            seq_len = line.strip().split()[-1].replace("Len=", "")
            seq_length[old_seqid] = seq_len
            seqid_list.append(old_seqid)
fw = open(file_output_seqid_replace, "w")
for seqid in sorted(seqid_list):
    i = int(seqid.replace("GWHBECT000000", ""))
    if i < 14:
        new_seqid = f"{sp}{str(i).zfill(2)}"
    else:
        new_seqid = f"{sp}_scaffold{str(i).zfill(3)}"
    seqid_replace_dict[seqid] = new_seqid
    fw.write(f"{new_seqid}\t{seqid}\t{seq_length[seqid]}\n")
fw.close()

# Read and rewrite genome / 读取并重写基因组
genome_dict = {}
with open(file_input_genome, "r") as fr:
    seqid = None
    sequence_lines = []
    for line in fr:
        if line.startswith("#") or line.strip() == "":
            continue
        if line.startswith(">"):
            if seqid is not None:
                genome_dict[seqid] = ''.join(sequence_lines)
                sequence_lines = []
            seqid = seqid_replace_dict[line[1:].strip().split("\t")[0]]
            print(f"Processing {seqid}")
        else:
            sequence_lines.append(line.strip())
    if seqid is not None:
        genome_dict[seqid] = ''.join(sequence_lines)

line_length = 70
fw = open(file_output_genome, "w")
fw_chr = open(file_output_genome_chr, "w")
for seqid in sorted(genome_dict.keys()):
    count_bp = 0
    print(f"Writing {seqid}.")
    parts = [genome_dict[seqid][i:i + line_length] for i in range(0, len(genome_dict[seqid]), line_length)]
    fw.write(f">{seqid}\n")
    fw.write("\n".join(parts) + "\n")
    if "scaffold" not in seqid:
        fw_chr.write(f">{seqid}\n")
        fw_chr.write("\n".join(parts) + "\n")
fw.close()
fw_chr.close()

# Build gene rename map by start position / 按起始位置构建基因重命名表
print(f"Building gene_id replace list.")
gene_dict = {}
gene_replace_dict = {}
fw = open(file_output_gene_replace, "w")
print(f"Reading {file_input_gff3}.")
with open(file_input_gff3, "r") as fr:
    for line in fr:
        if line.startswith("#") or line.strip() == "":
            continue
        else:
            items = line.strip().split("\t")
            seqid = seqid_replace_dict[items[0]]
            type = items[2]
            start_pos = items[3]
            old_gene_id = items[-1].split(";")[1].replace("Accession=", "")
            if seqid not in gene_dict.keys():
                gene_dict[seqid] = {}
            if type == "gene":
                while start_pos in gene_dict[seqid].keys():
                    start_pos = str(int(start_pos) + 1)
                else:
                    gene_dict[seqid][start_pos] = old_gene_id
for seqid in sorted(gene_dict.keys()):
    gene_count = 0
    if "scaffold" in seqid:
        index_seqid = seqid.replace(f"{sp}_scaffold", "")
        prefix = f"{sp}{index_seqid}S"
    else:
        prefix = f"{seqid}G"
    for start_pos in sorted(gene_dict[seqid].keys(), key=int):
        gene_count += 1
        new_gene_id = f"{prefix}{str(gene_count * 10).zfill(6)}"
        fw.write(f"{new_gene_id}\t{gene_dict[seqid][start_pos]}\n")
        gene_replace_dict[gene_dict[seqid][start_pos]] = new_gene_id
fw.close()

# Rewrite GFF3 and chr-only GFF3 / 重写 GFF3 与 chr-only GFF3
print(f"Reformatting gff3 files.")
fw = open(file_output_gff3, "w")
fw_chr = open(file_output_gff3_chr, "w")
mrna_replace_dict = {}
tab = "\t"
with open(file_input_gff3, "r") as fr:
    for line in fr:
        if line.startswith("#") or line.strip() == "":
            pass
        else:
            write_line = ""
            items = line.strip().split("\t")
            seqid = seqid_replace_dict[items[0]]
            type = items[2]
            if type == "gene":
                old_gene_id = items[-1].split(";")[1].replace("Accession=", "")
                new_gene_id = gene_replace_dict[old_gene_id]
                write_line = f"{seqid}\t{tab.join(items[1:-1])}\tID={new_gene_id}\n"
            elif type == "mRNA":
                old_mrna_id = items[-1].split(";")[1].replace("Accession=", "")
                suffix = items[-1].split(";")[0].split(".")[-1]
                new_mrna_id = f"{new_gene_id}.{suffix}"
                mrna_replace_dict[old_mrna_id] = new_mrna_id
                write_line = f"{seqid}\t{tab.join(items[1:-1])}\tID={new_mrna_id};Parent={new_gene_id}\n"
            else:
                suffix = items[-1].split(";")[0].replace("ID=", "").split("-")[0]
                write_line = f"{seqid}\t{tab.join(items[1:-1])}\tID={new_mrna_id}.{suffix};Parent={new_mrna_id}\n"
            if "scaffold" in seqid:
                fw.write(write_line)
            else:
                fw.write(write_line)
                fw_chr.write(write_line)
fw.close()
fw_chr.close()

# Write mRNA rename list / 写出 mRNA 重命名表
fw = open(file_output_mrna_replace, "w")
for old_mrna_id in sorted(mrna_replace_dict.keys()):
    new_mrna_id = mrna_replace_dict[old_mrna_id]
    fw.write(f"{new_mrna_id}\t{old_mrna_id}\n")
fw.close()

# Rewrite CDS / 重写 CDS
print(f"Reformatting cds files.")
cds_dict = {}
line_length = 70
fw = open(file_output_cds, "w")
fw_chr = open(file_output_cds_chr, "w")
with open(file_input_cds, "r") as fr:
    for line in fr:
        if line.startswith(">"):
            mrna_id = line.split()[0].strip().replace(">", "")
            if mrna_id not in mrna_replace_dict.keys():
                print(f"error: {mrna_id} 不在 gff 列表中。")
            else:
                cds_id = mrna_replace_dict[mrna_id]
                cds_dict[cds_id] = ""
        else:
            cds_dict[cds_id] += line.strip()
for cds_id in sorted(cds_dict.keys()):
    parts = [cds_dict[cds_id][i:i + line_length] for i in range(0, len(cds_dict[cds_id]), line_length)]
    fw.write(f">{cds_id}\n")
    fw.write("\n".join(parts) + "\n")
    if "G" in cds_id:
        fw_chr.write(f">{cds_id}\n")
        fw_chr.write("\n".join(parts) + "\n")
fw.close()
fw_chr.close()

# Rewrite peptides / 重写蛋白序列
print(f"Reformatting pep files.")
pep_dict = {}
line_length = 70
fw = open(file_output_pep, "w")
fw_chr = open(file_output_pep_chr, "w")
with open(file_input_pep, "r") as fr:
    for line in fr:
        if line.startswith(">"):
            mrna_id = line.split()[1].strip().replace("mRNA=", "")
            if mrna_id not in mrna_replace_dict.keys():
                print(f"error: {mrna_id} 不在 gff 列表中。")
            else:
                pep_id = mrna_replace_dict[mrna_id]
                pep_dict[pep_id] = ""
        else:
            pep_dict[pep_id] += line.strip().replace("*", "X")
for pep_id in sorted(pep_dict.keys()):
    parts = [pep_dict[pep_id][i:i + line_length] for i in range(0, len(pep_dict[pep_id]), line_length)]
    fw.write(f">{pep_id}\n")
    fw.write("\n".join(parts) + "\n")
    if "G" in pep_id:
        fw_chr.write(f">{pep_id}\n")
        fw_chr.write("\n".join(parts) + "\n")
fw.close()
fw_chr.close()



