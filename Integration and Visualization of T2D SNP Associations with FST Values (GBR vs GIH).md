```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Define file paths
fst_path = "FST_results_all_chromosomes_GBR_vs_GIH.csv"
t2d_path = "associationsss.tsv"

# Check if files exist
if not os.path.exists(fst_path):
    print(f"Error: FST file not found at {fst_path}")
    exit(1)
if not os.path.exists(t2d_path):
    print(f"Error: T2D file not found at {t2d_path}")
    exit(1)

# Load data
df_fst = pd.read_csv(fst_path, dtype={'CHROM': str})
df_t2d = pd.read_csv(t2d_path, sep='\t', dtype={'chromosome': str})

# Rename columns for consistency
df_t2d.rename(columns={'chromosome': 'CHROM', 'position': 'POS'}, inplace=True)

# Verify required columns
if 'CHROM' not in df_t2d.columns or 'POS' not in df_t2d.columns:
    print("Error: T2D DataFrame missing 'CHROM' or 'POS' after renaming")
    exit(1)
if 'CHROM' not in df_fst.columns or 'POS' not in df_fst.columns:
    print("Error: FST DataFrame missing 'CHROM' or 'POS'")
    exit(1)

# Merge DataFrames on 'CHROM' and 'POS'
df_merged = pd.merge(df_t2d, df_fst, on=['CHROM', 'POS'], how='inner')

# Display first 10 rows
print("First 10 rows of merged T2D SNPs with FST values:")
print(df_merged.head(10))

# Summary statistics
print("\nSummary statistics for FST values of T2D SNPs:")
print(df_merged['FST'].describe())

# Total number of T2D SNPs
total_t2d_snps = df_merged.shape[0]
print(f"\nTotal number of T2D SNPs: {total_t2d_snps}")

# Calculate key statistics
mean_fst = df_merged['FST'].mean()    
median_fst = df_merged['FST'].median() 
max_fst = df_merged['FST'].max()      

# Identify and display the outlier SNP
print("\nDetails of the SNP with maximum FST:")
max_fst_row = df_merged.loc[df_merged['FST'].idxmax()]
print(max_fst_row[['CHROM', 'POS', 'FST']])

# Plot histogram
plt.figure(figsize=(10, 6))
n, bins, patches = plt.hist(df_merged['FST'], bins=10, range=(0, 0.25), 
                           color='skyblue', edgecolor='black', alpha=0.7)

# Highlight the bar containing the maximum FST (outlier SNP)
bin_index = np.digitize(max_fst, bins) - 1
if 0 <= bin_index < len(patches):
    patches[bin_index].set_facecolor('red')


# Add vertical lines for key statistics
plt.axvline(x=mean_fst, color='green', linestyle='--', 
            label=f'Mean FST: {mean_fst:.4f}')
plt.axvline(x=median_fst, color='purple', linestyle='--', 
            label=f'Median FST: {median_fst:.4f}')
plt.axvline(x=max_fst, color='red', linestyle='--', 
            label=f'Max FST: {max_fst:.4f}')

# Overlay density curve
sns.kdeplot(df_merged['FST'], color='blue', lw=2)

# Trim x-axis
plt.xlim(0, 0.25)

# Labels and title
plt.xlabel("FST")
plt.ylabel("Number of T2D SNPs")
plt.title("Histogram of FST Values for T2D SNPs (GBR vs GIH)")

# Add legend
plt.legend()

# Display plot
plt.show()

# Save merged DataFrame
output_path = "t2d_snps_with_fst_GIHvsGBR.csv"
df_merged.to_csv(output_path, index=False)
print(f"\nMerged T2D SNPs with FST saved to {output_path}")
```

    First 10 rows of merged T2D SNPs with FST values:
                  varId  alignment alt ancestry    beta CHROM   clumpEnd  \
    0    9:22134068:G:A          1   A    Mixed -0.1430     9   26605499   
    1  10:114761697:A:C          1   C    Mixed  0.1332    10  127030606   
    2    6:20686878:C:T          1   T    Mixed  0.1313     6   56265633   
    3    11:2858546:C:T          1   T    Mixed -0.2112    11   20972162   
    4   3:185510613:T:G          1   G    Mixed  0.1023     3  188725858   
    5   16:53802494:C:T          1   T    Mixed  0.1004    16   56564387   
    6   8:118184783:C:T          1   T    Mixed -0.0819     8  138215648   
    7   10:94463945:G:A          1   A    Mixed -0.0876    10  107574798   
    8   7:127253550:C:T          1   T    Mixed  0.2736     7  131986889   
    9   10:12307894:C:T          1   T    Mixed  0.0837    10   20344510   
    
       clumpStart                         dataset                inMetaTypes  ...  \
    0    13458523  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    1   112613757  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    2    15253012  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    3      433541  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    4   177675859  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    5    49038220  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    6   113370184  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    7    86999072  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    8   125519449  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    9     8276572  bottom-line_analysis_T2D_Mixed  bottom-line;min_p;largest  ...   
    
                            source  stdErr                            clump  \
    0  bottom-line_analysis_common  0.0020   77_bottom-line_analysis_common   
    1  bottom-line_analysis_common  0.0018   62_bottom-line_analysis_common   
    2  bottom-line_analysis_common  0.0019    2_bottom-line_analysis_common   
    3  bottom-line_analysis_common  0.0027   49_bottom-line_analysis_common   
    4  bottom-line_analysis_common  0.0016   52_bottom-line_analysis_common   
    5  bottom-line_analysis_common  0.0017   73_bottom-line_analysis_common   
    6  bottom-line_analysis_common  0.0015   65_bottom-line_analysis_common   
    7  bottom-line_analysis_common  0.0016   16_bottom-line_analysis_common   
    8  bottom-line_analysis_common  0.0057  126_bottom-line_analysis_common   
    9  bottom-line_analysis_common  0.0019   72_bottom-line_analysis_common   
    
            dbSNP              consequence      nearest minorAllele     maf  \
    0  rs10811660       intergenic_variant   ["CDKN2B"]           A  0.1765   
    1  rs10885402           intron_variant   ["TCF7L2"]           C  0.4587   
    2  rs67131976           intron_variant   ["CDKAL1"]           T  0.2230   
    3   rs2237897           intron_variant   ["CDKN1C"]           T  0.1422   
    4   rs7633675           intron_variant  ["IGF2BP2"]           G  0.4675   
    5  rs11642015           intron_variant      ["FTO"]           T  0.2284   
    6  rs13266634         missense_variant  ["SLC30A8"]           T  0.2552   
    7   rs1977833       intergenic_variant     ["HHEX"]           A  0.4567   
    8   rs2233580         missense_variant     ["PAX4"]           T  0.0198   
    9  rs11257655  downstream_gene_variant   ["CDC123"]           T  0.3011   
    
                                                      af       FST  
    0  {"AA":0.0454,"EA":0.4355,"EU":0.168,"HS":0.125... -0.002269  
    1  {"AA":0.8601,"EA":0.0496,"EU":0.4911,"HS":0.34...  0.006632  
    2  {"AA":0.1445,"EA":0.3819,"EU":0.1779,"HS":0.17...  0.002232  
    3  {"AA":0.0809,"EA":0.3532,"EU":0.0467,"HS":0.27...  0.015749  
    4  {"AA":0.8411,"EA":0.2629,"EU":0.3042,"HS":0.30...  0.082468  
    5  {"AA":0.056,"EA":0.1677,"EU":0.4324,"HS":0.239...  0.037683  
    6  {"AA":0.08732,"EA":0.4392,"EU":0.302,"HS":0.25... -0.003732  
    7  {"AA":0.1853,"EA":0.7163,"EU":0.4245,"HS":0.37...  0.053133  
    8  {"AA":0.00006152,"EA":0.1105,"HS":0.0001156,"S...  0.000000  
    9  {"AA":0.2413,"EA":0.5397,"EU":0.2266,"HS":0.26... -0.003808  
    
    [10 rows x 27 columns]
    
    Summary statistics for FST values of T2D SNPs:
    count    98.000000
    mean      0.026755
    std       0.042325
    min      -0.005194
    25%      -0.000026
    50%       0.009850
    75%       0.041508
    max       0.220326
    Name: FST, dtype: float64
    
    Total number of T2D SNPs: 98
    
    Details of the SNP with maximum FST:
    CHROM          17
    POS      17753846
    FST      0.220326
    Name: 55, dtype: object
    


    
![png](output_0_1.png)
    


    
    Merged T2D SNPs with FST saved to t2d_snps_with_fst_GIHvsGBR.csv
    


```python
# Identify SNPs with missing FST values
missing_fst_snps = df_merged[df_merged['FST'].isna()]

# Display the number of SNPs with missing FST
print(f"\nNumber of T2D SNPs with missing FST values: {missing_fst_snps.shape[0]}")

# Display details of SNPs with missing FST values
print("\nT2D SNPs with missing FST values:")
print(missing_fst_snps[['CHROM', 'POS', 'varId']].head(10))  # Show first 10 rows
```

    
    Number of T2D SNPs with missing FST values: 0
    
    T2D SNPs with missing FST values:
    Empty DataFrame
    Columns: [CHROM, POS, varId]
    Index: []
    


```python

```


```python
from IPython.display import FileLink
FileLink(r"t2d_snps_with_fst_GIHvsGBR.csv")
```




<a href='t2d_snps_with_fst_GIHvsGBR.csv' target='_blank'>t2d_snps_with_fst_GIHvsGBR.csv</a><br>




```python
from IPython.display import HTML
HTML('<a download="t2d_snps_with_fst_GIHvsGBR.csv" href="t2d_snps_with_fst_GIHvsGBR.csv">Download</a>')
```




<a download="t2d_snps_with_fst_GIHvsGBR.csv" href="t2d_snps_with_fst_GIHvsGBR.csv">Download</a>


