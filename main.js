// Import the fetchSNPData function from api.js for making API calls, renderChart function from charts.js for rendering charts, 
// and setupSearch function from ui.js for setting up search functionality.

// Importing necessary functions exported from different modules
import { fetchSNPData, fetchGeneOntology } from './api.js';
import { renderChart } from './charts.js';
import { updateResultsTable, showGeneOntology, downloadTXT, downloadCSV, setupSearch } from "./ui.js"; 

// Makes it so the JavaScript code runs only after the HTML document has fully loaded.
document.addEventListener('DOMContentLoaded', () => {
    // Initialises the search functionality
    setupSearch();
});

// Event listener for the SNP search form submission
document.getElementById("searchForm").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent page refreshing / default form submission
    // Gets users input, remove extra spaces
    const snpInput = document.getElementById("snpInput").value.trim();
    console.log("Searching for SNP:", snpInput); // Debugging log
    // Check if the input is empty (tested: works)
    if (!snpInput) {
        alert("Please enter an SNP ID");
        return;
    }
    // Fetch SNP data from the API
    try {
        const response = await fetch(`/api/search?snp=${snpInput}`);
        console.log("API Response Status:", response.status); // Debugging log
        // If response is not OK (error status like 404, 500, etc.), throws an error
        if (!response.ok) {
            throw new Error("SNP not found");
        }
        // Converts the response to JSON format
        const data = await response.json();
        console.log("Received SNP Data:", data); // Debugging log to inspect fetched data

        // Update the results table with fetched SNP data
        updateResultsTable(data);  // Calls UI function to update table
        // Render chart with SNP statistics
        renderChart({
            labels: data.map(s => s.snp_id), // Extracts rhe SNP IDs for labels
            values: data.map(s => s.average_stat || 0) // Extract selection stats (defaults 0 if missing = ensure it doesn't crash)
        });

    } catch (error) {
        console.error("Error fetching SNP data:", error); // Log error details
        alert("Failed to retrieve SNP data. Please try again later."); // Notify the user
    }
});

// Event listener to handle gene link clicks in result table for Gene Ontology part
document.getElementById("resultsTable").addEventListener("click", async (event) => {
    // Checks if the clicked element has the 'gene-link' class
    if (event.target.classList.contains("gene-link")) {
        event.preventDefault(); // Prevents default link behavior
        const geneName = event.target.dataset.gene; // Extract gene name from data attribute
        const geneData = await fetchGeneOntology(geneName); // Fetch gene ontology information
        // Displays the gene ontology information if available
        if (geneData) {
            showGeneOntology(geneData);
        }
    }
});

// Event listeners for for downloading SNP data.

// Handles TXT download button
document.getElementById("downloadTXT").addEventListener("click", async () => {
    // Fetch SNP data based on the user’s current search input
    const snpData = await fetchSNPData(document.querySelector("#searchForm input").value.trim());
    if (snpData) {
        // If data is available, trigger the TXT file download
        downloadTXT(snpData);
    }
});
// Handles CSV download button
document.getElementById("downloadCSV").addEventListener("click", async () => {
    const snpData = await fetchSNPData(document.querySelector("#searchForm input").value.trim());
    if (snpData) {
        downloadCSV(snpData);
    }
});