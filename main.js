import { fetchSearchResults } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded and parsed.");
    
    // Get all necessary DOM elements
    const searchForm = document.getElementById("searchForm");
    const searchType = document.getElementById("searchType");
    const snpInput = document.getElementById("snpInput");
    const geneInput = document.getElementById("geneInput");
    const populationInput = document.getElementById("populationInput");
    const coordinateFields = document.getElementById("coordinateFields");
    const newSearchButton = document.getElementById("newSearchButton");

    if (newSearchButton) {
        newSearchButton.addEventListener("click", () => {
            window.location.href = "/";
        });
    }

    // Exit early if we're on a page without the search form
    if (!searchForm) {
        console.error("Search form not found in DOM!");
        return;
    }


    function updateSearchInput() {
        console.log("Updating search input display...");
        // Hide all inputs first
        snpInput.style.display = "none";
        geneInput.style.display = "none";
        populationInput.style.display = "none";
        coordinateFields.style.display = "none";

        // Show only the relevant input
        if (searchType.value === "snp") snpInput.style.display = "block";
        if (searchType.value === "gene") geneInput.style.display = "block";
        if (searchType.value === "population") populationInput.style.display = "block";
        if (searchType.value === "coordinates") coordinateFields.style.display = "block";
    }

    // Add listener for search type changes
    searchType.addEventListener("change", updateSearchInput);
    
    // Initialize correct input visibility
    updateSearchInput();

    // Handle form submission
    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        let query;
        let type = searchType.value;
    
        // Get the appropriate query value based on search type
        if (type === "snp") {
            query = snpInput.value;
        } else if (type === "gene") {
            query = geneInput.value;
        } else if (type === "population") {
            query = populationInput.value;
        } else if (type === "coordinates") {
            const chromosome = document.getElementById("chromosomeInput").value.trim();
            const start = document.getElementById("startInput").value.trim();
            const end = document.getElementById("endInput").value.trim();
            
            if (!chromosome) {
                alert("Please enter a chromosome number");
                return;
            }
    
            if (start || end) {
                // If either start or end is provided, both must be provided
                if (!start || !end) {
                    alert("Please provide both start and end positions");
                    return;
                }
                // Full coordinate search
                query = `${chromosome}:${start}-${end}`;
            } else {
                // Chromosome-only search
                type = "chromosome";
                query = chromosome;
            }
        }
    
        // Validate query
        if (!query) {
            console.warn("No query provided.");
            return;
        }
    
        console.log("Fetching results for:", type, query);
    
        try {
            // Fetch and store results
            const results = await fetchSearchResults(type, query);
            sessionStorage.setItem("searchResults", JSON.stringify(results));
            
            // Navigate to results page
            window.location.href = "/results";
        } catch (error) {
            console.error("Error fetching results:", error);
            alert("An error occurred while searching. Please try again.");
        }
    });
});

// Function to display results in the table
function displayResults(results) {
    const tableBody = document.getElementById("resultsTableBody");
    
    if (!tableBody) {
        console.error("Results table body not found!");
        return;
    }

    tableBody.innerHTML = ""; // Clear previous results
    
    results.forEach(result => {
        const row = document.createElement("tr");
        // Notice how we're now using /gene?gene= instead of gene.html?gene=
        row.innerHTML = `
            <td>${result[0]}</td>
            <td>${result[1]}</td>
            <td>${result[2]}</td>
            <td>${result[3]}</td>
            <td><a href="/gene?gene=${encodeURIComponent(result[4])}">${result[4]}</a></td>
            <td>${result[5]}</td>
            <td><a href="/population?population=${encodeURIComponent(result[6])}">${result[6]}</a></td>
        `;
        tableBody.appendChild(row);
    });
}