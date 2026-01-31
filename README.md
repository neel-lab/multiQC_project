<h1> multiqc </h1>
<p></p>multiqc.py enables NGS file analysis (i.e. fastqc and multiqc) in python environment for windows client.</p>

<p>To install follow the Windows + WSL setup notes (run once):</p>
<p>In Windows CMD (Admin), install wsl at Power Shell prompt:</p>
<p> wsl --install</p>
<p>Install Ubuntu, from “Microsoft Store” in start menu. Just look for ubuntu, rather than any specific version.</p>
<p>Reboot, open Ubuntu (WSL) terminal, then install STAR and FASTQC:</p>
<p>  sudo apt update</p>
<p>  sudo apt install rna-star fastqc</p>

<p>(Optional) Build STAR index (example; quote paths with spaces):</p>p>
<p>  STAR --runMode genomeGenerate \</p>
    <p>--genomeDir "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/star_transcriptome_index" \</p>
    <p>--genomeFastaFiles "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/gencode_v47_transcripts.fasta" \</p>
    <p></p>--runThreadN 8</p>

<p>MultiQC is run at python terminal to install multiqc:</p>
<p>  </p>pip install multiqc</p>
<p> </p>
<p></p>The function runs fastqc or rna-star in linux/ubuntu environment, and then uses mutiqc to integrate all the results.</p>
<p>The main function runs multiqc on data files after either fastqc or rna-star analysis:</p>
<p>The command is : process_sample_groups_from_csv(base_dir, csv_path, output_base_dir, star_index, run_alignment_flag, run_fastqc_flag, threads_fastqc=4,  threads_star=8)
<p>where:</p>
base_dir is directory with data file
<p> scv_path is input file with file names and a column for grouping</p>
<p> output_base_dir is output directory</p>
<p> star_index contais the genome data from ran-star</p>
<p> run_alignment_flag (T/F) enables alignment with genome using STAR</p>
<p> run_fastqc_flag (T/F) enables fastqc analysis</p>
<p> threads_fastqc specifies number of cores used for fastqc analysis</p>
<p> treads_star is number of processors used for rna-star alignment.</p>
