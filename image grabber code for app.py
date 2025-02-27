import base64

@app.route("/population/<population_name>")
def population_page(population_name):
    """Serve the population details page with image and information."""
    # Fetch the image associated with the population from the database
    results = query_database("""
        SELECT i.image
        FROM images i
        WHERE i.population = ?
    """, (population_name,))

    print(f"Results for population '{population_name}': {results}")
    
    if results and results[0][0]:
        image_data=results[0][0]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        return render_template("population.html", population_name=population_name, encoded_image=encoded_image)
    else:
        return render_template("population.html", population_name=population_name, encoded_image=None)
