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

def monthly_report(request):
    from django.db.models import Sum, Count, Avg
    from datetime import date
    import json
    
    # Get month parameter, e.g. "2026-06"
    month_param = request.GET.get('month', '2026-06')
    try:
        year, month = map(int, month_param.split('-'))
    except ValueError:
        year, month = 2026, 6
        
    report_date = date(year, month, 1)
    month_name = report_date.strftime('%B %Y')
    
    # 1. Query current month disturbances
    current_disturbances = DisturbanceArea.objects.filter(detection_date__year=year, detection_date__month=month)
    current_count = current_disturbances.count()
    current_area = current_disturbances.aggregate(total=Sum('area_ha'))['total'] or 0.0
    
    # Risk distributions
    high_risk_count = current_disturbances.filter(risk_class__iexact='high').count()
    medium_risk_count = current_disturbances.filter(risk_class__iexact='moderate').count()
    low_risk_count = current_disturbances.filter(risk_class__iexact='low').count()
    
    # Reforestation priority
    high_priority_reforest = current_disturbances.filter(reforestation_priority__iexact='high').count()
    medium_priority_reforest = current_disturbances.filter(reforestation_priority__iexact='medium').count()
    low_priority_reforest = current_disturbances.filter(reforestation_priority__iexact='low').count()
    
    # 2. Query previous month (May 2026) for comparison
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    
    prev_disturbances = DisturbanceArea.objects.filter(detection_date__year=prev_year, detection_date__month=prev_month)
    prev_count = prev_disturbances.count()
    prev_area = prev_disturbances.aggregate(total=Sum('area_ha'))['total'] or 0.0
    
    # Percentage changes
    count_change_pct = 0.0
    if prev_count > 0:
        count_change_pct = ((current_count - prev_count) / prev_count) * 100
        
    area_change_pct = 0.0
    if prev_area > 0:
        area_change_pct = ((current_area - prev_area) / prev_area) * 100
        
    # 3. Top 10 High Risk Disturbances
    top_disturbances = current_disturbances.order_by('-risk_score')[:10]
    
    # 4. Vulnerability Class Counts (using severity categories as class mappings)
    vuln_high = current_disturbances.filter(severity='high').count()
    vuln_mod = current_disturbances.filter(severity='moderate').count()
    vuln_low = current_disturbances.filter(severity='low').count()
    
    # 5. Reforestation Recommendations
    reforest_recommendations = current_disturbances.filter(reforestation_priority__isnull=False).exclude(reforestation_priority='').order_by('-area_ha')[:5]
    
    # 6. Explainability Reports
    xai_reports = current_disturbances.filter(xai_explanation__isnull=False).exclude(xai_explanation='').order_by('-risk_score')[:3]
    
    # 7. Protected Area Impact
    inside_protected = current_disturbances.filter(protected_area=True).count()
    outside_protected = current_disturbances.filter(protected_area=False).count()
    
    # 8. Recommended Field Visits (Patrol routing based on threats)
    field_visits = []
    for idx, dist in enumerate(current_disturbances.order_by('-risk_score')[:5]):
        reasons = []
        if dist.risk_score and dist.risk_score >= 0.70:
            reasons.append("High Risk Score")
        if dist.area_ha and dist.area_ha >= 2.0:
            reasons.append("Large Disturbed Area")
        if dist.protected_area:
            reasons.append("Protected Area Core Impact")
        if dist.village_distance_m and dist.village_distance_m < 800:
            reasons.append("Near Settlement Boundary")
            
        reason_str = " + ".join(reasons) if reasons else "Routine Inspection"
        field_visits.append({
            'site': f"Site {chr(65 + idx)} (Polygon {dist.area_id})",
            'reason': reason_str
        })
        
    # 9. Monthly Trend Analysis (Last 6 Months: Jan to Jun 2026)
    trends = []
    months_list = [
        (2026, 1, 'Jan'),
        (2026, 2, 'Feb'),
        (2026, 3, 'Mar'),
        (2026, 4, 'Apr'),
        (2026, 5, 'May'),
        (2026, 6, 'Jun'),
    ]
    for y, m, name in months_list:
        m_dists = DisturbanceArea.objects.filter(detection_date__year=y, detection_date__month=m)
        trends.append({
            'month': name,
            'count': m_dists.count(),
            'area': round(m_dists.aggregate(total=Sum('area_ha'))['total'] or 0.0, 1)
        })
        
    # 10. GeoJSON features for the map
    features = []
    for dist in current_disturbances:
        features.append({
            "type": "Feature",
            "properties": {
                "area_id": dist.area_id,
                "severity": dist.severity,
                "risk_class": dist.risk_class,
                "area_ha": dist.area_ha,
            },
            "geometry": dist.geometry
        })
    report_geojson = json.dumps({
        "type": "FeatureCollection",
        "features": features
    })
    
    context = {
        'month_param': month_param,
        'month_name': month_name,
        'current_count': current_count,
        'current_area': round(current_area, 1),
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'high_priority_reforest': high_priority_reforest,
        'medium_priority_reforest': medium_priority_reforest,
        'low_priority_reforest': low_priority_reforest,
        'prev_count': prev_count,
        'prev_area': round(prev_area, 1),
        'count_change_pct': round(count_change_pct, 1),
        'area_change_pct': round(area_change_pct, 1),
        'top_disturbances': top_disturbances,
        'vuln_high': vuln_high,
        'vuln_mod': vuln_mod,
        'vuln_low': vuln_low,
        'reforest_recommendations': reforest_recommendations,
        'xai_reports': xai_reports,
        'inside_protected': inside_protected,
        'outside_protected': outside_protected,
        'field_visits': field_visits,
        'trends': trends,
        'report_geojson': report_geojson,
    }
    return render(request, 'dashboard/monthly_report.html', context)


_ee_initialized = False

def initialize_ee():
    global _ee_initialized
    if _ee_initialized:
        return
    import ee
    import json
    import os
    
    gee_credentials_json = os.getenv('GEE_CREDENTIALS_JSON', '')
    if gee_credentials_json:
        credentials_dict = json.loads(gee_credentials_json)
        credentials = ee.ServiceAccountCredentials(
            credentials_dict['client_email'],
            key_data=gee_credentials_json
        )
        ee.Initialize(credentials)
    else:
        # Fallback to local user credentials (if run locally with gcloud auth)
        ee.Initialize()
    _ee_initialized = True

def api_gee_tile_url(request):
    import ee
    try:
        initialize_ee()
        
        # Wilpattu bounding box
        aoi = ee.Geometry.Rectangle([79.82, 8.12, 80.25, 8.65])
        
        # Query Sentinel-2 Surface Reflectance
        s2_collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                         .filterBounds(aoi)
                         .filterDate('2026-06-01', '2026-06-30')
                         .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
                         .sort('system:time_start', False))
        
        # Create median composite clipped to our Area of Interest
        image = s2_collection.median().clip(aoi)
        
        # True color visualization parameters
        vis_params = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 3000,
            'gamma': 1.4
        }
        
        map_info = image.getMapId(vis_params)
        tile_url = map_info['tile_fetcher'].url_format
        
        return JsonResponse({'tile_url': tile_url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def user_manual(request):
    return render(request, 'dashboard/user_manual.html')