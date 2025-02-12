import os   # We import OS module for file path operations
import sqlite3  # SQLite3 for database management
from flask import Flask, jsonify, request, send_from_directory  # Import the Flask modules for API functionality
from flask_cors import CORS # Enable Cross-Origin Resource Sharing (CORS)

# Initialize Flask Application
app = Flask(__name__, static_folder="static")   # Defines Flask app with static folder
CORS(app)   # Enable CORS for frontend requests, allow frontend to communicate with the backend (avoids cross-origin issues)

# Get the absolute path to the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# and the SQLite database, to Ensure correct DB path
DB_PATH = os.path.join(BASE_DIR, "genetics.db")

# Database Connection Function
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)    # Connect to database
        conn.row_factory = sqlite3.Row  # Return results as dictionaries
        return conn
    except sqlite3.OperationalError as e: 
        print(f"Database connection error: {e}")    # Logs database connection errors
        return None # Returns a None if connection fails

# Routes for the Serving of Static Files
@app.route("/")
def serve_index():
    """
    Serves the main `index.html` file when the root URL is accessed.
    """
    return app.send_static_file("index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    """
    Serves static files (CSS, JS, images) from the `static` folder.
    """
    return send_from_directory("static", filename)

# API Endpoints: List Available Routes
@app.route('/api/routes', methods=['GET'])
def list_routes():
    """
    Returns a list of all available API routes in JSON format.
    Was useful for debugging and API discovery.
    """
    output = [str(rule) for rule in app.url_map.iter_rules()]   # Extract all routes from the app
    return jsonify({"routes": output})  # Return as JSON response

# API Endpoint: Search for an SNP
@app.route('/api/search', methods=['GET'])
def search_snp():
    snp_id = request.args.get('snp')
    chromosome = request.args.get('chromosome')
    start_pos = request.args.get('start')
    gene_name = request.args.get('gene')

    if start_pos:
        try:
            start_pos = int(start_pos)
        except ValueError:
            return jsonify({"error": "Start position must be an integer"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    query = """
        SELECT snp.snp_name, snp.chromosome, snp.start_position, snp.p_value, 
               gene.gene_name, population.population_name, 
               snp_population_selection_stats.selection_statistic_1, 
               snp_population_selection_stats.selection_statistic_2
        FROM snp 
        LEFT JOIN gene ON snp.mapped_gene_id = gene.gene_id
        LEFT JOIN snp_population_selection_stats ON snp.snp_id = snp_population_selection_stats.snp_id
        LEFT JOIN population ON snp_population_selection_stats.population_id = population.population_id
        WHERE 1=1
    """
    params = []

    if snp_id:
        query += " AND snp.snp_name = ?"
        params.append(snp_id)
    if chromosome:
        query += " AND snp.chromosome = ?"
        params.append(chromosome)
    if start_pos:
        query += " AND snp.start_position >= ?"
        params.append(start_pos)
    if gene_name:
        query += " AND LOWER(gene.gene_name) LIKE LOWER(?)"
        params.append(f"%{gene_name}%")

    cursor.execute(query, tuple(params))
    snp_data = cursor.fetchall()
    conn.close()

    if not snp_data:
        return jsonify({"error": "No SNPs found"}), 404

    return jsonify([dict(row) for row in snp_data])
    
# API Endpoint: Fetch Gene Ontology Information
@app.route('/api/gene-ontology-page/<gene_name>', methods=['GET'])
def gene_ontology_page(gene_name):
    """
    Fetches gene ontology information and renders a template with the data.
    """
    conn = get_db_connection()
    if not conn:
        return render_template('secondpage.html', gene_name=gene_name, function_term_id = None, ontology_term_id = None), 500
    
    cursor = conn.cursor()

    query = """
        SELECT gene_name AS gene, functional_term AS function, ontology_term
        FROM gene
        WHERE gene_name = ?
    """
    cursor.execute(query, (gene_name,))
    gene_data = cursor.fetchone()
    conn.close()
    function_term = None
    ontology_term = None


    if gene_data:
        # If data is found, use the actual data
        function_term = gene_data["function"]
        ontology_term = gene_data["ontology_term"]
    
    return render_template('secondpage.html', 
                           gene_name=gene_data["gene"] if gene_data else gene_name,
                           function_term_id=function_term,
                           ontology_term_id=ontology_term)


# Runs the Flask Application
if __name__ == '__main__':
    app.run(debug=True) # Start the Flask server in debug mode
