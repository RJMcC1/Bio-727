export async function fetchSearchResults(searchType, query) {
    const response = await fetch(`/search?type=${searchType}&query=${query}`);
    return response.json();
}

export async function fetchGeneDetails(geneName) {
    const response = await fetch(`/api/gene/${encodeURIComponent(geneName)}`);
    return response.json();
}

export async function fetchPopulationDetails(populationName) {
    const response = await fetch(`/api/population/${encodeURIComponent(populationName)}`);
    return response.json();
}