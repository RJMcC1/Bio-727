// Function to update the SNP results table
/**
 * Updates the SNP results table with new data.
 * @param {Array} snpData - Array of SNP objects containing data to be displayed.
 */
import { renderChart } from "./charts.js";
import { fetchSNPData, fetchGeneOntology } from "./api.js";

function updateResultsTable(snpData) {
    console.log("Updating Results Table with:", snpData); // Debugging log
    const tableBody = document.getElementById("resultsBody");
    tableBody.innerHTML = ""; // Clear previous results

    if (!snpData || snpData.length === 0) {
        console.warn("No SNP data found.");
        tableBody.innerHTML = "<tr><td colspan='8'>No SNP data found.</td></tr>";
        return;
    }

    snpData.forEach(snp => {
        console.log("Adding row for:", snp.snp_name); // Debugging log
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${snp.snp_name}</td>
            <td>${snp.chromosome}</td>
            <td>${snp.start_position}</td>
            <td>${snp.p_value || "N/A"}</td>
            <td><a href="#" class="gene-link" data-gene="${snp.gene_name}">${snp.gene_name || "N/A"}</a></td>
            <td>${snp.population_name || "N/A"}</td>
            <td>${snp.selection_statistic_1 || "-"}</td>
            <td>${snp.selection_statistic_2 || "-"}</td>
        `;
        tableBody.appendChild(row);
    });

    console.log("Table Updated Successfully!");
}



// Fetch Gene Ontology on Click
document.getElementById("resultsTable").addEventListener("click", async (event) => {
    if (event.target.classList.contains("gene-link")) {
        event.preventDefault();
        const geneName = event.target.dataset.gene;
        
        try {
            const geneData = await fetchGeneOntology(geneName);
            showGeneOntology(geneData);
        } catch (error) {
            console.error("Error fetching Gene Ontology data:", error);
            document.getElementById("geneInfo").innerHTML = `<p>No gene ontology data found.</p>`;
        }
    }
});

document.getElementById("searchType").addEventListener("change", function () {
    document.getElementById("snpInput").style.display = this.value === "snp" ? "block" : "none";
    document.getElementById("geneInput").style.display = this.value === "gene" ? "block" : "none";
    document.getElementById("coordinateFields").style.display = this.value === "coordinates" ? "block" : "none";
});


/**
 * Displays Gene Ontology details for a selected gene.
 * @param {Object} geneData - Object containing gene ontology details.
 */

// Function to display Gene Ontology info
function showGeneOntology(geneData) {
    const geneInfoDiv = document.getElementById("geneInfo");
    if (!geneData) {
        geneInfoDiv.innerHTML = "<p>No Gene Ontology data available.</p>";
        return;
    }
    
    geneInfoDiv.innerHTML = `
        <h3>Gene Ontology Info for ${geneData.gene}</h3>
        <p><strong>Function:</strong> ${geneData.function || "N/A"}</p>
        <p><strong>Pathways:</strong> ${geneData.pathways ? geneData.pathways.join(", ") : "N/A"}</p>
    `;
}

// ===============================
// Function to Enable File Download (TXT Format)
// ===============================
/**
 * Generates and downloads SNP data as a TXT file.
 * @param {Array} data - SNP data to be downloaded.
 */
// Function to enable file download (TXT)
function downloadTXT(data) {
    // Prepare TXT file content with tab-separated values
    let txtContent = "SNP\tPosition\tP-Value\tGene\tSelection Stats\n";
    txtContent += data.map(snp => `${snp.snp_id}\t${snp.position}\t${snp.p_value}\t${snp.gene}\t${snp.selection_statistic_1}\t${snp.selection_statistic_2}`).join("\n");

    // Create a Blob (binary large object) for the file
    const blob = new Blob([txtContent], { type: "text/plain" });
    // Create an invisible download link
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "snp_data.txt";
    // Append to document and trigger download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup: Revoke the URL object to free memory
    setTimeout(() => URL.revokeObjectURL(link.href), 0); // Prevent memory leaks
    document.body.removeChild(link);
}

// ===============================
// Function to Enable File Download (CSV Format)
// ===============================
/**
 * Generates and downloads SNP data as a CSV file.
 * @param {Array} data - SNP data to be downloaded.
 */
// Function to enable file download (CSV)
function downloadCSV(data) {
    // Prepare CSV content with comma-separated values
    const csvContent = "data:text/csv;charset=utf-8," +
        ["SNP,Position,P-Value,Gene,Selection Stats"].concat(
            data.map(snp => `${snp.snp_id}\t${snp.position}\t${snp.p_value}\t${snp.gene}\t${snp.selection_statistic_1}\t${snp.selection_statistic_2}`).join("\n"));

    // Encode CSV content into a downloadable format
    const encodedUri = encodeURI(csvContent);
    // Create an invisible download link
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "snp_data.csv");
    // Append to document and trigger download
    document.body.appendChild(link);
    link.click();
}

// ===============================
// Export Functions for Use in Other Files
// ===============================
export { updateResultsTable, showGeneOntology, downloadTXT, downloadCSV };

// ===============================
// Function to Initialize SNP Search Functionality
// ===============================
// Sets up the search functionality by adding an event listener to the search form.
export function setupSearch() {
    console.log("setupSearch() function executed!"); // Debugging log

    document.getElementById("searchForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        const searchType = document.getElementById("searchType").value;
        let queryParam = '';

        console.log(`Search Type Selected: ${searchType}`); // Debugging log

        if (searchType === 'snp') {
            const snpValue = document.getElementById("snpInput").value.trim();
            console.log("SNP Search Triggered:", snpValue);
            if (!snpValue) {
                alert("Please enter a valid SNP.");
                return;
            }
            queryParam = `snp=${snpValue}`;
        } else if (searchType === 'coordinates') {
            const chr = document.getElementById("chromosomeInput").value.trim();
            const start = document.getElementById("startInput").value.trim();
            console.log("Coordinates Search Triggered:", chr, start);
            if (!chr || !start) {
                alert("Please enter chromosome and start position.");
                return;
            }
            queryParam = `chromosome=${chr}&start=${start}`;
        } else if (searchType === 'gene') {
            const geneValue = document.getElementById("geneInput").value.trim();
            console.log("Gene Search Triggered:", geneValue);
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
            console.log("Fetching SNP data for:", queryParam);
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

            if (searchType === 'snp' || searchType === 'gene') {
                renderChart({
                    labels: data.map(s => s.snp_name),
                    values: data.map(s => s.selection_statistic_1 || 0)
                });
            }

        } catch (error) {
            console.error("Error fetching SNP data:", error);
            alert("Failed to retrieve SNP data. Please try again later.");
        }
    });
}