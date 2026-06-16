document.addEventListener("DOMContentLoaded", function () {
    // ==========================================
    // 1. LEAFLET MAP & LAYERS INITIALIZATION
    // ==========================================
    var map = L.map('map').setView([8.4583, 80.0417], 11);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Create Layer Groups
    var disturbanceLayer = L.layerGroup().addTo(map);
    var riskLayer = L.layerGroup().addTo(map);
    var reforestationLayer = L.layerGroup().addTo(map);

    // Color helpers
    function getSeverityColor(severity) {
        switch (severity) {
            case 'high': return '#ef4444';
            case 'moderate': return '#f59e0b';
            case 'low': return '#3b82f6';
            default: return '#10b981';
        }
    }

    // Colors for risk levels
    function getRiskColor(level) {
        switch (level) {
            case 'high': return '#dc2626';      // Dark Red
            case 'medium': return '#d97706';    // Dark Yellow/Orange
            case 'low': return '#16a34a';       // Green
            default: return '#cbd5e1';          // Slate
        }
    }

    // Load Disturbances GeoJSON
    var rawDisturbances = null;

    function updateDisturbanceLayer() {
        if (!rawDisturbances) return;
        
        disturbanceLayer.clearLayers();
        
        var startYearSelect = document.getElementById('filter-start-year');
        var endYearSelect = document.getElementById('filter-end-year');
        var slider = document.getElementById('filter-year-slider');
        
        var startYear = startYearSelect ? parseInt(startYearSelect.value) : 2010;
        var endYear = endYearSelect ? parseInt(endYearSelect.value) : 2026;
        
        // Auto-adjust if start > end
        if (startYear > endYear) {
            endYear = startYear;
            if (endYearSelect) endYearSelect.value = startYear;
            if (slider) {
                slider.value = startYear;
                var valEl = document.getElementById('slider-value');
                if (valEl) valEl.innerText = startYear;
            }
        }
        
        // Filter GeoJSON features by year
        var filteredFeatures = rawDisturbances.features.filter(function(feature) {
            if (!feature.properties || !feature.properties.detection_date) return true;
            var dateStr = feature.properties.detection_date; // YYYY-MM-DD
            var year = parseInt(dateStr.substring(0, 4));
            return year >= startYear && year <= endYear;
        });
        
        var filteredData = {
            type: "FeatureCollection",
            features: filteredFeatures
        };
        
        L.geoJSON(filteredData, {
            style: function (feature) {
                return {
                    color: getSeverityColor(feature.properties.severity),
                    weight: 2,
                    fillColor: getSeverityColor(feature.properties.severity),
                    fillOpacity: 0.3
                };
            },
            onEachFeature: function (feature, layer) {
                let props = feature.properties;
                layer.bindPopup(`<b>Area ${props.area_id}</b><br>Severity: ${props.severity.toUpperCase()}<br>NDVI Change: ${props.ndvi_change}<br>Detected: ${props.detection_date}`);
            }
        }).addTo(disturbanceLayer);
    }

    fetch('/dashboard/api/disturbances/')
        .then(response => response.json())
        .then(data => {
            rawDisturbances = data;
            updateDisturbanceLayer();
        })
        .catch(err => console.error("Error loading disturbances in reforestation page:", err));

    // Load Risk Areas GeoJSON
    fetch('/dashboard/api/risk-areas/')
        .then(response => response.json())
        .then(data => {
            L.geoJSON(data, {
                style: function (feature) {
                    return {
                        color: getRiskColor(feature.properties.risk_level),
                        weight: 1.5,
                        dashArray: '4, 4',
                        fillColor: getRiskColor(feature.properties.risk_level),
                        fillOpacity: 0.2
                    };
                },
                onEachFeature: function (feature, layer) {
                    let props = feature.properties;
                    layer.bindPopup(`<b>Risk Area ${props.area_id}</b><br>Score: ${props.risk_score}<br>Level: ${props.risk_level.toUpperCase()}`);
                }
            }).addTo(riskLayer);
        })
        .catch(err => console.error("Error loading risk areas in reforestation page:", err));

    // Load Reforestation Sites
    L.circle([8.4900, 80.0100], {
        color: '#059669',
        fillColor: '#10b981',
        fillOpacity: 0.4,
        radius: 1200
    }).bindPopup('<b>Reforestation Site A</b><br>Target: 15 ha<br>Status: Ongoing').addTo(reforestationLayer);

    L.circle([8.4200, 80.0800], {
        color: '#059669',
        fillColor: '#10b981',
        fillOpacity: 0.4,
        radius: 900
    }).bindPopup('<b>Reforestation Site B</b><br>Target: 8 ha<br>Status: Planned').addTo(reforestationLayer);


    // ==========================================
    // 2. INTERACTIVE SIDEBAR CHECKLIST TOGGLES
    // ==========================================
    function setupToggle(elementId, layerGroup, boxClass) {
        var el = document.getElementById(elementId);
        if (el) {
            el.addEventListener('click', function () {
                this.classList.toggle('active');
                var box = this.querySelector('.' + boxClass);
                
                if (this.classList.contains('active')) {
                    if (box) {
                        box.innerText = '✓';
                        box.style.background = getBoxColor(boxClass);
                    }
                    map.addLayer(layerGroup);
                } else {
                    if (box) {
                        box.innerText = '';
                        box.style.background = '#cbd5e1'; // Grayed out checkbox
                    }
                    map.removeLayer(layerGroup);
                }
            });
        }
    }

    function getBoxColor(boxClass) {
        if (boxClass === 'red-box') return '#ef4444';
        if (boxClass === 'orange-box') return '#f97316';
        if (boxClass === 'green-box') return '#22c55e';
        return '#cbd5e1';
    }

    setupToggle('layer-disturbance', disturbanceLayer, 'red-box');
    setupToggle('layer-risk', riskLayer, 'orange-box');
    setupToggle('layer-reforestation', reforestationLayer, 'green-box');

    // Time Range Filters Event Listeners
    var startYearSelect = document.getElementById('filter-start-year');
    var endYearSelect = document.getElementById('filter-end-year');
    var slider = document.getElementById('filter-year-slider');
    var sliderVal = document.getElementById('slider-value');

    if (startYearSelect) {
        startYearSelect.addEventListener('change', function() {
            updateDisturbanceLayer();
        });
    }

    if (endYearSelect) {
        endYearSelect.addEventListener('change', function() {
            var val = this.value;
            if (slider) slider.value = val;
            if (sliderVal) sliderVal.innerText = val;
            updateDisturbanceLayer();
        });
    }

    if (slider) {
        slider.addEventListener('input', function() {
            var val = this.value;
            if (sliderVal) sliderVal.innerText = val;
            if (endYearSelect) endYearSelect.value = val;
            updateDisturbanceLayer();
        });
    }


    // ==========================================
    // 3. CHART.JS: VEGETATION TRENDS (NDVI)
    // ==========================================
    const ndviCtx = document.getElementById('ndviChart');
    if (ndviCtx) {
        new Chart(ndviCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                datasets: [{
                    label: 'NDVI',
                    data: [0.68, 0.72, 0.70, 0.74, 0.71, 0.69, 0.66, 0.45, 0.40],
                    borderColor: '#059669',
                    backgroundColor: 'rgba(5, 150, 105, 0.08)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointBackgroundColor: '#059669',
                    pointRadius: 3
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
                        min: 0.3,
                        max: 0.9,
                        grid: { color: '#f1f5f9' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
});