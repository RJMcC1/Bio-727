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
    """
    Searches for an SNP in the database and returns relevant data.
    """
    snp_id = request.args.get('snp')    # Get SNP ID from query parameters
    if not snp_id:
        return jsonify({"error": "Missing SNP ID"}), 400    # Return error if no SNP ID provided

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500    # Return error if database fails to connect
    
    cursor = conn.cursor()

    # Short SQL query to fetch SNP data, along with gene and selection statistics
    query = """
        SELECT snp.snp_name AS snp_id, snp.start_position, snp.p_value, gene.gene_name, ss.average_stat
        FROM snp 
        JOIN gene ON snp.mapped_gene_id = gene.gene_id
        LEFT JOIN selection_statistics_avg_std_dev ss ON snp.snp_id = ss.snp_id
        WHERE snp.snp_name = ?
    """
    cursor.execute(query, (snp_id,))    # Execute query with the provided SNP ID
    snp_data = cursor.fetchall()    # Fetch all matching records
    conn.close()    # Close the database connection
    
    if not snp_data:
        return jsonify({"error": "SNP not found"}), 404 # Return error if SNP is not found
    
    return jsonify([dict(row) for row in snp_data]) # Convert results to JSON and return

# API Endpoint: Fetch Gene Ontology Information
@app.route('/api/gene-ontology', methods=['GET'])
def get_gene_ontology():
    """
    Fetches gene ontology information for a given gene name.
    """
    gene_name = request.args.get('gene') # Get gene name from query parameters
    if not gene_name:
        return jsonify({"error": "Missing gene name"}), 400 # Return error if no gene name provided
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500 # Return error if database fails to connect
    
    cursor = conn.cursor()

    # A SQL query to fetch gene ontology data
    query = """
        SELECT gene_name AS gene, functional_term AS function, ontology_term
        FROM gene
        WHERE gene_name = ?
    """
    cursor.execute(query, (gene_name,)) # Execute query with the provided gene name
    gene_data = cursor.fetchone()   # Fetch the first matching record
    conn.close()    # Close the database connection
    
    if not gene_data:
        return jsonify({"error": "Gene not found"}), 404    # Returns error if gene is not found
    
    return jsonify(dict(gene_data)) # Convert result to JSON and return

# Runs the Flask Application
if __name__ == '__main__':
    app.run(debug=True) # Start the Flask server in debug mode


