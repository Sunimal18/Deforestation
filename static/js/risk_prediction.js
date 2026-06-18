document.addEventListener("DOMContentLoaded", function () {
    // 1. Prediction Trend Chart Configuration
    const predictionCtx = document.getElementById('predictionChart');
    let predictionChart = null;

    // Future-based predictions starting from July 2026
    const labels12 = ['Jul 26', 'Aug 26', 'Sep 26', 'Oct 26', 'Nov 26', 'Dec 26', 'Jan 27', 'Feb 27', 'Mar 27', 'Apr 27', 'May 27', 'Jun 27'];
    const data12 = [12, 15, 18, 22, 28, 25, 30, 27, 24, 29, 32, 35];

    const labels6 = ['Jul 26', 'Aug 26', 'Sep 26', 'Oct 26', 'Nov 26', 'Dec 26'];
    const data6 = [12, 15, 18, 22, 28, 25];

    if (predictionCtx) {
        predictionChart = new Chart(predictionCtx, {
            type: 'bar',
            data: {
                labels: labels12,
                datasets: [{
                    label: 'High Risk Areas',
                    data: data12,
                    backgroundColor: '#f7933a',
                    borderRadius: 5,
                    maxBarThickness: 40
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 60,
                        ticks: {
                            stepSize: 10
                        }
                    }
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
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // 3. Dynamic Period Filter (Next 6 Months vs Next 12 Months)
    const filterPeriod = document.getElementById('filter-period');
    const headerSuffix = document.getElementById('period-header-suffix');

    function updatePeriodFilter() {
        if (!filterPeriod) return;
        const period = filterPeriod.value;

        if (predictionChart) {
            if (period === '6') {
                predictionChart.data.labels = labels6;
                predictionChart.data.datasets[0].data = data6;
                if (headerSuffix) headerSuffix.innerText = '(Next 6 Months)';
            } else {
                predictionChart.data.labels = labels12;
                predictionChart.data.datasets[0].data = data12;
                if (headerSuffix) headerSuffix.innerText = '(Next 12 Months)';
            }
            predictionChart.update();
        }
    }

    if (filterPeriod) {
        filterPeriod.addEventListener('change', updatePeriodFilter);
    }

    // 4. View Details Dynamic Panel
    const detailPanel = document.getElementById('details-panel');
    const detailTitle = document.getElementById('details-title');
    const detailAreaId = document.getElementById('details-area-id');
    const detailRiskScore = document.getElementById('details-risk-score');
    const detailRiskLevel = document.getElementById('details-risk-level');
    const detailFactors = document.getElementById('details-factors');
    const detailActionText = document.getElementById('details-action-text');

    const detailButtons = document.querySelectorAll('.view-details-btn');

    detailButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            // Extract values from data attributes
            const areaId = this.getAttribute('data-area-id');
            const score = this.getAttribute('data-risk-score');
            const level = this.getAttribute('data-risk-level');
            const factors = this.getAttribute('data-factors');

            // Update details panel elements
            if (detailTitle) detailTitle.innerText = `Detailed Risk Analysis: Area ${areaId}`;
            if (detailAreaId) detailAreaId.innerText = areaId;
            if (detailRiskScore) detailRiskScore.innerText = score;
            if (detailRiskLevel) {
                detailRiskLevel.innerText = level;
                // Change class dynamically based on risk level
                detailRiskLevel.className = 'badge'; // Reset classes
                if (level.toLowerCase() === 'high') {
                    detailRiskLevel.classList.add('high');
                } else if (level.toLowerCase() === 'medium' || level.toLowerCase() === 'moderate') {
                    detailRiskLevel.classList.add('medium');
                } else {
                    detailRiskLevel.classList.add('low');
                }
            }
            if (detailFactors) detailFactors.innerText = factors;

            // Generate a realistic action plan text dynamically
            if (detailActionText) {
                let actionPlan = '';
                if (level.toLowerCase() === 'high') {
                    actionPlan = `Critical danger levels identified for Area ${areaId}. Proximity to roads and human settlement exposes this zone to immediate deforestation threats. Ground patrol deployment is recommended within the next 24 hours, and radar satellite metrics should be analyzed daily.`;
                } else {
                    actionPlan = `Moderate threat levels identified for Area ${areaId}. Primary factors include edge effects and distance from waterways. Buffer zones should be established and patrols conducted weekly to prevent encroachment.`;
                }
                detailActionText.innerText = actionPlan;
            }

            // Display details panel
            if (detailPanel) {
                detailPanel.style.display = 'block';
                // Scroll smoothly to panel
                detailPanel.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Row Hover Effects
    const rows = document.querySelectorAll("tbody tr");
    rows.forEach(row => {
        row.addEventListener("mouseenter", () => {
            row.style.background = "#f9fafb";
        });
        row.addEventListener("mouseleave", () => {
            row.style.background = "transparent";
        });
    });
});
