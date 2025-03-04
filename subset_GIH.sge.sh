#!/bin/bash
#$ -N subset_GIH
#$ -o logs/subset_GIH_$JOB_ID.out
#$ -e logs/subset_GIH_$JOB_ID.err
#$ -cwd
#$ -l h_rt=2:00:00
#$ -l h_vmem=4G
#$ -l rocky

# Load bcftools module (adjust version if needed)
module purge
module load bcftools/1.19-gcc-12.2.0

# Define the panel file and sample list file
PANEL_FILE="/data/scratch/bt24140/integrated_call_samples_v3.20130502.ALL.panel"
SAMPLE_LIST="GIH_samples.txt"

# Generate GIH_samples.txt if it does not exist.
if [ ! -f "$SAMPLE_LIST" ]; then
  # the panel file has a header and the second column contains population codes.
  awk -F '\t' 'NR > 1 && $2 == "GIH" {print $1}' "$PANEL_FILE" > "$SAMPLE_LIST"
  echo "Created sample list: $SAMPLE_LIST"
fi

# Define chromosomes to process
CHROMOSOMES=(2 3 6 7 8 9 10 11 16 17 20)
# Base directory for VCF files
VCF_DIR="/data/scratch/bt24140"

# Loop over each chromosome and subset VCF for GIH samples
for CHR in "${CHROMOSOMES[@]}"; do
  INPUT_VCF="${VCF_DIR}/ALL.chr${CHR}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
  OUTPUT_VCF="${VCF_DIR}/ALL.chr${CHR}.GIH.vcf.gz"
  
  if [ ! -f "${INPUT_VCF}" ]; then
    echo "ERROR: Input VCF for chr${CHR} not found: ${INPUT_VCF}"
    continue
  fi
  
  echo "Subsetting chromosome ${CHR} for GIH samples..."
  bcftools view -S "$SAMPLE_LIST" "$INPUT_VCF" -Oz -o "$OUTPUT_VCF"
  
  if [ $? -eq 0 ]; then
    bcftools index "$OUTPUT_VCF"
    echo "Finished chr${CHR}"
  else
    echo "Error subsetting chromosome ${CHR}"
  fi
done

echo "All chromosomes processed for GIH subset!"
