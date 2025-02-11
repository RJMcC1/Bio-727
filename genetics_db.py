import pandas as pd
import sqlite3

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
# Step 2: Create the Original Schema Tables
# ================================================================
cursor.execute('''CREATE TABLE IF NOT EXISTS gene (
    gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_name TEXT NOT NULL,
    functional_term TEXT,
    ontology_term TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS functional_term_gene_link (
    gene_id INTEGER NOT NULL,
    functional_term_id INTEGER,
    ontology_term_id INTEGER,
    PRIMARY KEY (gene_id, functional_term_id, ontology_term_id),
    FOREIGN KEY (gene_id) REFERENCES gene (gene_id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS population (
    population_id INTEGER PRIMARY KEY AUTOINCREMENT,
    population_name TEXT NOT NULL,
    sampling_location TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS snp (
    snp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snp_name TEXT NOT NULL,
    chromosome TEXT NOT NULL,
    start_position INTEGER NOT NULL,
    end_position INTEGER,
    p_value DECIMAL(10,6),
    mapped_gene_id INTEGER,
    FOREIGN KEY (mapped_gene_id) REFERENCES gene (gene_id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS selection_statistics_avg_std_dev (
    snp_id INTEGER,
    region_start INTEGER,
    region_end INTEGER,
    average_stat DECIMAL(10,6),
    std_dev_stat DECIMAL(10,6),
    FOREIGN KEY (snp_id) REFERENCES snp (snp_id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS snp_population_selection_stats (
    snp_id INTEGER NOT NULL,
    population_id INTEGER NOT NULL,
    selection_statistic_1 DECIMAL(10,6),
    selection_statistic_2 DECIMAL(10,6),
    PRIMARY KEY (snp_id, population_id),
    FOREIGN KEY (snp_id) REFERENCES snp (snp_id),
    FOREIGN KEY (population_id) REFERENCES population (population_id)
)''')

# ================================================================
# Step 3: Create a Staging Table for the TSV Data ("variants")
# ================================================================
cursor.execute('''CREATE TABLE IF NOT EXISTS variants (
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
)''')

conn.commit()

# ================================================================
# Step 4: Import the TSV File into the "variants" Staging Table Using Pandas
# ================================================================
# Read the TSV file (which should have headers) into a DataFrame.
df = pd.read_csv(tsv_file_path, sep='\t')

# Optional: Preview the first few rows of the TSV data
print("Preview of TSV data:")
print(df.head())

# Insert the data into the variants table.
# Using if_exists='replace' to ensure the staging table holds only the latest import.
df.to_sql('variants', conn, if_exists='replace', index=False)
conn.commit()

# ================================================================
# Step 5: Merge the TSV Data with the Original snp Table
# ================================================================
# 1. Insert new SNPs from variants into the snp table if they don't already exist.
cursor.execute('''
    INSERT INTO snp (snp_name, chromosome, start_position, p_value)
    SELECT v.varId, v.chromosome, v.position, v.pValue
    FROM variants v
    LEFT JOIN snp s ON s.snp_name = v.varId
    WHERE s.snp_name IS NULL
''')
conn.commit()

# 2. Update existing SNP records in the snp table with data from variants.
cursor.execute('''
    UPDATE snp
    SET chromosome = (
            SELECT v.chromosome FROM variants v
            WHERE v.varId = snp.snp_name
        ),
        start_position = (
            SELECT v.position FROM variants v
            WHERE v.varId = snp.snp_name
        ),
        p_value = (
            SELECT v.pValue FROM variants v
            WHERE v.varId = snp.snp_name
        )
    WHERE snp.snp_name IN (SELECT varId FROM variants)
''')
conn.commit()

# ================================================================
# Step 6: Close the Database Connection
# ================================================================
conn.close()
print("TSV data merged with the original schema successfully!")

# Connect to the database
conn = sqlite3.connect(db_file_path)

# Specify the table name you want to preview
table_name = 'snp'

# Query the first 10 rows of the table
df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10", conn)

# Display the DataFrame
print(f"Preview of table '{table_name}':")
print(df)

# Close the connection
conn.close()
