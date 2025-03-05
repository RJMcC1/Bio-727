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

// Helper function to clean gene names
function cleanGeneName(geneName) {
    if (!geneName) return "";
    if (Array.isArray(geneName)) return geneName[0];

    if (typeof geneName === 'string') {
        const match = geneName.match(/^\["(.+)"\]$/);
        if (match) return match[1];

        try {
            const parsed = JSON.parse(geneName);
            if (Array.isArray(parsed) && parsed.length > 0) return parsed[0];
        } catch (e) {}
    }
    return geneName;
}

// Handle search form submission
document.getElementById("searchForm")?.addEventListener("submit", async function(event) {
    event.preventDefault();
    const searchType = document.getElementById("searchType").value;
    let query;

    if (searchType === "snp") {
        query = document.getElementById("snpInput").value;
    } else if (searchType === "gene") {
        query = `["${document.getElementById("geneInput").value.trim()}"]`;
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
    if (!tableBody) return;

    tableBody.innerHTML = results.length === 0 
        ? "<tr><td colspan='7'>No results found</td></tr>"
        : results.map(result => `
            <tr>
                <td>${result[0]}</td>
                <td>${result[1]}</td>
                <td>${result[2]}</td>
                <td>${result[3]}</td>
                <td><a href="/gene/${encodeURIComponent(cleanGeneName(result[4]))}">${cleanGeneName(result[4])}</a></td>
                <td>${result[5]}</td>
                <td><a href="/population/${encodeURIComponent(result[6])}">${result[6]}</a></td>
                <td>${result[7] || "N/A"}</td>
            </tr>`).join("");
}

// Check if the current page is for the SA population
const isSAPopulation = window.location.pathname.includes("/population/SA");

document.addEventListener("DOMContentLoaded", async () => {
    if (!isSAPopulation) return;

    // Elements for FST
    const fstChromosomeSelect = document.getElementById("fstChromosomeSelect");
    const fstTableBody = document.getElementById("fstTable").querySelector("tbody");
    const fstPrevPageBtn = document.getElementById("fstPrevPage");
    const fstNextPageBtn = document.getElementById("fstNextPage");

    let fstCurrentPage = 1;
    const fstRowsPerPage = 50;

    async function populateFstChromosomeDropdown() {
        try {
            const response = await fetch("/api/chromosomes");
            const chromosomes = await response.json();
            fstChromosomeSelect.innerHTML = '<option value="">-- Select Chromosome --</option>';
            chromosomes.forEach(chrom => {
                const option = document.createElement("option");
                option.value = chrom;
                option.textContent = `Chromosome ${chrom}`;
                fstChromosomeSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error fetching chromosome data:", error);
        }
    }

    async function fetchAndDisplayFST(page = 1) {
        const selectedChromosome = fstChromosomeSelect.value;
        if (!selectedChromosome) return;

        try {
            const response = await fetch(`/api/fst?chromosome=${selectedChromosome}`);
            const fstData = await response.json();
            fstTableBody.innerHTML = "";

            if (fstData.length === 0) {
                fstTableBody.innerHTML = "<tr><td colspan='4'>No data available</td></tr>";
                return;
            }

            const startIdx = (page - 1) * fstRowsPerPage;
            const endIdx = startIdx + fstRowsPerPage;
            const paginatedData = fstData.slice(startIdx, endIdx);

            const fragment = document.createDocumentFragment();
            paginatedData.forEach(({ Chromosome, Position, SNP, FST }) => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${Chromosome}</td>
                    <td>${Position}</td>
                    <td>${SNP || "N/A"}</td>
                    <td>${FST.toFixed(4)}</td>
                `;
                fragment.appendChild(row);
            });

            fstTableBody.appendChild(fragment);
            fstPrevPageBtn.disabled = page === 1;
            fstNextPageBtn.disabled = endIdx >= fstData.length;

        } catch (error) {
            console.error("Error fetching FST data:", error);
        }
    }

    await populateFstChromosomeDropdown();
    fstChromosomeSelect.addEventListener("change", () => fetchAndDisplayFST(1));

    fstPrevPageBtn.addEventListener("click", () => {
        if (fstCurrentPage > 1) fetchAndDisplayFST(--fstCurrentPage);
    });

    fstNextPageBtn.addEventListener("click", () => {
        fetchAndDisplayFST(++fstCurrentPage);
    });
});

// Handle IHS data for SA population
document.addEventListener("DOMContentLoaded", async () => {
    if (!isSAPopulation) return;

    const ihsChromosomeSelect = document.getElementById("ihsChromosomeSelect");
    const ihsSubpopSelect = document.getElementById("ihsSubpopSelect");
    const ihsTableBody = document.getElementById("ihsTable").querySelector("tbody");
    const prevPageBtn = document.getElementById("prevPage");
    const nextPageBtn = document.getElementById("nextPage");

    let currentPage = 1;
    const rowsPerPage = 50;

    async function populateDropdown(url, dropdown, label) {
        try {
            const response = await fetch(url);
            const data = await response.json();
            dropdown.innerHTML = `<option value="">-- Select ${label} --</option>`;
            data.forEach(value => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = value;
                dropdown.appendChild(option);
            });
        } catch (error) {
            console.error(`Error fetching ${label}:`, error);
        }
    }

    await populateDropdown("/api/chromosomes", ihsChromosomeSelect, "Chromosome");
    await populateDropdown("/api/subpopulations", ihsSubpopSelect, "Sub-population");

    ihsChromosomeSelect.addEventListener("change", () => fetchAndDisplayIHS(1));
    ihsSubpopSelect.addEventListener("change", () => fetchAndDisplayIHS(1));

    prevPageBtn.addEventListener("click", () => {
        if (currentPage > 1) fetchAndDisplayIHS(--currentPage);
    });
    nextPageBtn.addEventListener("click", () => {
        fetchAndDisplayIHS(++currentPage);
    });
});

// Back button handling
const backButton = document.getElementById("backToResults");
if (backButton) {
    backButton.addEventListener("click", () => window.history.back());
}