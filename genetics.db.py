import pandas as pd
import sqlite3

# ================================================================
# Configuration / file paths
# ================================================================
db_file_path = 'genetics.db'    # path for the SQLite database
tsv_file_path = 'associations.tsv'  # path to TSV file

# ================================================================
# Connect to the SQLite database
# ================================================================
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# ================================================================
# Step 2: Create the Schema Tables
# ================================================================
cursor.execute('''CREATE TABLE IF NOT EXISTS gene (
    gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_name TEXT NOT NULL,
    functional_term TEXT,
    ontology_term TEXT,
    nearest TEXT
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
cursor.execute('''CREATE TABLE IF NOT EXISTS associations (
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
df.to_sql('associations', conn, if_exists='replace', index=False)
conn.commit()

# ================================================================
# Step 1: Insert new genes if not already in the database
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO gene (gene_name, functional_term, ontology_term, nearest)
    SELECT DISTINCT nearest, consequence, NULL, nearest
    FROM associations
    WHERE nearest IS NOT NULL;
''')
conn.commit()

# ================================================================
# Step 2: Insert new SNPs if they don’t already exist
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO snp (snp_name, chromosome, start_position, end_position, p_value, mapped_gene_id)
    SELECT DISTINCT associations.dbSNP, associations.chromosome, associations.clumpStart, associations.clumpEnd, associations.pValue, gene.gene_id
    FROM associations
    LEFT JOIN gene ON gene.gene_name = associations.nearest;
''')
conn.commit()


# ================================================================
# Step 3: Insert new populations if not already in the database
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO population (population_name)
    SELECT DISTINCT ancestry FROM associations;
''')
conn.commit()

# ================================================================
# Step 4: Insert SNP-Population selection statistics
# ================================================================
cursor.execute('''
    INSERT OR IGNORE INTO snp_population_selection_stats (snp_id, population_id, selection_statistic_1, selection_statistic_2)
    SELECT snp.snp_id, population.population_id, associations.maf, associations.beta
    FROM associations
    JOIN snp ON snp.snp_name = associations.dbSNP
    JOIN population ON population.population_name = associations.ancestry;
''')
conn.commit()

# ================================================================
# Handle JSON-Like `af` Column
# ================================================================
cursor.execute("ALTER TABLE associations ADD COLUMN af_json TEXT;")
conn.commit()

# Load TSV File
df = pd.read_csv(tsv_file_path, sep='\t')

# Convert `af` column to string for storage
df["af_json"] = df["af"].astype(str)
df.drop(columns=["af"], inplace=True)

# Reinsert into SQLite
df.to_sql('associations', conn, if_exists='replace', index=False)
conn.commit()

# ================================================================
# Step 5: Preview the Tables
# ================================================================
def preview_all_tables(db_path, limit=10):
    """
    Preview all tables in the SQLite database.
    
    Parameters:
    db_path (str): Path to the SQLite database
    limit (int): Number of rows to preview from each table
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Preview each table
    for table in tables:
        table_name = table[0]
        print("\n" + "="*50)
        print(f"Preview of table '{table_name}':")
        print("="*50)
        
        try:
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            print("\nColumns:", ", ".join(columns))
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"Total rows: {row_count}")
            
            # Preview data
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
            if not df.empty:
                print("\nSample data:")
                print(df)
            else:
                print("\nNo data available in this table.")
                
        except sqlite3.Error as e:
            print(f"Error previewing table {table_name}: {e}")
    
    conn.close()

print("\nPreviewing all tables in the database:")
preview_all_tables(db_file_path)

# Close the final connection
conn.close()
print("\nDatabase operations completed successfully!")

# ================================================================
# Step 6: Close the Database Connection
# ================================================================
conn.close()
print("TSV data merged with the original schema successfully!")