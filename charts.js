// Should handle the logic for rendering the charts and visualizations using libraries

// Chart Rendering Logic using Chart.js
// Global variable to keep track of the existing chart instance (prevents duplicates)
let chartInstance = null;

/**
 * Function to render a bar chart using Chart.js
 * @param {Object} data - The data object containing labels and values for the chart
 * @property {Array} data.labels - X-axis labels (SNP identifiers)
 * @property {Array} data.values - Y-axis values (Selection Stats)
 */

// Function to render a chart using Chart.js
function renderChart(data) {
    const ctx = document.getElementById("snpChart").getContext("2d");

    if (chartInstance) {
        chartInstance.destroy(); // Destroy previous chart
    }

    if (data.values.every(v => v === 0)) {
        document.getElementById("chartSection").innerHTML = "<p>No selection statistics available.</p>";
        return;
    }

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Selection Stats",
                data: data.values,
                backgroundColor: "rgba(54, 162, 235, 0.5)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}


function updateChart(selectedPopulation) {
    fetch(`/api/search?population=${selectedPopulation}`)
    .then(response => {
        if (!response.ok) throw new Error("Population data not found");
        return response.json();
    })
    .then(data => {
        if (data.length === 0) {
            console.warn("No data for selected population");
            return;
        }
        renderChart({
            labels: data.map(s => s.snp_name),
            values: data.map(s => s.statistic1)
        });
    })
    .catch(error => console.error("Error fetching population data:", error));
}


// Export the renderChart function so it can be used in other modules
export { renderChart };