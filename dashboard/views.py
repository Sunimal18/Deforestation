from django.shortcuts import render
from django.http import JsonResponse
import csv
import os
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

def load_disturbance_statistics():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'output', 'Table5_DisturbanceStatistics.csv')
    
    stats = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for row in reader:
                if len(row) >= 2:
                    key = row[0].strip()
                    val = row[1].strip()
                    stats[key] = val
    return stats

def dashboard(request):
    stats = load_disturbance_statistics()
    
    # Parse and clean metrics from Table 5 CSV
    total_disturbances = int(float(stats.get('Total Disturbance Polygons', 0)))
    total_area_ha = stats.get('Total Disturbance Area (ha)', '0.00')
    avg_area_ha = stats.get('Average Polygon Area (ha)', '0.00')
    max_area_ha = stats.get('Maximum Polygon Area (ha)', '0.00')
    
    # Query recent disturbances for the alerts panel
    recent_disturbances = DisturbanceArea.objects.all().order_by('-detection_date')[:2]
    recent_risks = RiskArea.objects.filter(risk_level='high').order_by('-risk_score')[:1]
    
    context = {
        'total_disturbances': total_disturbances,
        'total_area_ha': total_area_ha,
        'avg_area_ha': avg_area_ha,
        'max_area_ha': max_area_ha,
        'recent_disturbances': recent_disturbances,
        'recent_risks': recent_risks,
    }
    return render(request, 'dashboard/dashboard.html', context)

def disturbance_detection(request):
    # Pass metrics to disturbance detection overview
    areas = DisturbanceArea.objects.all().order_by('-detection_date')
    stats = load_disturbance_statistics()
    total_area_ha = stats.get('Total Disturbance Area (ha)', '0.0')
    
    # Legacy compatibility counts
    active_count = areas.filter(status='active').count()
    
    # Average NDVI change mapped from database disturbance score average
    avg_score = 0.0
    if areas.exists():
        import django.db.models as db_models
        avg_score = areas.aggregate(db_models.Avg('disturbance_score'))['disturbance_score__avg'] or 0.0
    avg_ndvi = round(-avg_score, 2)
    
    context = {
        'areas': areas,
        'active_count': active_count,
        'total_area_ha': total_area_ha,
        'avg_ndvi': avg_ndvi,
    }
    return render(request, 'disturbance/disturbance.html', context)

def api_disturbances(request):
    areas = DisturbanceArea.objects.all()
    features = []
    
    for area in areas:
        features.append({
            "type": "Feature",
            "properties": {
                "area_id": area.area_id,
                "polygon_id": area.polygon_id,
                "severity": area.severity,
                "status": area.status,
                "confidence": area.confidence,
                "area_m2": area.area_m2,
                "ndvi_change": area.ndvi_change,
                "detection_date": area.detection_date.strftime('%Y-%m-%d'),
                "area_ha": area.area_ha,
                "road_distance_m": area.road_distance_m,
                "village_distance_m": area.village_distance_m,
                "waterway_distance_m": area.waterway_distance_m,
                "protected_area": area.protected_area,
                "vulnerability_score": area.vulnerability_score,
                "disturbance_score": area.disturbance_score,
                "risk_score": area.risk_score,
                "risk_class": area.risk_class,
                "reforestation_suitability": area.reforestation_suitability,
                "reforestation_priority": area.reforestation_priority,
                "xai_explanation": area.xai_explanation,
            },
            "geometry": area.geometry
        })
        
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return JsonResponse(geojson)

def reports(request):
    return render(request, 'dashboard/reports.html')

def api_risk_areas(request):
    areas = RiskArea.objects.all()
    features = []
    
    for area in areas:
        features.append({
            "type": "Feature",
            "properties": {
                "area_id": area.area_id,
                "risk_score": area.risk_score,
                "risk_level": area.risk_level,
                "primary_factors": area.primary_factors,
            },
            "geometry": area.geometry
        })
        
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return JsonResponse(geojson)