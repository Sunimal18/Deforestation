# Draft Thesis Sections: Web-Based Decision Support System & Integration

This document contains the drafted sections for your thesis covering the Methodology (Chapter 3) and Implementation (Chapter 4) of the web-based decision-support system, database architecture, and frontend portal for the **LK-FOREST** project.

---

# CHAPTER 3: METHODOLOGY

## 3.11 Web-Based Decision Support System
To translate the geospatial findings, deep learning model segmentations, and GIS-based risk assessments of the LK-FOREST framework into actionable management outcomes, a web-based decision support system (DSS) was designed. The primary objective of this system is to provide forest managers, rangers, and conservation administrators with an interactive, intuitive, and centralized dashboard. This portal integrates analytical outputs into a unified visual environment, mitigating the typical fragmentation of remote sensing studies and enabling data-driven conservation planning in Wilpattu National Park.

```
+-----------------------------------------------------------------------+
|                             USER PORTAL                               |
|       (Dashboard, Disturbance, Risk Prediction, Reforestation)        |
+------------------------------------+----------------------------------+
                                     |
                                HTTP | Requests
                                     v
+------------------------------------+----------------------------------+
|                           DJANGO BACKEND                              |
|          (URL Router, Controllers/Views, JSON Serializers)           |
+------------------------------------+----------------------------------+
                                     |
                        ORM Queries  |  REST API Calls
                                     v
+------------------------------------+----------------------------------+
|                         DATABASE LAYER                                |
|        (Supabase PostgreSQL & PostGIS, GeoJSON API Endpoints)         |
+-----------------------------------------------------------------------+
```

### 3.11.1 Frontend Architecture
The frontend layer of the LK-FOREST web portal is designed following human-computer interaction (HCI) best practices and modern responsive design patterns. The user interface (UI) is structured using HTML5 for semantic page layout and CSS3 for visual styling, grid systems, and responsiveness. The logic is powered by client-side JavaScript (ES6+), which handles asynchronous data fetching, dynamic template updates, DOM manipulation, map renders, and chart animations.

The layout is split into two primary panels:
1. **The Navigation and Control Panel**: Consisting of a sticky top navigation bar (for site-wide routing across the Dashboard, Disturbance Detection, Risk Prediction, Reforestation, and Reports pages) and a left sidebar that exposes interactive inputs (checkboxes, drop-down menus, and range sliders) to control the visible data.
2. **The Visual and Analytical Panel**: A central grid displaying Leaflet-based interactive maps, dynamic alert feeds, statistical KPI cards, and trend charts.

The design implements a color-coded visual hierarchy to represent data categories consistently:
- **Disturbance Data**: Associated with **Red** alerts and indicators to convey immediate environmental changes.
- **Risk Predictions**: Associated with **Orange** markers to represent warning states and forecasts.
- **Reforestation Sites**: Associated with **Green** elements to convey ongoing and planned restoration efforts.

### 3.11.2 Backend Architecture
The backend is powered by the Django web framework, which follows the Model-View-Template (MVT) design pattern. The backend acts as the middleware and orchestration layer of the LK-FOREST platform, performing several critical functions:
1. **Routing and Security**: Handles incoming HTTP requests, maps them to corresponding controller views, manages user authentication, and secures database connection credentials.
2. **API Endpoint Management**: Serves custom JSON REST APIs that serialize PostgreSQL database records. It filters and structures raw spatial geometries and attributes into standardized GeoJSON formats required by Leaflet.js.
3. **Template Context Binding**: Evaluates user page views and injects server-side context variables (e.g., summary statistics, model confidence scores, and lists of high-risk areas) into HTML templates before rendering.

### 3.11.3 Database Architecture
The database layer uses Supabase, a cloud-hosted PostgreSQL platform. It stores both relational attributes and vector geospatial geometries. Using a PostgreSQL database provides high reliability, ACID compliance, and robust querying capabilities. 
The geospatial data structure is represented in two main tables:
1. `disturbance_polygons`: Stores features detected by the hybrid algorithm, including geometry, detection date, area in hectares, priority levels, and XAI explanations.
2. `risk_predictions`: Stores prediction outputs, risk scores, threat categories, primary degradation factors, and automatically generated threat action recommendations.

Data exchange between the database and frontend is mediated through Django's Object-Relational Mapping (ORM) and RESTful API endpoints. Geometries are extracted as GeoJSON feature collections, ensuring compatibility with client-side mapping engines.

### 3.11.4 Interactive Dashboard Design
The dashboard is designed as a centralized monitoring center, containing two key visualization engines:
1. **Interactive Mapping Engine (Leaflet.js)**: Displays forest segments as styled vector polygons overlaid on standard map tiles. It allows users to toggle layer visibilities (Disturbance, Risk Prediction, Reforestation) in the sidebar. Clicking on a polygon triggers a popup detailing the segment's ID, affected area size, proximity to roads/settlements/water, and an XAI-generated explanation text.
2. **Analytical Charting Engine (Chart.js)**: Renders bar, line, and pie charts to summarize dataset distributions. The charts are configured to adapt dynamically based on sidebar filter selections, resizing their visual components to prevent overlap or visual clutter.

---

## 3.12 Automated Monitoring Workflow
To minimize manual labor and delays in identifying forest disturbances, the LK-FOREST framework implements an automated spatial data pipeline. This pipeline describes how raw satellite imagery is ingested, analyzed, classified, and published.

```
+------------------+     +-----------------------+     +-----------------------+
|  Sentinel-2 GEE  | --> | Hybrid Index Differ.  | --> |  U-Net Segmentation   |
| Image Ingestion  |     | (NDVI, NBR, FDVI Mask)|     |  (Pixel Delineation)  |
+------------------+     +-----------------------+     +-----------------------+
                                                                   |
                                                                   v
+------------------+     +-----------------------+     +-----------------------+
|  User Dashboard  | <-- |  XAI & Recommendation | <-- | Raster-to-Vector GIS  |
|  (Map & Alerts)  |     |   (Rule-Based Text)   |     | (Polygon Extraction)  |
+------------------+     +-----------------------+     +-----------------------+
```

### 3.12.1 Data Acquisition Workflow
Multispectral imagery is acquired automatically from the Sentinel-2 constellation via Google Earth Engine (GEE). A spatial filter is applied using the coordinates of Wilpattu National Park to crop images to the study area boundaries. A temporal filter selects images matching specified baseline and evaluation dates. To filter out low-quality data, a cloud-masking filter based on the QA60 band excludes scenes containing cloud cover above a 10% threshold.

### 3.12.2 Processing Workflow
Once high-quality images are loaded, they undergo a series of preprocessing and analysis steps:
1. **Spectral Index Differencing**: The red (B4), green (B3), blue (B2), near-infrared (B8), and shortwave infrared (B11, B12) bands are extracted. The system calculates baseline and current values for the Normalized Difference Vegetation Index (NDVI), Normalized Burn Ratio (NBR), and Forest Disturbance Vegetation Index (FDVI). Difference maps are generated by subtracting the baseline index from the current index.
2. **Hybrid Mask Fusion**: Threshold filters are applied to the difference maps to identify pixels with significant vegetation loss. The binary outcomes are combined using logical operations to build a robust hybrid disturbance mask.
3. **U-Net Segmentation & Polygon Delineation**: The preprocessed Sentinel-2 patches (256 × 256 pixels) are fed into the trained U-Net model to refine pixel-level boundaries. The resulting binary raster is converted to vector polygons using connectivity analysis.
4. **Attribute Enrichment & Explainability**: GIS spatial algorithms calculate proximity values (distance to roads, villages, water bodies) for each polygon. These variables are evaluated through the rule-based explainability module, which maps numerical attributes to structured text templates to generate human-readable explanations and threat action recommendations.

### 3.12.3 System Integration Workflow
Once the vector polygons and attributes are compiled, they are written to the Supabase database. The database issues notifications to the Django backend, which updates its local cache. When a client browser requests the dashboard, the server renders the templates and fires AJAX requests to load the GeoJSON datasets. Leaflet.js renders the boundaries, and client-side listeners bind the elements, completing the end-to-end monitoring chain.

---

# CHAPTER 4: IMPLEMENTATION OF THE RESEARCH

## 4.12 Frontend Implementation
The frontend portal was implemented as a multi-page web application within the Django template structure. To avoid layout shifts and ensure high performance, standard HTML5 semantic elements (such as `<nav>`, `<aside>`, `<main>`, and `<section>`) and custom CSS styling rules were implemented. 

The styling system defined layout grids and responsive sizing:
```css
.dashboard-container {
    display: flex;
    height: 100vh;
}
.center-panel {
    flex: 1;
    padding: 20px;
}
.right-panel {
    width: 320px;
    background: white;
    border-left: 1px solid #ddd;
    overflow-y: auto;
}
```
Navigation is styled via `navbar.css`, using a sticky configuration to remain accessible during vertical scrolls. Global layout cards, tables, and buttons use transition transformations to deliver a premium, fluid aesthetic:
```css
.stat-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
```

The navbar includes the project's official logo (`static/images/logo.PNG`), replacing the previous simple text placeholder. The image styling coordinates dimensions and fits using standard constraints:
```css
.logo-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 8px;
}
```

---

## 4.13 Database Implementation
The database schema was implemented in Supabase, using standard PostgreSQL. Spatially enabled queries are managed through PostGIS extensions. The connection is established via the `psycopg2` Python connector in Django.

The table structure for storing polygons and assessment attributes is modeled as follows:
```sql
CREATE TABLE disturbance_polygons (
    id SERIAL PRIMARY KEY,
    area_id VARCHAR(50) NOT NULL,
    polygon_id INTEGER NOT NULL,
    area_ha DOUBLE PRECISION NOT NULL,
    reforestation_priority VARCHAR(50) NOT NULL,
    road_distance_m DOUBLE PRECISION NOT NULL,
    village_distance_m DOUBLE PRECISION NOT NULL,
    waterway_distance_m DOUBLE PRECISION NOT NULL,
    protected_area BOOLEAN NOT NULL,
    xai_explanation TEXT NOT NULL,
    geom geometry(Polygon, 4326) NOT NULL
);
```
Geometries are stored in standard EPSG:4326 (WGS 84) coordinate reference system. Django views pull these records using native database adapters and serialize them into standard GeoJSON structures.

---

## 4.14 Dashboard Development
The dashboard interface was developed by integrating Leaflet.js (v1.9) mapping elements and Chart.js (v4.0) charting tools.

### 4.14.1 Leaflet.js Mapping Layer Configuration
The Leaflet map is initialized centered on Wilpattu National Park (`[8.4583, 80.0417]`) with an initial zoom level of 11:
```javascript
var map = L.map('map').setView([8.4583, 80.0417], 11);
```
Three separate `L.layerGroup` instances are initialized to manage layers independently: `disturbanceLayer`, `riskLayer`, and `reforestationLayer`. The layers are loaded via async fetch calls to the Django API, styled using custom category colors, and bound to popups:
```javascript
L.geoJSON(data, {
    style: function (feature) {
        return {
            color: getSeverityColor(feature.properties.severity),
            weight: 2,
            fillColor: getSeverityColor(feature.properties.severity),
            fillOpacity: 0.3
        };
    },
    onEachFeature: function (feature, layer) {
        // Register layer globally by area_id
        if (feature.properties.area_id) {
            window.mapAreaLayers[feature.properties.area_id] = layer;
        }
        layer.bindPopup(buildPopupHTML(feature.properties));
    }
}).addTo(disturbanceLayer);
```

### 4.14.2 Color-Coded Checkbox Implementation
The sidebar layer controls were styled to match their corresponding map features using CSS `accent-color` declarations, which apply custom themes to the default browser checkboxes:
```css
#layer-disturbance {
    accent-color: #ef4444; /* Red */
}
#layer-risk {
    accent-color: #f97316; /* Orange */
}
#layer-reforestation {
    accent-color: #10b981; /* Green */
}
```
We modified `.sidebar label` as a flex container with a `8px` gap, ensuring input indicators and descriptive text align vertically:
```css
.sidebar label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}
```

### 4.14.3 Dynamic Alert Clicking and Auto-Zoom
To link the right-hand alert panel to the central map, a document-level click handler was implemented. When an alert card is clicked, the script retrieves its `data-area-id` and `data-alert-type`. It checks if the layer group is active; if not, it toggles the checkbox and adds the layer to the map. The map then zooms to the polygon's boundaries and opens its information popup:
```javascript
document.addEventListener('click', function(e) {
    const card = e.target.closest('.clickable-alert');
    if (card) {
        const areaId = card.getAttribute('data-area-id');
        const alertType = card.getAttribute('data-alert-type');
        window.zoomToArea(areaId, alertType);
    }
});

window.zoomToArea = function(areaId, alertType) {
    // Enable layer group if disabled
    const checkbox = document.getElementById(`layer-${alertType}`);
    if (checkbox && !checkbox.checked) {
        checkbox.checked = true;
        map.addLayer(alertType === 'disturbance' ? disturbanceLayer : riskLayer);
    }
    
    // Zoom and trigger popup
    const layer = window.mapAreaLayers[areaId];
    if (layer) {
        map.fitBounds(layer.getBounds(), { maxZoom: 14 });
        setTimeout(() => { layer.openPopup(); }, 300);
    }
};
```

### 4.14.3 Chart.js Visual Optimization
To show future predictions clearly and prevent bars from becoming too wide in shorter views, the monthly trend chart is configured with a restricted card container height (`280px`) and maximum bar thickness rules:
```javascript
predictionChart = new Chart(predictionCtx, {
    type: 'bar',
    data: {
        labels: labels12,
        datasets: [{
            label: 'High Risk Areas',
            data: data12,
            backgroundColor: '#f7933a',
            borderRadius: 5,
            maxBarThickness: 40 // Capping bar width
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 60, // Shortening bar columns visually
                ticks: { stepSize: 10 }
            }
        }
    }
});
```

---

## 4.15 Automated Workflow Implementation
The automated processing pipeline was implemented using Python automation scripts that connect Google Earth Engine GEE, regional GIS assets, and local database APIs. A cron scheduler triggers a data ingestion script every week. This script queries the Sentinel-2 image collection, applies the cloud filters, stacks bands, runs the index calculations, and saves a composite raster.

This raster is fed into the PyTorch inference model, which runs the U-Net segmentation. The outputs are saved to the vector extraction script, converting pixel clusters to GeoJSON polygons.

---

## 4.16 System Integration
System integration was achieved through unified data serialization. GEE exports and model classifications are consolidated as GeoJSON files that match database table constraints. The Django ORM handles all database insertions, and a shared API router exposes endpoints to the client. This centralized structure ensures that changes to model predictions or map layer selections reflect across all dashboard cards and charts instantly, providing a robust decision-support portal.
