import sqlite3  # SQLite module to create and manage the database.
import pandas as pd # Pandas for handling TSV/CSV file imports, reads and writes data from TSV/CSV files.
import json # JSON module for handling & parsing the allele frequency data.

# ================================================================
# Configuration: Adjust these file paths as needed
# ================================================================
db_file_path = 'genetics.db'    # SQLite database file (output)
# Input files:
tsv_file_path = 'associations.tsv'  # File containing SNP association data
uniprot_path = 'uniprot_data.tsv'   # File containing gene-to-UniProt page mapping
fst_file_path = 't2d_snps_with_fst_GIHvsGBR.csv'    # FST values for genetic differentiation
details_glb= 'Populationdetails.tsv'    # File containing global population data
ihs_file_path = 'ihs_summary_table.tsv'
subpopuplation ='sub_population.tsv';   # File containing sub-population data

# Holds the mean and standard deviation for a genetic statistic (e.g., FST)
# Data to be inserted: Placeholder for genetic statistics like FST (Fixation Index)??????????
data = {
    'stats': ['fst', 'ihs'],  # The name of the statistics being stored
    'mean': [0.0268, -6.84859e-10],
    'std': [0.0423, 0.999982]
}

# ================================================================
# Database Setup and Table Creation:
# Initializes the SQLite database and creates necessary tables
# ================================================================
def setup_database():
    conn = sqlite3.connect(db_file_path)    # Connect to / create the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL queries

    # Create tables
    # gene Table: Stores Gene Information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gene (
            gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_name TEXT NOT NULL,
            functional_term TEXT,
            UNIQUE(gene_name, functional_term)
        )
    ''')
    # population Table: Stores Population Names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS population (
            population_id INTEGER PRIMARY KEY AUTOINCREMENT,
            population_name TEXT NOT NULL UNIQUE
        )
    ''')
    # snp Table: Stores SNPs and Their Locations
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
    # population_glb Table: Stores Population Metadata
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS population_glb (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        population_name TEXT NOT NULL,
        geographical_sampling_locations TEXT NOT NULL,
        genetic_diversity TEXT NOT NULL,
        disease_trait_associations TEXT NOT NULL,
        FOREIGN KEY (population_name) REFERENCES population (population_name) 
    )
''')
    # snp_population_selection_stats Table: Stores SNP Frequencies by Population
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snp_population_selection_stats (
            snp_id INTEGER NOT NULL,
            population_id INTEGER NOT NULL,
            allele_freq DECIMAL(10,6),
            PRIMARY KEY (snp_id, population_id),
            FOREIGN KEY (snp_id) REFERENCES snp (snp_id),
            FOREIGN KEY (population_id) REFERENCES population (population_id)
        )
    ''')

    # Staging associations table for TSV import
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS associations (
            varId TEXT, alignment TEXT, alt TEXT, ancestry TEXT,
            beta REAL, chromosome TEXT, clumpEnd INTEGER, clumpStart INTEGER,
            dataset TEXT, inMetaTypes TEXT, leadSNP TEXT, n INTEGER,
            pValue REAL, phenotype TEXT, position INTEGER,
            posteriorProbability REAL, reference TEXT, source TEXT,
            stdErr REAL, clump TEXT, dbSNP TEXT, consequence TEXT,
            nearest TEXT, minorAllele TEXT, maf REAL, af TEXT
        )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS uniprot_data (
        gene_name TEXT NOT NULL,
        mapped_gene_id INTEGER,  -- Foreign Key to Gene Table
        uniprot_url TEXT,
        uniprot_id TEXT,
        FOREIGN KEY (mapped_gene_id) REFERENCES gene (gene_id)
        )
    ''')

    
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS fst (
            varId TEXT,
            alignment TEXT,
            alt TEXT,
            ancestry TEXT,
            beta DECIMAL(10,6),
            CHROM TEXT,
            clumpEnd INTEGER,
            clumpStart INTEGER,
            dataset TEXT,
            inMetaTypes TEXT,
            leadSNP TEXT,
            n INTEGER,
            pValue DECIMAL(10,6),
            phenotype TEXT,
            POS INTEGER,
            posteriorProbability DECIMAL(10,6),
            reference TEXT,
            source TEXT,
            stdErr DECIMAL(10,6),
            clump TEXT,
            dbSNP TEXT,
            consequence TEXT,
            nearest TEXT,
            minorAllele TEXT,
            maf DECIMAL(10,6),
            af TEXT,
            FST DECIMAL(10,6),
            FOREIGN KEY (dbSNP) REFERENCES snp (snp_name)             
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sub_population_details (
        population TEXT ,
        sub_population TEXT ,
        genetic_diversity TEXT ,
        disease_trait_associations TEXT ,
        PRIMARY KEY (population, sub_population),
        FOREIGN KEY (population) REFERENCES population (population_name)
        )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mean_std(
        stat TEXT UNIQUE,
        mean DECIMAL(10,6),
        std DECIMAL(10,6)
        )
    ''')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ihs_stat (
    Chromosome TEXT,
    Position INTEGER,
    iHS_Score DECIMAL(10,6),
    Mean_iHS DECIMAL(10,6),
    Std_iHS DECIMAL(10,6),
    Population TEXT)
    """)
           
    
    conn.commit()
    return conn
print (1)

# ================================================================
# Data Processing Functions
# ================================================================
# Extracts unique population names from JSON in af column and inserts them into the population table:
def process_populations(conn):
    cursor = conn.cursor()
    
    # Extract unique population names from JSON 'af' column
    cursor.execute("SELECT af FROM associations WHERE af IS NOT NULL AND af != ''")
    af_records = cursor.fetchall()

    population_names = set()
    for (af_json_str,) in af_records:
        try:
            af_dict = json.loads(af_json_str.replace("'", "\""))
            population_names.update(af_dict.keys())
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing JSON: {e}")
            continue

    # Insert populations
    for pop_name in population_names:
        cursor.execute('''
            INSERT OR IGNORE INTO population (population_name)
            VALUES (?)
        ''', (pop_name,))
        cursor.execute('''
            INSERT OR IGNORE INTO mean_std(stat, mean, std)
            VALUES (?, ?, ?)
        ''', (data['stats'][0], data['mean'][0], data['std'][0]))
        conn.commit()

# ================================================================
# Extracts genes from associations table and inserts them into gene table:
def process_genes(conn):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO gene (gene_name, functional_term)
        SELECT DISTINCT nearest, consequence
        FROM associations
        WHERE nearest IS NOT NULL
    ''')
    conn.commit()

# ================================================================
# Extracts SNPs from associations table and links them to genes:
def process_snps(conn):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO snp (
            snp_name, chromosome, start_position, end_position, p_value, mapped_gene_id
        )
        SELECT DISTINCT a.dbSNP, a.chromosome, a.clumpStart, a.clumpEnd, a.pValue, g.gene_id
        FROM associations a
        LEFT JOIN gene g ON g.gene_name = a.nearest AND g.functional_term = a.consequence
        LEFT JOIN snp s ON s.snp_name = a.dbSNP
        WHERE a.dbSNP IS NOT NULL AND s.snp_name IS NULL
    ''')
    conn.commit()

# ================================================================
# Extracts SNPs with allele frequency data (af) from the associations table.
def process_allele_frequencies(conn):
    cursor = conn.cursor()
    # Fetch SNPs with allele frequency data
    cursor.execute('''
        SELECT dbSNP, af FROM associations
        WHERE dbSNP IS NOT NULL AND af IS NOT NULL AND af != ''
    ''')
    snp_af_rows = cursor.fetchall()
    # Parses JSON allele frequency data.
    for dbSNP, af_json_str in snp_af_rows:
        try:
            af_dict = json.loads(af_json_str.replace("'", "\""))
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing JSON for {dbSNP}: {e}")
            continue

        # Insert Population-Specific Allele Frequencies: maps SNPs to population-specific allele frequencies.
        # Get SNP ID
        cursor.execute('SELECT snp_id FROM snp WHERE snp_name = ?', (dbSNP,))
        snp_result = cursor.fetchone()
        if not snp_result:
            continue
        snp_id = snp_result[0]

        # Process each population frequency
        for pop_name, af_value in af_dict.items():
            cursor.execute('''
                SELECT population_id FROM population WHERE population_name = ?
            ''', (pop_name,))
            pop_result = cursor.fetchone()
            if not pop_result:
                continue
            pop_id = pop_result[0]

            cursor.execute('''
                INSERT OR REPLACE INTO snp_population_selection_stats
                (snp_id, population_id, allele_freq)
                VALUES (?, ?, ?)
            ''', (snp_id, pop_id, af_value))
    conn.commit()

def process_uniprot(conn):
    cursor = conn.cursor()
    cursor.execute('''
                   ''')
print(2)

# ================================================================
# Main Execution
# ================================================================
# Loads TSV data and processes it:
def main():
    conn = setup_database() # Initialize database connection and create tables
    
    # Import TSV data
    # Load TSV file into a DataFrame, as from tab-separated values
    df = pd.read_csv(tsv_file_path, sep='\t')
    df.to_sql('associations', conn, if_exists='replace', index=False) # Insert into associations table
    conn.commit()

    ihs = pd.read_csv(ihs_file_path, sep = '\t')
    ihs.to_sql('ihs_stat', conn, if_exists='replace',index= False )
    conn.commit()
    print(5)

    # Load uniprot_data.tsv (UniProt Mappings)
    # Load uniprot_data.tsv
    uniprot_df = pd.read_csv(uniprot_path, sep='\t')
    # Fetch existing gene mappings from the database
    gene_mapping_query = "SELECT gene_id, gene_name FROM gene"
    gene_mapping = pd.read_sql_query(gene_mapping_query, conn)
    gene_mapping_dict = dict(zip(gene_mapping["gene_name"], gene_mapping["gene_id"]))
    # Map gene_name to mapped_gene_id using the gene table
    uniprot_df["mapped_gene_id"] = uniprot_df["gene_name"].map(gene_mapping_dict)
    # Insert updated data into uniprot_data, ensuring 'mapped_gene_id' is populated
    uniprot_df.to_sql('uniprot_data', conn, if_exists='replace', index=False)

    # Loads global population metadata (geographical locations, genetic diversity) & stores it in population_glb.
    glb = pd.read_csv(details_glb, sep = '\t')
    glb.to_sql('population_glb', conn, if_exists= 'replace', index=False)   # Insert into 'population_glb'
    conn.commit()
    
    # Reads genetic differentiation (FST) data from a CSV file.
    fst = pd.read_csv(fst_file_path, sep = ',')
    fst.to_sql('fst', conn, if_exists='replace', index = False )
    conn.commit()

    print(3)

    # Reads sub-population data from sub_population.tsv & Stores it in sub_population_details.
    sub = pd.read_csv(subpopuplation, sep = '\t')
    sub.to_sql('sub_population_details', conn, if_exists='replace', index = False ) # Insert into 'sub_population_details'
    conn.commit()
    print(4)

    # Process data
    process_populations(conn) # Extract unique populations from associations
    process_genes(conn) # Extract genes and insert them into the gene table
    process_snps(conn)  # Extract SNPs and insert them into the snp table
    process_allele_frequencies(conn)    # Extract allele frequencies and insert into snp_population_selection_stats

    conn.close()
    print("Database population completed successfully!")

if __name__ == "__main__":
    main()
