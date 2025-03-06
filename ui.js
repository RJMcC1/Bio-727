import { fetchSearchResults, fetchGeneDetails, fetchPopulationDetails } from "./api.js";

console.log("ui.js loaded!"); // Debugging log to verify the script is executing

// Load search results from session storage
document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("resultsTableBody");
    if (!tableBody) return;

    const storedResults = sessionStorage.getItem("searchResults");
    if (storedResults) {
        displayResults(JSON.parse(storedResults));
    }
});

// Helper function to clean gene names
function cleanGeneName(geneName) {
    if (!geneName) return "";
    if (Array.isArray(geneName)) return geneName[0];

    if (typeof geneName === "string") {
        try {
            const parsed = JSON.parse(geneName);
            if (Array.isArray(parsed) && parsed.length > 0) return parsed[0];
        } catch (e) {}
    }
    return geneName;
}

// Handle search form submission
document.getElementById("searchForm")?.addEventListener("submit", async function (event) {
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

// Display search results
function displayResults(results) {
    const tableBody = document.getElementById("resultsTableBody");
    if (!tableBody) return;

    tableBody.innerHTML =
        results.length === 0
            ? "<tr><td colspan='7'>No results found</td></tr>"
            : results
                  .map(
                      (result) => `
            <tr>
                <td>${result[0]}</td>
                <td>${result[1]}</td>
                <td>${result[2]}</td>
                <td>${result[3]}</td>
                <td><a href="/gene/${encodeURIComponent(cleanGeneName(result[4]))}">${cleanGeneName(result[4])}</a></td>
                <td>${result[5]}</td>
                <td><a href="/population/${encodeURIComponent(result[6])}">${result[6]}</a></td>
                <td>${result[7] || "N/A"}</td>
            </tr>`
                  )
                  .join("");
}

// Check if the page is for the SA population
const isSAPopulation = window.location.pathname.includes("/population/SA");

if (isSAPopulation) {
    document.addEventListener("DOMContentLoaded", async () => {
        console.log("✅ DOM Loaded. Populating dropdowns...");

        const ihsChromosomeSelect = document.getElementById("ihsChromosomeSelect");
        const ihsSubpopSelect = document.getElementById("ihsSubpopSelect");
        const fstChromosomeSelect = document.getElementById("fstChromosomeSelect");

        if (!ihsChromosomeSelect || !ihsSubpopSelect || !fstChromosomeSelect) {
            console.error("🚨 Dropdown elements not found in DOM!");
            return;
        }

        console.log("✅ Dropdown elements found. Fetching data...");

        await populateDropdown("/api/chromosomes", ihsChromosomeSelect, "Chromosome");
        await populateDropdown("/api/chromosomes", fstChromosomeSelect, "Chromosome");
        await populateDropdown("/api/subpopulations", ihsSubpopSelect, "Sub-population");

        console.log("✅ All dropdowns populated.");

        ihsChromosomeSelect.addEventListener("change", () => {
            console.log(`🔄 Chromosome selected: ${ihsChromosomeSelect.value}`);
            fetchAndDisplayIHS(1);
        });

        ihsSubpopSelect.addEventListener("change", () => {
            console.log(`🔄 Sub-population selected: ${ihsSubpopSelect.value}`);
            fetchAndDisplayIHS(1);
        });

        fstChromosomeSelect.addEventListener("change", () => {
            console.log(`🔄 FST Chromosome selected: ${fstChromosomeSelect.value}`);
            fetchAndDisplayFST(1);
        });
    });

    async function populateDropdown(apiUrl, dropdown, placeholderText) {
        try {
            console.log(`Fetching data from ${apiUrl}...`);

            const response = await fetch(apiUrl);
            const data = await response.json();

            console.log(`Data received from ${apiUrl}:`, data);

            if (!Array.isArray(data) || data.length === 0) {
                console.error(`❌ Error: No valid data received from ${apiUrl}`);
                return;
            }

            dropdown.innerHTML = `<option value="">-- Select ${placeholderText} --</option>`;
            data.forEach((value) => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = `${placeholderText} ${value}`;
                dropdown.appendChild(option);
            });

            console.log(`✅ Dropdown ${placeholderText} populated successfully.`);

        } catch (error) {
            console.error(`🚨 Error fetching ${placeholderText} data from ${apiUrl}:`, error);
        }
    }

    async function fetchAndDisplayIHS(page = 1) {
        const chromosome = document.getElementById("ihsChromosomeSelect").value;
        const subPopulation = document.getElementById("ihsSubpopSelect").value;
        if (!chromosome) return;

        let url = `/api/ihs?chromosome=${chromosome}&limit=50&offset=${(page - 1) * 50}`;
        if (subPopulation) {
            url += `&sub_population=${subPopulation}`;
        }

        console.log("Fetching IHS data from:", url);

        try {
            const response = await fetch(url);
            const ihsData = await response.json();
            console.log("IHS Data:", ihsData);

            const ihsTableBody = document.getElementById("ihsTable").querySelector("tbody");

            if (!Array.isArray(ihsData) || ihsData.length === 0) {
                ihsTableBody.innerHTML = "<tr><td colspan='6'>No data available</td></tr>";
                return;
            }

            ihsTableBody.innerHTML = ihsData.map(({ Chromosome, Position, iHS_Score, Mean_iHS, Std_iHS, Population }) => `
                <tr>
                    <td>${Chromosome}</td>
                    <td>${Position}</td>
                    <td>${iHS_Score.toFixed(4)}</td>
                    <td>${Mean_iHS.toFixed(4)}</td>
                    <td>${Std_iHS.toFixed(4)}</td>
                    <td>${Population}</td>
                </tr>
            `).join("");

        } catch (error) {
            console.error("Error fetching IHS data:", error);
        }
    }

    async function fetchAndDisplayFST(page = 1) {
        const chromosome = document.getElementById("fstChromosomeSelect").value;
        if (!chromosome) return;

        let url = `/api/fst?chromosome=${chromosome}`;

        console.log("Fetching FST data from:", url);

        try {
            const response = await fetch(url);
            const fstData = await response.json();
            console.log("FST Data:", fstData);

            const fstTableBody = document.getElementById("fstTable").querySelector("tbody");

            if (!Array.isArray(fstData) || fstData.length === 0) {
                fstTableBody.innerHTML = "<tr><td colspan='4'>No data available</td></tr>";
                return;
            }

            fstTableBody.innerHTML = fstData.map(({ Chromosome, Position, SNP, FST }) => `
                <tr>
                    <td>${Chromosome}</td>
                    <td>${Position}</td>
                    <td>${SNP || "N/A"}</td>
                    <td>${FST.toFixed(4)}</td>
                </tr>
            `).join("");

        } catch (error) {
            console.error("Error fetching FST data:", error);
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const fstPopulationSelect = document.getElementById("fstPopulationCompare");

    if (fstPopulationSelect) {
        fstPopulationSelect.addEventListener("change", function () {
            const selectedComparison = this.value;
            fetchFstData(selectedComparison);
        });
    }
});

function fetchFstData(populationComparison) {
    fetch(`/get_fst_data?populationComparison=${populationComparison}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector("#fstTable tbody");
            tableBody.innerHTML = ""; // Clear table before inserting new data

            data.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.Chromosome}</td>
                    <td>${row.Position}</td>
                    <td>${row.SNP}</td>
                    <td>${row.FST}</td>
                `;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error("Error fetching FST data:", error));
}


// Back button handling
document.getElementById("backToResults")?.addEventListener("click", () => window.history.back());