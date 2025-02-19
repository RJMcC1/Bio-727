import sqlite3
import pandas as pd

# ================================================================
# Configuration: Adjust these file paths as needed.
# ================================================================
db_file_path = 'genetics.db'
tsv_file_path = 'associations.tsv'  # e.g., 'data/variants.tsv'

# ================================================================
# Step 1: Connect to the SQLite database
# ================================================================
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# ================================================================
# Step 2: Create the Schema Tables with Fixes
# ================================================================

# Gene table: we add a UNIQUE constraint on (gene_name, functional_term) so that 
# a gene with a different consequence (functional_term) is stored separately.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gene (
        gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
        gene_name TEXT NOT NULL,
        functional_term TEXT,
        ontology_term TEXT,
        UNIQUE(gene_name, functional_term)
    )
''')

# Functional term gene link: We change the column types to TEXT (instead of IDs) for this example.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS functional_term_gene_link (
        gene_id INTEGER NOT NULL,
        functional_term TEXT,
        ontology_term TEXT,
        PRIMARY KEY (gene_id, functional_term, ontology_term),
        FOREIGN KEY (gene_id) REFERENCES gene (gene_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS population (
        population_id INTEGER PRIMARY KEY AUTOINCREMENT,
        population_name TEXT NOT NULL UNIQUE,
        sampling_location TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS snp (
        snp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        snp_name TEXT NOT NULL UNIQUE,
        chromosome TEXT NOT NULL,
        start_position INTEGER NOT NULL,
        end_position INTEGER,
        p_value DECIMAL(10,6),
        mapped_gene_id INTEGER,
        FOREIGN KEY (mapped_gene_id) REFERENCES gene (gene_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS selection_statistics_avg_std_dev (
        snp_id INTEGER,
        region_start INTEGER,
        region_end INTEGER,
        average_stat DECIMAL(10,6),
        std_dev_stat DECIMAL(10,6),
        FOREIGN KEY (snp_id) REFERENCES snp (snp_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS snp_population_selection_stats (
        snp_id INTEGER NOT NULL,
        population_id INTEGER NOT NULL,
        selection_statistic_1 DECIMAL(10,6),
        selection_statistic_2 DECIMAL(10,6),
        PRIMARY KEY (snp_id, population_id),
        FOREIGN KEY (snp_id) REFERENCES snp (snp_id),
        FOREIGN KEY (population_id) REFERENCES population (population_id)
    )
''')

# Create a staging table for the TSV data ("associations")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS associations (
        varId                TEXT,
        alignment            TEXT,
        alt                  TEXT,
        ancestry             TEXT,
        beta                 REAL,
        chromosome           TEXT,
        clumpEnd             INTEGER,
        clumpStart           INTEGER,
        dataset              TEXT,
        inMetaTypes          TEXT,
        leadSNP              TEXT,
        n                    INTEGER,
        pValue               REAL,
        phenotype            TEXT,
        position             INTEGER,
        posteriorProbability REAL,
        reference            TEXT,
        source               TEXT,
        stdErr               REAL,
        clump                TEXT,
        dbSNP                TEXT,
        consequence          TEXT,
        nearest              TEXT,
        minorAllele          TEXT,
        maf                  REAL,
        af                   REAL
    )
''')
conn.commit()

# ================================================================
# Step 3: Import the TSV File into the associations Staging Table Using Pandas
# ================================================================
df = pd.read_csv(tsv_file_path, sep='\t')
print("Preview of TSV data:")
print(df.head())

# Use if_exists='replace' so the staging table holds only the latest import.
df.to_sql('associations', conn, if_exists='replace', index=False)
conn.commit()

# ================================================================
# Step 4: Insert New Genes 
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO gene (gene_name, functional_term)
    SELECT DISTINCT nearest, consequence
    FROM associations
    WHERE nearest IS NOT NULL;
''')
conn.commit()

# ================================================================
# Step 5: Populate the Functional Term Gene Link Table
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO functional_term_gene_link (gene_id, functional_term, ontology_term)
    SELECT gene_id, functional_term, ontology_term
    FROM gene;
''')
conn.commit()

# ================================================================
# Step 6: Insert New SNPs 
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO snp (snp_name, chromosome, start_position, end_position, p_value, mapped_gene_id)
    SELECT DISTINCT a.dbSNP, a.chromosome, a.clumpStart, a.clumpEnd, a.pValue, g.gene_id
    FROM associations a
    LEFT JOIN gene g 
         ON g.gene_name = a.nearest 
        AND g.functional_term = a.consequence
    LEFT JOIN snp s 
         ON s.snp_name = a.dbSNP
    WHERE a.dbSNP IS NOT NULL 
      AND s.snp_name IS NULL;
''')
conn.commit()

# ================================================================
# Step 7: Insert New Populations
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO population (population_name)
    SELECT DISTINCT ancestry FROM associations
    WHERE ancestry IS NOT NULL;
''')
conn.commit()

# ================================================================
# Step 8: Insert SNP-Population Selection Statistics
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO snp_population_selection_stats (snp_id, population_id, selection_statistic_1, selection_statistic_2)
    SELECT s.snp_id, p.population_id, a.maf, a.beta 
    FROM associations a
    JOIN snp s ON s.snp_name = a.dbSNP
    JOIN population p ON p.population_name = a.ancestry
    WHERE a.dbSNP IS NOT NULL 
      AND a.ancestry IS NOT NULL;
''')
conn.commit()

# ================================================================
# Close the Connection
# ================================================================
conn.close()
