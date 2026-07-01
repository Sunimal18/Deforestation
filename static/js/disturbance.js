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

    // ==========================================
    // LEAFLET MAP INTEGRATION FOR DISTURBANCES
    // ==========================================
    const mapContainer = document.getElementById('disturbance-map');
    if (mapContainer) {
        var distMap = L.map('disturbance-map').setView([8.4583, 80.0417], 11);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(distMap);

        function getSeverityColor(severity) {
            switch (severity) {
                case 'high': return '#ef4444';
                case 'moderate': return '#f59e0b';
                case 'low': return '#3b82f6';
                default: return '#10b981';
            }
        }

        fetch('/dashboard/api/disturbances/')
            .then(response => response.json())
            .then(data => {
                L.geoJSON(data, {
                    style: function (feature) {
                        var sev = feature.properties.severity || 'low';
                        return {
                            color: getSeverityColor(sev),
                            weight: 2,
                            fillColor: getSeverityColor(sev),
                            fillOpacity: 0.3
                        };
                    },
                    onEachFeature: function (feature, layer) {
                        var props = feature.properties;
                        if (props) {
                            var areaId = props.area_id || 'N/A';
                            var severity = props.severity || 'low';
                            var date = props.detection_date || 'N/A';

                            layer.bindTooltip("<b>Area ID:</b> Area " + areaId, {
                                direction: "top",
                                sticky: true
                            });

                            var popupContent = `
                                <div style="font-family: system-ui, sans-serif; font-size: 13px; color: #1e293b; padding: 4px;">
                                    <h4 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 600; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">Area ID: Area ${areaId}</h4>
                                    <b>Severity:</b> <span style="text-transform: uppercase; font-weight: 700; color: ${getSeverityColor(severity)};">${severity}</span><br>
                                    <b>Detected:</b> ${date}<br>
                                    <b>Area Affected:</b> ${parseFloat(props.area_ha).toFixed(3)} ha
                                </div>
                            `;
                            layer.bindPopup(popupContent);
                        }
                    }
                }).addTo(distMap);
            })
            .catch(error => console.error("Error loading disturbances map:", error));
    }
});