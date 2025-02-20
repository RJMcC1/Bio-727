from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__, static_folder="static")

def query_database(query, params=()):
    """Helper function to query the database."""
    conn = sqlite3.connect("genetics.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    search_type = request.args.get("type")
    query_value = request.args.get("query")
    
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
    
    if search_type == "snp":
        query = base_query + "WHERE snp.snp_name = ?"
        results = query_database(query, (query_value,))
    
    elif search_type == "chromosome":
        query = base_query + "WHERE snp.chromosome = ? ORDER BY snp.start_position"
        results = query_database(query, (query_value,))
    
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
    
    elif search_type == "gene":
        query = base_query + "WHERE gene.gene_name = ?"
        results = query_database(query, (query_value,))
    
    elif search_type == "population":
        query = base_query + "WHERE population.population_name = ?"
        results = query_database(query, (query_value,))
    
    else:
        results = []

    return jsonify(results)

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/gene/<gene_name>")
def gene_page(gene_name):
    """Serve the gene details page"""
    results = query_database("""
        SELECT gene_name, functional_term, ontology_term 
        FROM gene 
        WHERE gene_name = ?
    """, (gene_name,))
    
    return render_template("gene.html", gene_name=gene_name)

@app.route("/population/<population_name>")
def population_page(population_name):
    """Serve the population details page"""
    results = query_database("""
        SELECT population_name, sampling_location 
        FROM population 
        WHERE population_name = ?
    """, (population_name,))
    
    return render_template("population.html", population_name=population_name)

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

if __name__ == "__main__":
    app.run(debug=True)