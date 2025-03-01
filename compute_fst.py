#!/usr/bin/env python
import allel
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# Base directory where your VCF files are stored on the HPC
vcf_base = "/data/scratch/bt24140"

# Define the chromosomes to process
chromosomes = [2, 3, 6, 7, 8, 9, 10, 11, 16, 17, 20]

# Population labels 
pop1 = "GBR"  # British samples
pop2 = "GIH"  # GIH samples

def process_chromosome(chrom, base_dir, pop1, pop2):
    """
    Process one chromosome: load VCF files for pop1 and pop2, calculate FST using Hudson's estimator,
    and return a DataFrame with chromosome, SNP positions, and FST values.
    """
    # Construct file paths for both populations
    vcf_file1 = os.path.join(base_dir, f"ALL.chr{chrom}.{pop1}.vcf.gz")
    vcf_file2 = os.path.join(base_dir, f"ALL.chr{chrom}.{pop2}.vcf.gz")
    
    # Check if both files exist
    if not os.path.exists(vcf_file1):
        print(f"VCF file for {pop1} on chr{chrom} not found. Skipping...")
        return None
    if not os.path.exists(vcf_file2):
        print(f"VCF file for {pop2} on chr{chrom} not found. Skipping...")
        return None
    
    print(f"Processing chromosome {chrom} for {pop1} vs {pop2}...")
    
    # Load VCF data (we only need positions and genotype calls)
    cs1 = allel.read_vcf(vcf_file1, fields=['variants/POS', 'calldata/GT'])
    cs2 = allel.read_vcf(vcf_file2, fields=['variants/POS', 'calldata/GT'])
    
    # Assume both VCFs have the same set of variants in the same order.
    pos = cs1['variants/POS']
    gt1 = allel.GenotypeArray(cs1['calldata/GT'])
    gt2 = allel.GenotypeArray(cs2['calldata/GT'])
    
    # Count allele frequencies for each SNP
    ac1 = gt1.count_alleles()
    ac2 = gt2.count_alleles()
    
    # Calculate FST using Hudson's estimator; avoid division by zero
    num, den = allel.hudson_fst(ac1, ac2)
    fst_values = np.divide(num, den, out=np.zeros_like(num, dtype=float), where=(den > 0))
    
    # Create a DataFrame for the current chromosome
    df = pd.DataFrame({
        "CHROM": chrom,
        "POS": pos,
        "FST": fst_values
    })
    return df

# Process each chromosome and store results
results = []
for chrom in chromosomes:
    df = process_chromosome(chrom, vcf_base, pop1, pop2)
    if df is not None:
        results.append(df)

# Combine results across chromosomes
if results:
    all_fst = pd.concat(results, ignore_index=True)
    print("Combined FST results (first 10 rows):")
    print(all_fst.head(10))
    
    # Save combined results to CSV
    output_csv = os.path.join(vcf_base, "FST_results_all_chromosomes_GBR_vs_GIH.csv")
    all_fst.to_csv(output_csv, index=False)
    print(f"FST results saved to {output_csv}")
    
    # Plot a histogram of FST values
    plt.figure(figsize=(10, 6))
    plt.hist(all_fst['FST'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    plt.xlabel("FST")
    plt.ylabel("Number of SNPs")
    plt.title("Distribution of FST values (GBR vs GIH)")
    hist_path = os.path.join(vcf_base, "FST_histogram_GBR_vs_GIH.png")
    plt.savefig(hist_path)
    print(f"Histogram saved as {hist_path}")
    # Optionally, display the plot if running interactively:
    # plt.show()
else:
    print("No FST results were computed. Check input files and population codes.")
