import sqlite3
import pandas as pd
import json

# ================================================================
# Configuration: Adjust these file paths as needed
# ================================================================
db_file_path = 'genetics.db'
tsv_file_path = 'associations.tsv'  # Update to your TSV file path
uniprot_path = 'uniprot_data.tsv'
fst_file_path = 't2d_snps_with_fst_GIHvsGBR.csv'
# ================================================================
# Database Setup and Table Creation
# ================================================================
def setup_database():
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gene (
            gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_name TEXT NOT NULL,
            functional_term TEXT,
            UNIQUE(gene_name, functional_term)
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
        CREATE TABLE IF NOT EXISTS snp_population_selection_stats (
            snp_id INTEGER NOT NULL,
            population_id INTEGER NOT NULL,
            allele_freq DECIMAL(10,6),
            PRIMARY KEY (snp_id, population_id),
            FOREIGN KEY (snp_id) REFERENCES snp (snp_id),
            FOREIGN KEY (population_id) REFERENCES population (population_id)
        )
    ''')

    # Staging table for TSV import
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
                mapped_gene_id INTEGER,
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


               
    conn.commit()
    return conn

# ================================================================
# Data Processing Functions
# ================================================================
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
    conn.commit()

def process_genes(conn):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO gene (gene_name, functional_term)
        SELECT DISTINCT nearest, consequence
        FROM associations
        WHERE nearest IS NOT NULL
    ''')
    conn.commit()

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

def process_allele_frequencies(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT dbSNP, af FROM associations
        WHERE dbSNP IS NOT NULL AND af IS NOT NULL AND af != ''
    ''')
    snp_af_rows = cursor.fetchall()

    for dbSNP, af_json_str in snp_af_rows:
        try:
            af_dict = json.loads(af_json_str.replace("'", "\""))
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing JSON for {dbSNP}: {e}")
            continue

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


# ================================================================
# Main Execution
# ================================================================
def main():
    conn = setup_database()
    
    # Import TSV data
    df = pd.read_csv(tsv_file_path, sep='\t')
    df.to_sql('associations', conn, if_exists='replace', index=False)
    conn.commit()

    uf = pd.read_csv(uniprot_path, sep = '\t')
    uf.to_sql('uniprot', conn, if_exists= 'replace', index=False)
    conn.commit()

    fst = pd.read_csv(fst_file_path, sep = ',')
    fst.to_sql('fst', conn, if_exists='replace', index = False )
    conn.commit()

    # Process data
    process_populations(conn)
    process_genes(conn)
    process_snps(conn)
    process_allele_frequencies(conn)

    conn.close()
    print("Database population completed successfully!")


if __name__ == "__main__":
    main()

db_file_path= 'genetics.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

image_path = 'download.png'

with open(image_path, 'rb') as file:
	image_data = file.read()

cursor.execute('''

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image BLOB NOT NULL,
    population TEXT NOT NULL,
    FOREIGN KEY (population) REFERENCES population (population_name)
);
''')

cursor.execute('''INSERT INTO images (name, image, population) VALUES (?,?,?) ''', ('download.png',image_data, 'SA'))

conn.commit()

conn.close()

print("image inserted successfully!")
