
import sqlite3

def create_database():
    # Connect to database (creates if it doesn't exist)
    conn = sqlite3.connect('genetics.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables
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

    # Commit changes and close connection
    conn.commit()
    conn.close()

def example_usage():
    conn = sqlite3.connect('genetics.db')
    cursor = conn.cursor()
    
    # Insert sample data
    cursor.execute('''INSERT INTO gene (gene_name, functional_term, ontology_term)
                    VALUES ('BRCA1', 'DNA repair', 'GO:0006281')''')
    
    cursor.execute('''INSERT INTO population (population_name, sampling_location)
                    VALUES ('European', 'Iceland')''')
    
    cursor.execute('''INSERT INTO snp (snp_name, chromosome, start_position, mapped_gene_id)
                    VALUES ('rs123456', '17', 43000000, 1)''')
    
    # Query data
    cursor.execute('''SELECT * FROM gene''')
    print("Genes:")
    print(cursor.fetchall())
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    example_usage()
