// Function to update the SNP results table
/**
 * Updates the SNP results table with new data.
 * @param {Array} snpData - Array of SNP objects containing data to be displayed.
 */
function updateResultsTable(snpData) {
    console.log("Updating Results Table with Data:", snpData); // Debugging log

    const tableBody = document.getElementById("resultsBody");
    // Check if the table body exists
    if (!tableBody) {
        console.error("Error: Table body not found!");
        return;
    }
    
    tableBody.innerHTML = ""; // Clear old results, to insert new data.

    // Loops through SNP data and creates table rows dynamically
    snpData.forEach(snp => {
        const row = `<tr>
            <td>${snp.snp_id}</td> <!-- SNP ID -->
            <td>${snp.start_position}</td> <!-- SNP Genomic Position -->
            <td>${snp.p_value !== null ? snp.p_value : "N/A"}</td> <!-- p-value or N/A -->
            <td><a href="#" class="gene-link" data-gene="${snp.gene_name}">${snp.gene_name}</a></td> <!-- Click gene name for Gene Ontology -->
            <td>${snp.average_stat !== null ? snp.average_stat : "N/A"}</td> <!-- Selection Stats -->
        </tr>`;
        tableBody.insertAdjacentHTML('beforeend', row); // Appends row to table
    });

    console.log("Table Updated Successfully!"); // Debugging log
}

// ===============================
// Function to Display Gene Ontology Information
// ===============================
/**
 * Displays Gene Ontology details for a selected gene.
 * @param {Object} geneData - Object containing gene ontology details.
 */

// Function to display Gene Ontology info
function showGeneOntology(geneData) {
    const geneInfoDiv = document.getElementById("geneInfo");

    // Update the UI with gene ontology details
    geneInfoDiv.innerHTML = `
        <h3>Gene Ontology Info for ${geneData.gene}</h3>
        <p>Function: ${geneData.function}</p>
        <p>Pathways: ${geneData.pathways.join(", ")}</p>
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
    txtContent += data.map(snp => `${snp.snp_id}\t${snp.position}\t${snp.p_value}\t${snp.gene}\t${snp.selection_stat}`).join("\n");

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
            data.map(snp => `${snp.snp_id},${snp.position},${snp.p_value},${snp.gene},${snp.selection_stat}`)
        ).join("\n");

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
    // Add event listener for form submission
    document.getElementById("searchForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        const snpInput = document.getElementById("snpInput").value.trim();
        console.log("Searching for SNP:", snpInput);

        // Validate input: Ensure user has entered an SNP ID
        if (!snpInput) {
            alert("Please enter an SNP ID");
            return;
        }

        try {
            // Fetches SNP data from API
            const response = await fetch(`/api/search?snp=${snpInput}`);
            // Handle errors if SNP is not found
            if (!response.ok) {
                throw new Error("SNP not found");
            }
            const data = await response.json();
            console.log("Received SNP Data:", data); // Debugging log

            // Update table with retrieved SNP data
            updateResultsTable(data);
            // Render chart with SNP statistics
            renderChart({
                labels: data.map(s => s.snp_id),
                values: data.map(s => s.average_stat || 0)
            });

        } catch (error) {
            console.error("Error fetching SNP data:", error);
            alert("Failed to retrieve SNP data. Please try again later.");
        }
    });
}

