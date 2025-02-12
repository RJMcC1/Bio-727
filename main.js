// Imports functions from other JavaScript files.  
import { fetchSNPData, fetchGeneOntology } from './api.js';
import { renderChart } from './charts.js';
import { updateResultsTable, showGeneOntology, downloadTXT, downloadCSV, setupSearch } from "./ui.js"; 


document.addEventListener('DOMContentLoaded', () => {
    setupSearch();
    document.getElementById("searchType").value = "snp"; // Set default to SNP
    document.getElementById("snpInput").style.display = "block"; // Show SNP input
    document.getElementById("coordinateFields").style.display = "none";
    document.getElementById("geneInput").style.display = "none";
});

document.getElementById("searchType").addEventListener("change", function() {
    document.getElementById("snpInput").style.display = this.value === "snp" ? "block" : "none";
    document.getElementById("geneInput").style.display = this.value === "gene" ? "block" : "none";
    document.getElementById("coordinateFields").style.display = this.value === "coordinates" ? "block" : "none";
});


document.getElementById("searchForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const searchType = document.getElementById("searchType").value; // Get selected search type
    let queryParam = '';

    if (searchType === 'snp') {
        const snpValue = document.getElementById("snpInput").value.trim();
        console.log("SNP Search Triggered:", snpValue); // Debugging log
        if (!snpValue) {
            alert("Please enter a valid SNP.");
            return;
        }
        queryParam = `snp=${snpValue}`;
    } else if (searchType === 'coordinates') {
        const chr = document.getElementById("chromosomeInput").value.trim();
        const start = document.getElementById("startInput").value.trim();
        console.log("Coordinates Search Triggered:", chr, start); // Debugging log
        if (!chr || !start) {
            alert("Please enter chromosome and start position.");
            return;
        }
        queryParam = `chromosome=${chr}&start=${start}`;
    } else if (searchType === 'gene') {
        const geneValue = document.getElementById("geneInput").value.trim();
        console.log("Gene Search Triggered:", geneValue); // Debugging log
        if (!geneValue) {
            alert("Please enter a valid Gene Name.");
            return;
        }
        queryParam = `gene=${geneValue}`;
    }

    if (!queryParam) {
        alert("Please enter search criteria.");
        return;
    }

    try {
        console.log("Fetching SNP data for:", queryParam); // Debugging log
        const response = await fetch(`/api/search?${queryParam}`);
        console.log("Response received:", response);

        if (!response.ok) {
            throw new Error("Data not found");
        }

        const data = await response.json();
        console.log("Parsed data:", data);

        if (!data || data.length === 0) {
            alert("No SNP data found.");
            return;
        }

        updateResultsTable(data);
        renderChart({
            labels: data.map(s => s.snp_name),
            values: data.map(s => s.selection_statistic_1 || 0)
        });

    } catch (error) {
        console.error("Error fetching SNP data:", error);
        alert("Failed to retrieve SNP data. Please try again later.");
    }
});


document.getElementById("resultsTable").addEventListener("click", async (event) => {
    if (event.target.classList.contains("gene-link")) {
        event.preventDefault();
        const geneName = event.target.dataset.gene;
        window.location.href = `/api/gene-ontology-page/${geneName}`;

        try {
            const geneData = await fetchGeneOntology(geneName);
            if (geneData) {
                showGeneOntology(geneData);
            } else {
                alert("Gene ontology data not found.");
            }
        } catch (error) {
            console.error("Error fetching gene ontology:", error);
            alert("Failed to retrieve gene ontology data.");
        }
    }
});

async function handleDownload(downloadFunction) {
    try {
        const snpInput = document.getElementById("snpInput").value.trim(); // Define snpInput
        if (!snpInput) {
            alert("Please enter an SNP before downloading.");
            return;
        }

        const snpData = await fetchSNPData(snpInput);
        if (!snpData || snpData.length === 0) {
            alert("No data available for download.");
            return;
        }

        downloadFunction(snpData);
    } catch (error) {
        console.error("Error downloading file:", error);
        alert("Failed to generate the file.");
    }
}
document.getElementById("downloadTXT").addEventListener("click", () => handleDownload(downloadTXT));
document.getElementById("downloadCSV").addEventListener("click", () => handleDownload(downloadCSV));
