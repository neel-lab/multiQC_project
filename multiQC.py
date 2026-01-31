"""
Windows + WSL setup notes (run once):

In Windows CMD (Admin):
  wsl --install
Reboot, open Ubuntu (WSL) terminal, then:
  sudo apt update
  sudo apt install rna-star fastqc

(Optional) Build STAR index (example; quote paths with spaces):
  STAR --runMode genomeGenerate \
    --genomeDir "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/star_transcriptome_index" \
    --genomeFastaFiles "/mnt/c/Users/neel/Box/My programs/Python/scglyco/data/gencode_v47_transcripts.fasta" \
    --runThreadN 8

MultiQC is run on Windows:
  pip install multiqc
"""

import os, time
import posixpath
import subprocess
from pathlib import PureWindowsPath

import pandas as pd


def win_to_wsl_path(win_path: str) -> str:
    """
    Convert a Windows path like: C:\\Users\\neel\\file.fastq.gz
    to a WSL path like: /mnt/c/Users/neel/file.fastq.gz

    Works for any drive letter.
    """
    p = PureWindowsPath(win_path)

    if p.drive:
        drive_letter = p.drive.rstrip(":").lower()
        parts = p.parts[1:]  # drop 'C:\\'
        return posixpath.join("/mnt", drive_letter, *parts)

    return win_path.replace("\\", "/")


def fastqc_expected_basename(filepath: str) -> str:
    """
    FastQC output uses the input filename with common FASTQ suffixes removed.
    Examples:
      sample_R1_001.fastq.gz -> sample_R1_001_fastqc.zip
      sample_R1_001.fq.gz    -> sample_R1_001_fastqc.zip
      sample_R1_001.fastq    -> sample_R1_001_fastqc.zip
    """
    base = os.path.basename(filepath)

    if base.lower().endswith(".gz"):
        base = base[:-3]

    lower = base.lower()
    for suf in (".fastq", ".fq"):
        if lower.endswith(suf):
            base = base[: -len(suf)]
            break

    return base


def run_alignment(sample_fastq_r1, sample_fastq_r2, output_dir, star_index, sample_name, threads=4):
    """
    Run STAR alignment on paired-end fastq(.gz) files using WSL.
    """
    if not star_index:
        raise ValueError("star_index must be provided when run_alignment_flag=True")

    os.makedirs(output_dir, exist_ok=True)

    r1_wsl = win_to_wsl_path(sample_fastq_r1)
    r2_wsl = win_to_wsl_path(sample_fastq_r2)
    output_dir_wsl = win_to_wsl_path(output_dir)
    star_index_wsl = win_to_wsl_path(star_index)

    # IMPORTANT: use POSIX join for WSL paths (avoid Windows backslashes)
    star_out_prefix_wsl = posixpath.join(output_dir_wsl, sample_name + "_")

    cmd = [
        "wsl", "-e", "STAR",
        "--runThreadN", str(threads),
        "--genomeDir", star_index_wsl,
        "--readFilesIn", r1_wsl, r2_wsl,
        "--readFilesCommand", "zcat",
        "--outFileNamePrefix", star_out_prefix_wsl,
        "--outSAMtype", "BAM", "SortedByCoordinate",
        "--outSAMunmapped", "Within",
        "--outFilterMultimapNmax", "1",
        "--outReadsUnmapped", "Fastx",
    ]

    print(f"Running STAR alignment for {sample_name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("STAR command:")
        print("  " + " ".join(cmd))
        print("\nSTAR stderr:\n" + (result.stderr or "").strip())
        print("\nSTAR stdout:\n" + (result.stdout or "").strip())
    else:
        print(f"STAR alignment completed for {sample_name}.")

    return os.path.join(output_dir, sample_name + "_Log.final.out")


import time
import posixpath
import subprocess

def run_fastqc_to_wsl_then_copy(r1_wsl, r2_wsl, win_fastqc_output_dir, threads=4, wsl_root="~/fastqc_runs"):
    """
    Run FastQC in WSL filesystem (fast/reliable), then copy results to a Windows directory.

    Args:
      r1_wsl, r2_wsl: WSL paths to FASTQs (e.g. /mnt/c/...fastq.gz)
      win_fastqc_output_dir: Windows path where you ultimately want results (e.g. C:\\Users\\...\\fastqc_output)
      threads: FastQC threads
      wsl_root: base dir in WSL (Linux FS) to store outputs
    """
    # Make a unique WSL output dir per run (avoids collisions)
    stamp = str(int(time.time()))
    wsl_out = posixpath.join(wsl_root, f"fastqc_{stamp}")

    win_out_wsl = win_to_wsl_path(win_fastqc_output_dir)

    bash_cmd = (
        "set -euo pipefail; "
        "cd /tmp; "
        f"mkdir -p {wsl_out!s}; "
        f"fastqc -t {threads} '{r1_wsl}' '{r2_wsl}' -o {wsl_out!s}; "
        # Create Windows dir if possible; if Box blocks mkdir, this will fail.
        # So we copy to the parent (which should already exist from Windows) and overwrite contents.
        f"cp -a {wsl_out!s}/. '{win_out_wsl}'")

    cmd = ["wsl", "-e", "bash", "-lc", bash_cmd]
    print(f"Running FastQC (WSL->copy): {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    if result.returncode != 0:
        print("FastQC stderr:\n" + (result.stderr or "").strip())
        print("FastQC stdout:\n" + (result.stdout or "").strip())
    else:
        print("FastQC completed and copied to Windows output dir.")


def run_fastqc(r1_wsl, r2_wsl, output_dir_wsl, threads=2):
    """
    NOT USED
    Run FastQC on paired-end FASTQ files via WSL.
    Ensures the output directory exists in WSL and avoids Box/permission CWD issues
    by running from /tmp.
    """
    bash_cmd = (
        f"set -euo pipefail; "
        f"cd /tmp; "
        f"mkdir -p '{output_dir_wsl}'; "
        f"fastqc -t {threads} '{r1_wsl}' '{r2_wsl}' -o '{output_dir_wsl}'")
    cmd = ["wsl", "-e", "bash", "-lc", bash_cmd]
    print(f"Running FastQC: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print("FastQC stderr:\n" + (result.stderr or "").strip())
        print("FastQC stdout:\n" + (result.stdout or "").strip())
    else:
        print("FastQC completed.")


def parse_star_log(log_path):
    """Parse STAR Log.final.out file to extract mapping stats."""
    if not os.path.exists(log_path):
        print(f"Warning: Log file {log_path} not found.")
        return {}

    stats = {}
    with open(log_path, "r") as f:
        for line in f:
            if "Uniquely mapped reads %" in line:
                stats["Uniquely mapped reads %"] = line.strip().split("|")[1].strip()
            elif "Number of input reads" in line:
                stats["Number of input reads"] = line.strip().split("|")[1].strip()
            elif "Number of reads mapped to multiple loci" in line:
                stats["Multimapped reads"] = line.strip().split("|")[1].strip()
            elif "Number of reads mapped to too many loci" in line:
                stats["Too many loci reads"] = line.strip().split("|")[1].strip()
    return stats


def run_multiqc_on_group(files_to_analyze, output_dir):
    """Run MultiQC on a list of files/directories (Windows)."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = ["multiqc", "-v -o", output_dir] + files_to_analyze       # -v is verbose
    print(f"Running MultiQC: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print("MultiQC stderr:\n" + (result.stderr or "").strip())
        print("MultiQC stdout:\n" + (result.stdout or "").strip())
    else:
        print(f"MultiQC report generated in {output_dir}")


def process_sample_groups_from_csv(base_dir, csv_path, output_base_dir, star_index=None, run_alignment_flag=False,
                                   run_fastqc_flag=False, threads_fastqc=2, threads_star=4):
    """
    Process sample groups based on 'Group' column in CSV:
      - optionally run FastQC (WSL)
      - optionally run STAR alignment (WSL)
      - run MultiQC (Windows) per group
    """
    df = pd.read_csv(os.path.join(base_dir, csv_path))
    if "Group" not in df.columns:
        raise ValueError("CSV must contain a 'Group' column.")

    required_cols = {"FASTQ Path - Read 1", "FASTQ Path - Read 2"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    unique_groups = df["Group"].dropna().unique().tolist()

    for i, group in enumerate(unique_groups, start=1):
        group_df = df[df["Group"] == group]

        print(f"\nProcessing group {i} ({group}) with samples:")
        files_to_analyze = []

        for _, row in group_df.iterrows():
            r1 = os.path.join(base_dir, row["FASTQ Path - Read 1"])
            r2 = os.path.join(base_dir, row["FASTQ Path - Read 2"])

            # derive a nice sample name
            sample_name = os.path.basename(r1)
            for tag in ("_R1_001.fastq.gz", "_R1_001.fq.gz", "_R1_001.fastq", "_R1_001.fq"):
                if sample_name.endswith(tag):
                    sample_name = sample_name[: -len(tag)]
                    break
            sample_name = (sample_name.replace(".fastq.gz", "")
                .replace(".fq.gz", "")
                .replace(".fastq", "")
                .replace(".fq", ""))

            if not (os.path.exists(r1) and os.path.exists(r2)):
                print(f"Warning: Missing files for sample {sample_name}: {r1} or {r2}")
                continue

            print(f"  Sample: {sample_name}")

            r1_wsl = win_to_wsl_path(r1)
            r2_wsl = win_to_wsl_path(r2)

            sample_output_dir = os.path.join(output_base_dir, f"group_{i}", sample_name)
            os.makedirs(sample_output_dir, exist_ok=True)

            # -------------------------
            # FastQC (WSL) if requested
            # -------------------------
            if run_fastqc_flag:
                fastqc_output_dir = os.path.join(sample_output_dir, "fastqc_output")
                os.makedirs(fastqc_output_dir, exist_ok=True)
                run_fastqc_to_wsl_then_copy(r1_wsl, r2_wsl, fastqc_output_dir, threads=threads_fastqc)

                files_to_analyze.append(fastqc_output_dir)

                # Check that file is written correctly
                r1_base = fastqc_expected_basename(r1)
                r2_base = fastqc_expected_basename(r2)
                expected1 = os.path.join(fastqc_output_dir, r1_base + "_fastqc.zip")
                expected2 = os.path.join(fastqc_output_dir, r2_base + "_fastqc.zip")
                if not os.path.exists(expected1):
                    print(f"  Warning: expected FastQC output not found: {expected1}")
                if not os.path.exists(expected2):
                    print(f"  Warning: expected FastQC output not found: {expected2}")

            # -------------------------
            # STAR (WSL) if requested
            # -------------------------
            if run_alignment_flag:
                align_out_dir = os.path.join(sample_output_dir, "star_alignment")
                log_file = run_alignment(
                    r1, r2, align_out_dir, star_index, sample_name, threads=threads_star
                )
                if os.path.exists(log_file):
                    files_to_analyze.append(log_file)
                else:
                    print(f"  Warning: STAR log not found: {log_file}")

        if not files_to_analyze:
            print(f"No files to analyze for group {i}. Skipping MultiQC.")
            continue

        multiqc_out_dir = os.path.join(output_base_dir, f"group_{i}_{group}", "multiqc_report")
        run_multiqc_on_group(files_to_analyze, multiqc_out_dir)


if __name__ == "__main__":
    base_dir = r"D:\human_genome\SR010180"
    csv_path = "Samplemap2_consolidated.csv"
    output_base_dir = r"D:\human_genome\SR010180\pipeline_output"
    star_index = r"D:\human_genome\data\star_transcriptome_index"

    # Set flags for what you want to run
    run_alignment_flag = False  # True to enable STAR
    run_fastqc_flag = True      # True to run FastQC

    process_sample_groups_from_csv(base_dir=base_dir, csv_path=csv_path, output_base_dir=output_base_dir,
                                   star_index=star_index, run_alignment_flag=run_alignment_flag,
                                   run_fastqc_flag=run_fastqc_flag, threads_fastqc=4,  threads_star=8)
