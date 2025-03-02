export async function fetchSearchResults(searchType, query) {
    console.log(`Fetching search results for: type=${searchType}, query=${query}`); // Debugging

    const response = await fetch(`/search?type=${searchType}&query=${query}`);
    const data = await response.json();

    console.log("Received search data:", data); // Debugging
    return data;
}

// Helper function to clean gene names
function cleanGeneName(geneName) {
    if (Array.isArray(geneName)) {
        return geneName[0];  // Extract first element if it's an array
    }
    return geneName.replace(/^\["|"\]$/g, "");  // Remove brackets and quotes
}

export async function fetchGeneDetails(geneName) {
    const cleanName = cleanGeneName(geneName);
    const response = await fetch(`/api/gene/${encodeURIComponent(cleanName)}`);
    return response.json();
}

export async function fetchPopulationDetails(populationName) {
    const response = await fetch(`/api/population/${encodeURIComponent(populationName)}`);
    return response.json();
}