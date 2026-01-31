<h1> multiqc </h1>
<p></p>multiqc.py enables NGS file analysis (i.e. fastqc and multiqc) in python environment for windows client.</p>
To install follow the Windows + WSL setup notes (run once):<br />
In Windows CMD (Admin), install wsl at Power Shell prompt:<br />
   wsl --install<br />
   <p>Install Ubuntu, from “Microsoft Store” in start menu. Just look for ubuntu, rather than any specific version.</p>
Reboot, open Ubuntu (WSL) terminal, then install STAR and FASTQC:br />
  sudo apt update<br />
  sudo apt install rna-star fastqc<br />
<p> </p>
(Optional) Build STAR index (example; quote paths with spaces):<br />
  STAR --runMode genomeGenerate \<br />
    --genomeDir "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/star_transcriptome_index" \<br />
    --genomeFastaFiles "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/gencode_v47_transcripts.fasta" \<br />
    --runThreadN 8<br />

<p>MultiQC is run at python terminal to install multiqc:</p>
<p>  </p>pip install multiqc</p>
<p> </p>
<p></p>The function runs fastqc or rna-star in linux/ubuntu environment, and then uses mutiqc to integrate all the results.</p>
<p>The main function runs multiqc on data files after either fastqc or rna-star analysis:</p>
<p>The command is : process_sample_groups_from_csv(base_dir, csv_path, output_base_dir, star_index, run_alignment_flag, run_fastqc_flag, threads_fastqc=4,  threads_star=8)
<p>where:</p>
<b>base_dir</b> is directory with data file<br />
<b>scv_path</b> is input file with file names and a column for grouping<br />
<b>output_base_dir</b> is output directory<br />
<b>star_index</b> contains the genome data from ran-star<br />
<b>run_alignment_flag</b> (T/F) enables alignment with genome using STAR<br />
<b>run_fastqc_flag (T/F)</b> enables fastqc analysis<br />
<b>threads_fastqc</b> specifies number of cores used for fastqc analysis<br />
<b>treads_star</b> is number of processors used for rna-star alignment.<br />
