def fetch_ihs_data():
    conn = sqlite3.connect('genetics.db')
    query = "SELECT Chromosome, Position, iHS_Score, Std_iHS_Population FROM ihs_stat"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@app.route("/statistics")
def statistics():
    return render_template("population.html")  # Load the HTML page

@app.route("/statistics/ihs_data")
def get_ihs_data():
    df = fetch_ihs_data()
    data = df.to_dict(orient="records")
    return jsonify(data)  # Return data as JSON

