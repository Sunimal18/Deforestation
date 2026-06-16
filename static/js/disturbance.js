document.addEventListener("DOMContentLoaded", function () {

    const trendCtx =
        document.getElementById('trendChart');

    if (trendCtx) {

        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [
                    'Jan',
                    'Feb',
                    'Mar',
                    'Apr',
                    'May',
                    'Jun'
                ],
                datasets: [{
                    label: 'Disturbances',
                    data: [10, 15, 8, 25, 18, 30],
                    borderWidth: 3
                }]
            }
        });
    }

    const ndviCtx =
        document.getElementById('ndviChart');

    if (ndviCtx) {

        new Chart(ndviCtx, {
            type: 'bar',
            data: {
                labels: [
                    'Zone A',
                    'Zone B',
                    'Zone C',
                    'Zone D'
                ],
                datasets: [{
                    label: 'NDVI Change',
                    data: [
                        -0.25,
                        -0.41,
                        -0.12,
                        -0.37
                    ],
                    borderWidth: 1
                }]
            }
        });
    }

    // Interactive severity/status filtering
    const filterSeverity = document.getElementById('filter-severity');
    const filterStatus = document.getElementById('filter-status');
    const rows = document.querySelectorAll('.disturbance-row');

    function filterTable() {
        const severityVal = filterSeverity ? filterSeverity.value : 'all';
        const statusVal = filterStatus ? filterStatus.value : 'all';

        rows.forEach(row => {
            const rowSeverity = row.getAttribute('data-severity');
            const rowStatus = row.getAttribute('data-status');

            const severityMatch = (severityVal === 'all' || rowSeverity === severityVal);
            const statusMatch = (statusVal === 'all' || rowStatus === statusVal);

            if (severityMatch && statusMatch) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    if (filterSeverity) filterSeverity.addEventListener('change', filterTable);
    if (filterStatus) filterStatus.addEventListener('change', filterTable);
});