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
    console.log("Rendering Chart with Data:", data); // Debugging log, to confirm data being used
    // Get the canvas element where the chart will be drawn
    const canvas = document.getElementById('snpChart');
    // Check if the canvas element exists in the DOM
    if (!canvas) {
        console.error("Chart element not found!"); // Log an error if the canvas is missing
        return;
    }

    // Get the 2D drawing context for the canvas
    const ctx = canvas.getContext('2d');

    // Destroy existing chart before re-drawing, preventing overlapping or duplicate charts when re-rendering.
    if (chartInstance) {
        chartInstance.destroy(); // Clears previous chart instance
    }

    // Create and render a new bar chart using Chart.js
    chartInstance = new Chart(ctx, {
        type: 'bar', // Specify the type of chart (bar chart)
        data: {
            labels: data.labels, // X-axis labels (e.g., SNP IDs)
            datasets: [{
                label: 'Selection Stats', // Legend label
                data: data.values, // Y-axis values (e.g., Selection statistics)
                // Bar and border looks, we can change later to match Z style.
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true, // Ensures the chart resizes dynamically
            scales: {
                y: { beginAtZero: true } // Ensures Y-axis starts at 0
            }
        }
    });

    console.log("Chart Rendered Successfully!"); // Debugging log to confirm successful rendering
}
// Export the renderChart function so it can be used in other modules
export { renderChart };