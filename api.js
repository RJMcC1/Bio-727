// Function to fetch SNP data from the API
export async function fetchSNPData(snpID) {
    try {
        const response = await fetch(`/api/search?snp=${snpID}`);
        if (!response.ok) {
            return { error: `SNP ${snpID} not found` };
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching SNP data:", error);
        return { error: "Server error. Please try again later." };
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