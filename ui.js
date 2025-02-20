import { fetchSearchResults, fetchGeneDetails, fetchPopulationDetails } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("resultsTableBody");

    if (!tableBody) {
        console.error("Error: Results table body not found! Check if results.html is loaded.");
        return;
    }

    const storedResults = sessionStorage.getItem("searchResults");
    if (storedResults) {
        displayResults(JSON.parse(storedResults));
    }
});

// Handle search form submission
document.getElementById("searchForm")?.addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const searchType = document.getElementById("searchType").value;
    let query;
    
    if (searchType === "snp") {
        query = document.getElementById("snpInput").value;
    } else if (searchType === "gene") {
        query = document.getElementById("geneInput").value;
    } else if (searchType === "population") {
        query = document.getElementById("populationInput").value;
    }
    
    if (!query) return;
    
    const results = await fetchSearchResults(searchType, query);
    displayResults(results);
});

// Display search results function
function displayResults(results) {
    const tableBody = document.getElementById("resultsTableBody");

    if (!tableBody) {
        console.error("Error: Results table body not found in the DOM!");
        return;
    }

    tableBody.innerHTML = ""; // Clear existing rows
    results.forEach(result => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${result[0]}</td>
            <td>${result[1]}</td>
            <td>${result[2]}</td>
            <td>${result[3]}</td>
            <td><a href="/gene/${encodeURIComponent(result[4])}">${result[4]}</a></td>
            <td>${result[5]}</td>
            <td><a href="/population/${encodeURIComponent(result[6])}">${result[6]}</a></td>
        `;
        tableBody.appendChild(row);
    });
}