document.addEventListener("DOMContentLoaded", () => {
    // 1. Prediction Trend Chart Configuration
    const predictionCtx = document.getElementById('predictionChart');
    let predictionChart = null;

    const fullLabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const fullData = [12, 15, 18, 22, 28, 25, 30, 27, 24, 29, 32, 35];

    if (predictionCtx) {
        predictionChart = new Chart(predictionCtx, {
            type: 'bar',
            data: {
                labels: fullLabels,
                datasets: [{
                    label: 'High Risk Areas',
                    data: fullData,
                    backgroundColor: '#f7933a',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 2. Risk Distribution Pie Chart
    const riskCtx = document.getElementById('riskChart');
    if (riskCtx) {
        new Chart(riskCtx, {
            type: 'pie',
            data: {
                labels: [
                    'High Risk 28%',
                    'Low Risk 30%',
                    'Medium Risk 42%'
                ],
                datasets: [{
                    data: [28, 30, 42],
                    backgroundColor: [
                        '#ef4444',
                        '#fbbf24',
                        '#f7933a'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    // 3. Dynamic Period Filter (Next 6 vs 12 Months)
    const filterPeriod = document.getElementById('filter-period');
    const tableRows = document.querySelectorAll("tbody tr");
    const countBadge = document.getElementById('high-risk-count');

    function updatePeriodFilter() {
        if (!filterPeriod) return;
        const months = filterPeriod.value; // "6" or "12"

        // Update prediction trend chart data
        if (predictionChart) {
            if (months === "6") {
                predictionChart.data.labels = fullLabels.slice(0, 6);
                predictionChart.data.datasets[0].data = fullData.slice(0, 6);
            } else {
                predictionChart.data.labels = fullLabels;
                predictionChart.data.datasets[0].data = fullData;
            }
            predictionChart.update();
        }

        // Filter high-risk areas table
        // Next 6 months: only show critical risk threat areas (score >= 75%)
        // Next 12 months: show all threat areas (score >= 60%)
        let visibleCount = 0;
        tableRows.forEach(row => {
            const scoreText = row.querySelector('.risk-bar').nextSibling.textContent.trim();
            const score = parseInt(scoreText) || 0;

            const isVisible = (months === "12" || score >= 75);
            if (isVisible) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        // Update metrics count card
        if (countBadge) {
            countBadge.innerText = visibleCount;
        }
    }

    if (filterPeriod) {
        filterPeriod.addEventListener('change', updatePeriodFilter);
        // Run once on load to ensure initial state matches selection
        updatePeriodFilter();
    }

    // Row Hover Effects
    tableRows.forEach(row => {
        row.addEventListener("mouseenter", () => {
            row.style.background = "#f9fafb";
        });

        row.addEventListener("mouseleave", () => {
            row.style.background = "transparent";
        });
    });
});
