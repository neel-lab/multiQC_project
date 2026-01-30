import subprocess
import os
import shutil

def run_alignment(sample_fastq_r1, sample_fastq_r2, output_dir, star_index, sample_name):
    """
    Run STAR alignment on paired-end fastq files.

    Args:
        sample_fastq_r1 (str): Path to R1 fastq.gz file.
        sample_fastq_r2 (str): Path to R2 fastq.gz file.
        output_dir (str): Directory to save STAR output.
        star_index (str): Path to STAR genome index.
        sample_name (str): Sample name for output prefix.
    """
    os.makedirs(output_dir, exist_ok=True)
    star_out_prefix = os.path.join(output_dir, sample_name + "_")

    cmd = [
        "STAR",
        "--runThreadN", "4",  # Adjust threads as needed
        "--genomeDir", star_index,
        "--readFilesIn", sample_fastq_r1, sample_fastq_r2,
        "--readFilesCommand", "zcat",
        "--outFileNamePrefix", star_out_prefix,
        "--outSAMtype", "BAM", "SortedByCoordinate",
        "--outSAMunmapped", "Within",
        "--outFilterMultimapNmax", "1",
        "--outReadsUnmapped", "Fastx"
    ]

    print(f"Running STAR alignment for {sample_name}...")
    subprocess.run(cmd, check=True)
    print(f"STAR alignment completed for {sample_name}.")

    return star_out_prefix + "Log.final.out"


def parse_star_log(log_path):
    """
    Parse STAR Log.final.out file to extract % uniquely mapped reads for R2.

    Args:
        log_path (str): Path to STAR Log.final.out file.

    Returns:
        dict: Dictionary with mapping stats.
    """
    stats = {}
    with open(log_path, 'r') as f:
        for line in f:
            if "Uniquely mapped reads %" in line:
                stats['Uniquely mapped reads %'] = line.strip().split('|')[1].strip()
            elif "Number of input reads" in line:
                stats['Number of input reads'] = line.strip().split('|')[1].strip()
            elif "Number of reads mapped to multiple loci" in line:
                stats['Multimapped reads'] = line.strip().split('|')[1].strip()
            elif "Number of reads mapped to too many loci" in line:
                stats['Too many loci reads'] = line.strip().split('|')[1].strip()
    return stats


def run_multiqc_on_group(files_to_analyze, output_dir):
    """
    Run MultiQC on a list of files.

    Args:
        files_to_analyze (list): List of file paths.
        output_dir (str): Directory to save MultiQC report.
    """
    os.makedirs(output_dir, exist_ok=True)
    cmd = ['multiqc', '-o', output_dir] + files_to_analyze
    print(f"Running MultiQC: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"MultiQC report generated in {output_dir}")


def process_sample_groups(base_dir, sample_prefix, sample_groups, output_base_dir, star_index=None, run_alignment_flag=False):
    """
    Process sample groups: optionally run alignment, then run MultiQC.

    Args:
        base_dir (str): Directory containing fastq files.
        sample_prefix (str): Common prefix of sample files.
        sample_groups (list of lists): Groups of sample IDs.
        output_base_dir (str): Base directory for outputs.
        star_index (str): Path to STAR genome index (required if run_alignment_flag=True).
        run_alignment_flag (bool): Whether to run alignment step.
    """
    for i, group in enumerate(sample_groups, start=1):
        print(f"\nProcessing group {i} with samples: {group}")
        files_to_analyze = []

        for sample_num in group:
            r1 = os.path.join(base_dir, f"{sample_prefix}_{sample_num}_L001_R1_001.fastq.gz")
            r2 = os.path.join(base_dir, f"{sample_prefix}_{sample_num}_L001_R2_001.fastq.gz")

            if not (os.path.exists(r1) and os.path.exists(r2)):
                print(f"Warning: Missing files for sample {sample_num}: {r1} or {r2}")
                continue

            if run_alignment_flag:
                align_out_dir = os.path.join(output_base_dir, f"group_{i}", sample_num, "star_alignment")
                log_file = run_alignment(r1, r2, align_out_dir, star_index, sample_num)
                stats = parse_star_log(log_file)
                print(f"Alignment stats for {sample_num}: {stats}")

                # Add alignment log to MultiQC input
                files_to_analyze.append(log_file)

            # Add raw fastq files for MultiQC
            files_to_analyze.extend([r1, r2])

        if not files_to_analyze:
            print(f"No files to analyze for group {i}. Skipping MultiQC.")
            continue

        multiqc_out_dir = os.path.join(output_base_dir, f"group_{i}", "multiqc_report")
        run_multiqc_on_group(files_to_analyze, multiqc_out_dir)


if __name__ == "__main__":
    base_dir = r"C:\Users\neel\Box\cbe-neel\cbe-neel-shared\DATA FOLDER\NGS data\SR010180"
    sample_prefix = "LIB131765_23GJLVLT4"
    sample_groups = [
        ['S1', 'S2'],          # Group 1
        ['S3'],                # Group 2 (single sample)
        ['S4', 'S5']           # Group 3
    ]
    output_base_dir = r"C:\Users\neel\Box\cbe-neel\cbe-neel-shared\DATA FOLDER\NGS data\SR010180\pipeline_output"
    star_index = r"C:\path\to\star\genome_index"  # Set your STAR genome index path here

    # Set to True to run alignment, False to skip alignment and only run MultiQC on existing files
    run_alignment_flag = True

    process_sample_groups(base_dir, sample_prefix, sample_groups, output_base_dir, star_index, run_alignment_flag)