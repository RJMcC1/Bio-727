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

// Helper function to clean gene names
function cleanGeneName(geneName) {
    if (Array.isArray(geneName)) {
        return geneName[0];  // Extract first element if it's an array
    }
    return geneName.replace(/^\["|"\]$/g, "");  // Remove brackets and quotes
}


// Display search results function
function displayResults(results) {
    console.log("Displaying results:", results); // Debugging
    const tableBody = document.getElementById("resultsTableBody");

    if (!tableBody) {
        console.error("Error: Results table body not found in the DOM!");
        return;
    }

    tableBody.innerHTML = ""; // Clear previous results

    if (!results || results.length === 0) {
        console.warn("No search results found!");
        tableBody.innerHTML = "<tr><td colspan='7'>No results found</td></tr>";
        return;
    }

    // Add event listeners to gene links after appending rows
  tableBody.querySelectorAll('a[href^="/gene/"]').forEach(link => {
    link.addEventListener('click', async function(event) {
      event.preventDefault();
      const geneId = decodeURIComponent(this.getAttribute('href').replace('/gene/', ''));
      const geneDetails = await fetchGeneDetails(geneId);
      // Now display these details somewhere
      displayGeneDetails(geneDetails);
    });
  });

  console.log(results.map((result => result[4])));

    results.forEach(result => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${result[0]}</td>
            <td>${result[1]}</td>
            <td>${result[2]}</td>
            <td>${result[3]}</td>
            <td><a href="/gene/${encodeURIComponent(cleanGeneName(result[4]))}">${cleanGeneName(result[4])}</a></td>
            <td>${result[5]}</td>
            <td><a href="/population/${encodeURIComponent(result[6])}">${result[6]}</a></td>
        `;
        tableBody.appendChild(row);
    });
}

// Function to download results as a text file
function downloadResultsAsText() {
    const tableBody = document.getElementById("resultsTableBody");
    if (!tableBody) {
        console.error("Results table body not found!");
        return;
    }

    let textContent = "SNP ID\tChromosome\tStart Position\tEnd Position\tGene\tP-Value\tPopulation\n";

    // Loop through table rows and extract text content
    tableBody.querySelectorAll("tr").forEach(row => {
        const rowData = Array.from(row.children).map(cell => cell.textContent.trim()).join("\t");
        textContent += rowData + "\n";
    });

    // Create a Blob and trigger file download
    const blob = new Blob([textContent], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "search_results.txt";
    a.click();
}

// Add event listener to the download button
document.getElementById("downloadResults")?.addEventListener("click", downloadResultsAsText);