<h1> multiqc </h1>h
multiqc.py enables NGS file analysis (i.e. fastqc and multiqc) in python environment for windows client.

To install follow the Windows + WSL setup notes (run once):
In Windows CMD (Admin), install wsl at Power Shell prompt:
  wsl --install
  Install Ubuntu, from “Microsoft Store” in start menu. Just look for ubuntu, rather than any specific version.

Reboot, open Ubuntu (WSL) terminal, then install STAR and FASTQC:
  sudo apt update
  sudo apt install rna-star fastqc

(Optional) Build STAR index (example; quote paths with spaces):
  STAR --runMode genomeGenerate \
    --genomeDir "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/star_transcriptome_index" \
    --genomeFastaFiles "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/gencode_v47_transcripts.fasta" \
    --runThreadN 8

MultiQC is run at python terminal to install multiqc:
  pip install multiqc

The function runs fastqc or rna-star in linux/ubuntu environment, and then uses mutiqc to integrate all the results.

The main function runs multiqc on data files after either fastqc or rna-star analysis:
The command is : process_sample_groups_from_csv(base_dir, csv_path, output_base_dir, star_index,
run_alignment_flag, run_fastqc_flag, threads_fastqc=4,  threads_star=8)
 where:
 base_dir is directory with data file
 scv_path is input file with file names and a column for grouping
 output_base_dir is output directory
 star_index contais the genome data from ran-star
 run_alignment_flag (T/F) enables alignment with genome using STAR
 run_fastqc_flag (T/F) enables fastqc analysis
 threads_fastqc specifies number of cores used for fastqc analysis
 treads_star is number of processors used for rna-star alignment.
