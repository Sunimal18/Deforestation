document.addEventListener("DOMContentLoaded", function () {
    // ==========================================
    // 1. DATA STORES & LAYERS INITIALIZATION
    // ==========================================
    var map = L.map('overview-map').setView([8.4583, 80.0417], 11);

    // Esri World Imagery (Satellite) tiles
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP'
    }).addTo(map);

    // Layer Groups
    var disturbanceLayer = L.layerGroup().addTo(map);
    var riskLayer = L.layerGroup().addTo(map);
    var reforestationLayer = L.layerGroup().addTo(map);

    // Data containers
    var rawDisturbances = null;
    var rawRiskAreas = null;
    var currentFilteredDisturbances = [];
    var reforestationSites = [
        { name: "Reforestation Site A", coords: [8.4900, 80.0100], targetArea: 15, status: "Ongoing" },
        { name: "Reforestation Site B", coords: [8.4200, 80.0800], targetArea: 8, status: "Planned" }
    ];

    // Helpers
    function getSeverityColor(severity) {
        switch (severity) {
            case 'high': return '#ef4444';
            case 'moderate': return '#f59e0b';
            case 'low': return '#3b82f6';
            default: return '#10b981';
        }
    }

    function getRiskColor(level) {
        switch (level) {
            case 'high': return '#dc2626';
            case 'medium': return '#d97706';
            case 'low': return '#16a34a';
            default: return '#cbd5e1';
        }
    }

    function getFeatureCenter(feature) {
        if (!feature.geometry || !feature.geometry.coordinates) return [8.4583, 80.0417];
        var coords = feature.geometry.coordinates[0];
        if (feature.geometry.type === 'MultiPolygon') {
            coords = feature.geometry.coordinates[0][0];
        }
        var sumLat = 0, sumLng = 0;
        for (var i = 0; i < coords.length; i++) {
            sumLng += coords[i][0];
            sumLat += coords[i][1];
        }
        return [sumLat / coords.length, sumLng / coords.length];
    }

    function getRegion(lat, lng) {
        if (lat > 8.47) return 'North Sector';
        if (lat < 8.43) return 'South Sector';
        if (lng > 80.06) return 'East Sector';
        if (lng < 80.02) return 'West Sector';
        return 'Central Zone';
    }

    // ==========================================
    // 2. CHART INSTANCES INITIALIZATION
    // ==========================================
    var ndviCtx = document.getElementById('ndviTrendsChart').getContext('2d');
    var ndviChart = new Chart(ndviCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'NDVI Index',
                data: new Array(12).fill(0.8),
                borderColor: '#16a34a',
                backgroundColor: 'rgba(22, 163, 74, 0.05)',
                fill: true,
                tension: 0.35,
                borderWidth: 3,
                pointBackgroundColor: '#16a34a',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { min: 0.4, max: 0.9, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });

    var distCtx = document.getElementById('disturbanceOverTimeChart').getContext('2d');
    var distChart = new Chart(distCtx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Disturbances',
                data: new Array(12).fill(0),
                backgroundColor: '#ef4444',
                borderRadius: 4,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });

    // ==========================================
    // 3. MAIN FILTERING & RENDERING ENGINE
    // ==========================================
    function filterAndRender() {
        var startDateVal = document.getElementById('filter-start-date').value;
        var endDateVal = document.getElementById('filter-end-date').value;
        var regionVal = document.getElementById('filter-region').value;

        var startDate = startDateVal ? new Date(startDateVal) : new Date('2010-01-01');
        var endDate = endDateVal ? new Date(endDateVal) : new Date('2026-12-31');

        if (!rawDisturbances) return;

        // Clear leaflet layers
        disturbanceLayer.clearLayers();
        riskLayer.clearLayers();
        reforestationLayer.clearLayers();

        // 1. Filter Disturbances
        var filteredDisturbances = rawDisturbances.features.filter(function (feature) {
            var props = feature.properties;
            var center = getFeatureCenter(feature);
            var featureRegion = getRegion(center[0], center[1]);
            
            // Region filter
            if (regionVal !== 'all' && featureRegion !== regionVal) {
                return false;
            }

            // Date filter
            if (props.detection_date) {
                var dDate = new Date(props.detection_date);
                if (dDate < startDate || dDate > endDate) {
                    return false;
                }
            }
            return true;
        });
        currentFilteredDisturbances = filteredDisturbances;

        // 2. Filter Risk Areas (Region filter only)
        var filteredRiskAreas = [];
        if (rawRiskAreas) {
            filteredRiskAreas = rawRiskAreas.features.filter(function (feature) {
                var center = getFeatureCenter(feature);
                var featureRegion = getRegion(center[0], center[1]);
                return regionVal === 'all' || featureRegion === regionVal;
            });
        }

        // 3. Filter Reforestation Sites
        var filteredReforestation = reforestationSites.filter(function (site) {
            var siteRegion = getRegion(site.coords[0], site.coords[1]);
            return regionVal === 'all' || siteRegion === regionVal;
        });

        // ==========================================
        // 4. DRAW MAP OVERLAYS
        // ==========================================
        // Disturbances
        L.geoJSON({ type: "FeatureCollection", features: filteredDisturbances }, {
            style: function (feature) {
                return {
                    color: getSeverityColor(feature.properties.severity),
                    weight: 1.5,
                    fillColor: getSeverityColor(feature.properties.severity),
                    fillOpacity: 0.25
                };
            },
            onEachFeature: function (feature, layer) {
                var props = feature.properties;
                var badgeColor = getRiskColor(props.risk_class.toLowerCase());
                var popupContent = `
                    <div style="font-family: system-ui, -apple-system, sans-serif; font-size: 13px; width: 280px; color: #1e293b;">
                        <h4 style="margin: 0 0 8px 0; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; font-size: 14px; font-weight: 600; display: flex; justify-content: space-between; align-items: center;">
                            <span>Area ${props.area_id}</span>
                            <span style="background: ${badgeColor}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase;">${props.risk_class} Risk</span>
                        </h4>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 6px;">
                            <div style="display: flex; justify-content: space-between;"><b>Area affected:</b> <span>${parseFloat(props.area_ha).toFixed(3)} ha</span></div>
                            <div style="display: flex; justify-content: space-between;"><b>Restoration Priority:</b> <span style="font-weight: 600; color: #059669;">${props.reforestation_priority}</span></div>
                            <div style="display: flex; justify-content: space-between;"><b>Distance to Road:</b> <span>${Math.round(props.road_distance_m).toLocaleString()} m</span></div>
                            <div style="display: flex; justify-content: space-between;"><b>Distance to Village:</b> <span>${Math.round(props.village_distance_m).toLocaleString()} m</span></div>
                            <div style="display: flex; justify-content: space-between;"><b>Distance to Waterway:</b> <span>${Math.round(props.waterway_distance_m).toLocaleString()} m</span></div>
                            <div style="display: flex; justify-content: space-between;"><b>Protected Area:</b> <span>${props.protected_area ? '✅ Yes' : '❌ No'}</span></div>
                            <div style="margin-top: 6px; padding: 8px; background: #f8fafc; border-radius: 6px; border: 1px dashed #cbd5e1; font-size: 11.5px; line-height: 1.4; color: #475569;">
                                <b>XAI Explanation:</b><br>${props.xai_explanation}
                            </div>
                        </div>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        }).addTo(disturbanceLayer);

        // Risk Areas
        L.geoJSON({ type: "FeatureCollection", features: filteredRiskAreas }, {
            style: function (feature) {
                return {
                    color: getRiskColor(feature.properties.risk_level),
                    weight: 1,
                    dashArray: '3, 3',
                    fillColor: getRiskColor(feature.properties.risk_level),
                    fillOpacity: 0.15
                };
            },
            onEachFeature: function (feature, layer) {
                var props = feature.properties;
                layer.bindPopup(`<b>Risk Zone ${props.area_id}</b><br>Score: ${props.risk_score}<br>Factors: ${props.primary_factors}`);
            }
        }).addTo(riskLayer);

        // Reforestation sites
        filteredReforestation.forEach(function (site) {
            L.circle(site.coords, {
                color: '#059669',
                fillColor: '#10b981',
                fillOpacity: 0.35,
                radius: site.targetArea * 80
            }).bindPopup(`<b>${site.name}</b><br>Target: ${site.targetArea} ha<br>Status: ${site.status}`).addTo(reforestationLayer);
        });

        // ==========================================
        // 5. UPDATE METRICS
        // ==========================================
        document.getElementById('metric-disturbances').innerText = filteredDisturbances.length;
        
        var highRiskCount = filteredDisturbances.filter(function(f) {
            return f.properties.severity === 'high';
        }).length;
        document.getElementById('metric-risk').innerText = highRiskCount;

        var totalReforestationArea = filteredReforestation.reduce(function(sum, site) {
            return sum + site.targetArea;
        }, 0);
        document.getElementById('metric-reforestation').innerText = totalReforestationArea + " ha";

        // ==========================================
        // 6. UPDATE CHARTS
        // ==========================================
        var monthlyCounts = new Array(12).fill(0);
        var monthlyNdviSum = new Array(12).fill(0);
        var monthlyNdviCount = new Array(12).fill(0);

        filteredDisturbances.forEach(function (feature) {
            var props = feature.properties;
            if (!props.detection_date) return;
            var dateParts = props.detection_date.split('-');
            var monthIndex = parseInt(dateParts[1]) - 1;
            if (monthIndex >= 0 && monthIndex < 12) {
                monthlyCounts[monthIndex]++;
                var ndviVal = 0.8 + (parseFloat(props.ndvi_change) || 0);
                monthlyNdviSum[monthIndex] += ndviVal;
                monthlyNdviCount[monthIndex]++;
            }
        });

        var monthlyNdviAvg = new Array(12).fill(0.8);
        for (var m = 0; m < 12; m++) {
            if (monthlyNdviCount[m] > 0) {
                monthlyNdviAvg[m] = parseFloat((monthlyNdviSum[m] / monthlyNdviCount[m]).toFixed(2));
            }
        }

        // Update charts data and render
        ndviChart.data.datasets[0].data = monthlyNdviAvg;
        ndviChart.update();

        distChart.data.datasets[0].data = monthlyCounts;
        distChart.update();

        // ==========================================
        // 7. UPDATE DETECTIONS TABLE
        // ==========================================
        var tbody = document.getElementById('detections-table-body');
        tbody.innerHTML = '';

        // Sort filtered disturbances by date desc
        var sortedDetections = filteredDisturbances.slice().sort(function(a, b) {
            return b.properties.detection_date.localeCompare(a.properties.detection_date);
        });

        var displayDetections = sortedDetections.slice(0, 10);

        if (displayDetections.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">No disturbances match current filters.</td></tr>';
        } else {
            displayDetections.forEach(function(feature) {
                var props = feature.properties;
                var center = getFeatureCenter(feature);
                var featureRegion = getRegion(center[0], center[1]);
                
                var badgeClass = props.severity === 'high' ? 'badge-high' : (props.severity === 'moderate' ? 'badge-medium' : 'badge-low');
                var severityTextClass = props.severity === 'high' ? 'text-danger' : (props.severity === 'moderate' ? 'text-warning' : 'text-success');
                var severityLabel = props.severity.charAt(0).toUpperCase() + props.severity.slice(1);

                var tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${props.detection_date}</td>
                    <td>${featureRegion} (${props.area_id})</td>
                    <td><span class="badge ${badgeClass}">${(props.confidence * 100).toFixed(0)}%</span></td>
                    <td class="${severityTextClass} font-medium">${severityLabel}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // ==========================================
    // 8. FETCH INITIAL GEOJSONS & EVENT BINDING
    // ==========================================
    Promise.all([
        fetch('/dashboard/api/disturbances/').then(r => r.json()),
        fetch('/dashboard/api/risk-areas/').then(r => r.json())
    ]).then(function(results) {
        rawDisturbances = results[0];
        rawRiskAreas = results[1];
        
        // Initial render
        filterAndRender();

        // Bind filter event listeners
        document.getElementById('filter-start-date').addEventListener('change', filterAndRender);
        document.getElementById('filter-end-date').addEventListener('change', filterAndRender);
        document.getElementById('filter-region').addEventListener('change', filterAndRender);

        // Bind Monthly Report button
        var btnMonthlyReport = document.getElementById('btn-monthly-report');
        if (btnMonthlyReport) {
            btnMonthlyReport.addEventListener('click', function() {
                var endDateVal = document.getElementById('filter-end-date').value;
                var monthStr = "2026-06"; // Default
                if (endDateVal) {
                    monthStr = endDateVal.substring(0, 7); // Get YYYY-MM
                }
                window.open('/dashboard/reports/monthly/?month=' + monthStr, '_blank');
            });
        }

        // Bind PDF Download button
        var btnDownloadPdf = document.getElementById('btn-download-pdf');
        if (btnDownloadPdf) {
            btnDownloadPdf.addEventListener('click', function() {
                window.print();
            });
        }

        // Bind CSV Export button
        var btnExportCsv = document.getElementById('btn-export-csv');
        if (btnExportCsv) {
            btnExportCsv.addEventListener('click', function() {
                exportFilteredDataToCSV(currentFilteredDisturbances);
            });
        }
    }).catch(function(err) {
        console.error("Error loading GeoJSON datasets for reports:", err);
    });

    // CSV Exporter Helper Function
    function exportFilteredDataToCSV(data) {
        if (!data || data.length === 0) {
            alert("No data available to export.");
            return;
        }
        
        // CSV Headers
        var csvContent = "Area ID,Detection Date,NDVI Change,Area (m2),Severity,Status,Confidence,Region\n";
        
        data.forEach(function(feature) {
            var props = feature.properties;
            var center = getFeatureCenter(feature);
            var region = getRegion(center[0], center[1]);
            
            var row = [
                props.area_id,
                props.detection_date || "",
                props.ndvi_change,
                props.area_m2,
                props.severity,
                props.status,
                props.confidence,
                region
            ].map(function(val) {
                return '"' + String(val).replace(/"/g, '""') + '"';
            }).join(',');
            
            csvContent += row + "\n";
        });
        
        // Download Trigger
        var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        var url = URL.createObjectURL(blob);
        var link = document.createElement("a");
        link.setAttribute("href", url);
        
        var dateStr = new Date().toISOString().slice(0, 10);
        link.setAttribute("download", "Monitoring_Report_" + dateStr + ".csv");
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
});
