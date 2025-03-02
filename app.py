# Importing Required Modules:
from flask import Flask, render_template, request, jsonify
    # flask create routes and handle requests, render_template renders HTML template dynamically, 
    # request handles query parameters in search requests, jsonify converts database query results into JSON format for API responses.
import sqlite3
    # Connects to the SQLite database to retrieve genetic data
import requests
    # requests: Fetches external data (i.e., UniProt API).
import base64
    # base64: Encodes images from the database into a format suitable for rendering in HTML.
import pandas as pd

# Creates the Flask web application & specifies static files (CSS, JS) directory.
app = Flask(__name__, static_folder="static")


# Search Q Function: opens a connection, executes a query, fetches results, and then closes the connection.
def query_database(query, params=()):
    """Helper function to query the database."""
    conn = sqlite3.connect("genetics.db")   # Connect to the database
    cursor = conn.cursor()  # Create a cursor to execute SQL queries
    cursor.execute(query, params)   # Execute the SQL query with parameters
    results = cursor.fetchall() # Fetch all results
    conn.close() # Close the database connection
    return results # Returns the query results


# Homepage Route: 
@app.route("/")
def index():
    return render_template("index.html") # Renders index.html where user enters SNP search queries.

# SNP Search API Route: API retrieves SNP data from the database based on user search input, uses SQL joins to combine SNP, gene, and population data.
@app.route("/search", methods=["GET"])
def search():
    # Extracts search parameters (type & query) from the request.
    search_type = request.args.get("type")  # Get search type (i.e. snp, gene, population)
    query_value = request.args.get("query") # Get the user's query input
    # Base SQL query joins the SNP, gene, and population tables to retrieve relevant SNP information.
    base_query = """
        SELECT DISTINCT 
            snp.snp_name, 
            snp.chromosome, 
            snp.start_position, 
            snp.end_position, 
            gene.gene_name, 
            snp.p_value, 
            population.population_name 
        FROM snp 
        LEFT JOIN gene ON snp.mapped_gene_id = gene.gene_id 
        LEFT JOIN snp_population_selection_stats ON snp.snp_id = snp_population_selection_stats.snp_id 
        LEFT JOIN population ON snp_population_selection_stats.population_id = population.population_id 
    """
    
    # Search by SNP ID (rsID): Finds the SNP in the database.
    if search_type == "snp":
        query = base_query + "WHERE snp.snp_name = ?"
        results = query_database(query, (query_value,))
    
    # Search by chromosome: Retrieves all SNPs on a given chromosome, sorted by position.
    elif search_type == "chromosome":
        query = base_query + "WHERE snp.chromosome = ? ORDER BY snp.start_position"
        results = query_database(query, (query_value,))
    
    # Search by genomic coordinates: splits input, extracts chromosome, start, and end positions, and queries SNPs in that range
    elif search_type == "coordinates":
        # Parse the coordinate string (format: "chr:start-end")
        try:
            chr_val, pos_range = query_value.split(":")
            start_pos, end_pos = pos_range.split("-")
            query = base_query + """
                WHERE snp.chromosome = ? 
                AND snp.start_position >= ? 
                AND snp.end_position <= ?
                ORDER BY snp.start_position
            """
            results = query_database(query, (chr_val, int(start_pos), int(end_pos)))
        except (ValueError, AttributeError):
            results = []
    
    # Search by gene name: Finds SNPs associated with a given gene
    elif search_type == "gene":
        query = base_query + "WHERE gene.gene_name = ?"
        results = query_database(query, (query_value,))
        
    # Search by population: Finds SNPs observed in a specific population.
    elif search_type == "population":
        query = base_query + "WHERE population.population_name = ?"
        results = query_database(query, (query_value,))
    
    # Converts the query results into JSON format and sends it as a response.
    else:
        results = []
    return jsonify(results)


# Search Results Page: Loads results.html, which displays search results.
@app.route("/results")
def results():
    return render_template("results.html")

# Gene Details Page: fetching data from both the database and UniProt API w/ UniProt API Integration
@app.route("/gene/<path:gene_name>")
def gene_page(gene_name):
    """Serve the gene details page with database and UniProt API data."""
    # Query the database for gene data/details, checks if UniProt data exists in the database
    db_results = query_database(
        """
        SELECT u.uniprot_id, u.uniprot_url, g.functional_term 
        FROM uniprot_data u
        JOIN gene g ON u.mapped_gene_id = g.gene_id
        WHERE u.gene_name = ?
        """,
        (gene_name,)
    )
    # Stores UniProt ID, URL, and function (if available).
    if db_results:
        uniprot_id, uniprot_url, functional_term = db_results[0]  # Extract tuple elements
        gene_name = gene_name.strip("[]").replace('"', '')  # Remove brackets and quotes
        db_data = {
            "uniprot_id": uniprot_id,
            "uniprot_url": uniprot_url,
            "function": functional_term,
    }
    else:
        db_data = None

    
    # Fetch data from UniProt API if gene not found in DB, queries UniProt for gene function and synonyms
    uniprot_data = None
    if not db_data:
        uniprot_api_url = f"https://rest.uniprot.org/uniprotkb/search?query=gene:{gene_name}+AND+organism_id:9606&format=json"
        try:
            response = requests.get(uniprot_api_url)
            response.raise_for_status()
            data = response.json()

            # Extract Gene Function and Synonyms from the UniProt response.
            if data.get("results"):
                entry = data["results"][0]
                function_text = next(
                    (comment.get("texts", [{}])[0].get("value", "N/A")
                     for comment in entry.get("comments", []) if comment.get("commentType") == "FUNCTION"),
                    "N/A"
                )
                synonyms = [synonym["value"] for gene in entry.get("genes", []) for synonym in gene.get("synonyms", [])]

                uniprot_data = {
                    "accession": entry.get("primaryAccession", "N/A"),
                    "function": function_text,
                    "synonyms": synonyms if synonyms else ["N/A"],
                    "gene_name": gene_name,
                }
        except requests.exceptions.RequestException as e:
            print(f"UniProt API error: {e}")
    # Sends data to gene.html for rendering.
    return render_template("gene.html", gene_name=str(gene_name).strip("[]").replace('"', ''), db_data=db_data, uniprot_data=uniprot_data)



# Population Details Page: 

@app.route("/population/<population_name>")
def population_page(population_name):
    """Fetch population details from SQL tables and render them on the population page."""

    # Query main population details
    population_results = query_database(
    """
    SELECT population_glb.population_name, population_glb.geographical_sampling_locations, 
           population_glb.genetic_diversity, population_glb.disease_trait_associations
    FROM population_glb
    WHERE population_glb.population_name = ?
    """,
    (population_name,))


    # Query sub-population details
    sub_population_results = query_database("""
        SELECT sub_population, genetic_diversity, disease_trait_associations 
        FROM sub_population_details 
        WHERE population = ?
    """, (population_name,))

    # Format main population data
    if population_results:
        pop_name, geo_sampling, genetic_div, disease_traits = population_results[0]
        population_info = {
            "population_name": pop_name,
            "geographical_sampling": geo_sampling,
            "genetic_diversity": genetic_div,
            "disease_traits": disease_traits
        }
    else:
        population_info = None  # No match found

    # Format sub-population data
    sub_populations = []
    if sub_population_results:
        for sub_population in sub_population_results:
            sub_populations.append({
                "sub_population": sub_population[0],
                "genetic_diversity": sub_population[1],
                "disease_traits": sub_population[2]
            })

    return render_template(
        "population.html",
        population_name=population_name,
        population_info=population_info,
        sub_populations=sub_populations
    )
    

# API endpoints for fetching data
@app.route("/api/gene/<gene_name>")
def gene_details(gene_name):
    """API endpoint for getting gene details"""
    results = query_database("""
        SELECT gene_name, functional_term, ontology_term 
        FROM gene 
        WHERE gene_name = ?
    """, (gene_name,))
    return jsonify(results)

@app.route("/api/population/<population_name>")
def population_details(population_name):
    """API endpoint for getting population details"""
    results = query_database("""
        SELECT population_name, sampling_location 
        FROM population 
        WHERE population_name = ?
    """, (population_name,))
    return jsonify(results)

# Runs the Flask app in debug mode.
if __name__ == "__main__":
    app.run(debug=True)