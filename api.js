// API Fetch Functions to call our back-end API using fetch()
// api.js - Fetch SNP and Gene Ontology Data from FastAPI Backend

// Function to fetch SNP data from the API
export async function fetchSNPData(snpID) {
    try {
        // Sends a request to the backend API to retrieve SNP data
        const response = await fetch(`/api/search?snp=${snpID}`);
        // Check if the response is valid
        if (!response.ok) {
            throw new Error(`SNP ${snpID} not found`); // Throws error if SNP is not found
        }
        // Convert response to JSON format and return it
        return await response.json();
    } catch (error) {
        console.error("Error fetching SNP data:", error); // Log any errors that occur
        return null; // Return null in case of an error to prevent crashes
    }
}

// Function to fetch Gene Ontology information from the API
export async function fetchGeneOntology(geneName) {
    try {
        // Send a request to the backend API to retrieve gene ontology details
        const response = await fetch(`/api/gene-ontology?gene=${geneName}`);
        // Check if the response is valid
        if (!response.ok) {
            throw new Error(`Gene ${geneName} not found`); // Throws error if gene is not found
        }
        // Convert response to JSON format and return it
        return await response.json();
    } catch (error) {
        console.error("Error fetching Gene Ontology data:", error);
        return null;
    }
}

// TO DO!: NOT FINISHED/TESTED! Demonstrate fetching SNP data and updating the UI
async function loadSNPDetails(snpID) {
    const snpData = await fetchSNPData(snpID);
    if (snpData) {
        console.log("SNP Data:", snpData);
        // Update UI here...
    }
}

async function loadGeneOntology(geneName) {
    const geneData = await fetchGeneOntology(geneName);
    if (geneData) {
        console.log("Gene Ontology Data:", geneData);
        // Update UI here...
    }
}