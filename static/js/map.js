window.mapAreaLayers = {};
var map = L.map('map').setView([8.4583, 80.0417], 11);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Create Layer Groups and add them to the map initially
var disturbanceLayer = L.layerGroup().addTo(map);
var riskLayer = L.layerGroup().addTo(map);
var reforestationLayer = L.layerGroup().addTo(map);
var satelliteLayer = L.layerGroup(); // Loaded lazily on toggle

// Colors for severity levels
function getSeverityColor(severity) {
    switch (severity) {
        case 'high': return '#ef4444';      // Red
        case 'moderate': return '#f59e0b';  // Orange/Amber
        case 'low': return '#3b82f6';       // Blue
        default: return '#10b981';          // Emerald
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

// 1. Fetch and load Disturbance Polygons
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
            if (props.area_id) {
                window.mapAreaLayers[props.area_id] = layer;
            }
            let badgeColor = getRiskColor(props.risk_class.toLowerCase());
            let popupContent = `
                <div style="font-family: system-ui, -apple-system, sans-serif; font-size: 13px; width: 280px; color: #1e293b;">
                    <h4 style="margin: 0 0 8px 0; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; font-size: 14px; font-weight: 600; display: flex; justify-content: space-between; align-items: center;">
                        <span>Area ${props.area_id} (ID: ${props.polygon_id})</span>
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
}

fetch('/dashboard/api/disturbances/')
    .then(response => response.json())
    .then(data => {
        rawDisturbances = data;
        updateDisturbanceLayer();
    })
    .catch(error => console.error("Error fetching disturbance GeoJSON: ", error));

// 2. Fetch and load Risk Prediction Polygons
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
                if (props.area_id) {
                    window.mapAreaLayers[props.area_id] = layer;
                }
                let popupContent = `
                    <div style="font-family: system-ui, -apple-system, sans-serif; font-size: 13px; min-width: 150px;">
                        <h4 style="margin: 0 0 8px 0; color: #111827; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Risk Area ${props.area_id}</h4>
                        <div style="display: grid; gap: 4px;">
                            <div><b>Risk Score:</b> <span style="color: ${getRiskColor(props.risk_level)}; font-weight: 600;">${props.risk_score}</span></div>
                            <div><b>Risk Level:</b> ${props.risk_level.toUpperCase()}</div>
                            <div><b>Primary Factors:</b> ${props.primary_factors}</div>
                        </div>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        }).addTo(riskLayer);
    })
    .catch(error => console.error("Error fetching risk GeoJSON: ", error));

// 3. Mock Reforestation Layer Group (Adding a few green reforestation circles)
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
// LAYER INTERACTIVE TOGGLING (SIDEBAR)
// ==========================================
document.addEventListener("DOMContentLoaded", function() {
    var checkDisturbance = document.getElementById('layer-disturbance');
    var checkRisk = document.getElementById('layer-risk');
    var checkReforestation = document.getElementById('layer-reforestation');

    if (checkDisturbance) {
        checkDisturbance.addEventListener('change', function() {
            if (this.checked) {
                map.addLayer(disturbanceLayer);
            } else {
                map.removeLayer(disturbanceLayer);
            }
        });
    }

    if (checkRisk) {
        checkRisk.addEventListener('change', function() {
            if (this.checked) {
                map.addLayer(riskLayer);
            } else {
                map.removeLayer(riskLayer);
            }
        });
    }

    if (checkReforestation) {
        checkReforestation.addEventListener('change', function() {
            if (this.checked) {
                map.addLayer(reforestationLayer);
            } else {
                map.removeLayer(reforestationLayer);
            }
        });
    }

    var checkSatellite = document.getElementById('layer-satellite');
    var satelliteTileLayer = null;

    if (checkSatellite) {
        checkSatellite.addEventListener('change', function() {
            if (this.checked) {
                if (!satelliteTileLayer) {
                    // Show a visual loading indicator or console log
                    console.log("Fetching satellite imagery tiles from Google Earth Engine...");
                    
                    fetch('/dashboard/api/gee-tile-url/')
                        .then(response => response.json())
                        .then(data => {
                            if (data && data.tile_url) {
                                satelliteTileLayer = L.tileLayer(data.tile_url, {
                                    maxZoom: 19,
                                    attribution: '© Google Earth Engine / Sentinel-2'
                                });
                                satelliteLayer.addLayer(satelliteTileLayer);
                                map.addLayer(satelliteLayer);
                            } else if (data.error) {
                                alert("Google Earth Engine error: " + data.error);
                                checkSatellite.checked = false;
                            }
                        })
                        .catch(error => {
                            console.error("Error fetching GEE tiles:", error);
                            alert("Failed to connect to Google Earth Engine service. Please check your credentials.");
                            checkSatellite.checked = false;
                        });
                } else {
                    map.addLayer(satelliteLayer);
                }
            } else {
                map.removeLayer(satelliteLayer);
            }
        });
    }

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

    // Zoom and highlight area on alert click
    document.addEventListener('click', function(e) {
        const card = e.target.closest('.clickable-alert');
        if (card) {
            const areaId = card.getAttribute('data-area-id');
            const alertType = card.getAttribute('data-alert-type');
            if (areaId) {
                window.zoomToArea(areaId, alertType);
            }
        }
    });
});

window.zoomToArea = function(areaId, alertType) {
    if (alertType === 'disturbance') {
        const checkbox = document.getElementById('layer-disturbance');
        if (checkbox && !checkbox.checked) {
            checkbox.checked = true;
            map.addLayer(disturbanceLayer);
        }
    } else if (alertType === 'risk') {
        const checkbox = document.getElementById('layer-risk');
        if (checkbox && !checkbox.checked) {
            checkbox.checked = true;
            map.addLayer(riskLayer);
        }
    }

    const layer = window.mapAreaLayers[areaId];
    if (layer) {
        if (typeof layer.getBounds === 'function') {
            map.fitBounds(layer.getBounds(), { maxZoom: 14 });
        } else if (typeof layer.getLatLng === 'function') {
            map.setView(layer.getLatLng(), 14);
        }
        setTimeout(() => {
            layer.openPopup();
        }, 300);
    } else {
        console.warn(`Layer for area_id ${areaId} not found.`);
    }
};