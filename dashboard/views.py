from django.shortcuts import render
from django.http import JsonResponse
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

def dashboard(request):
    # Pass metrics to dashboard overview
    total_disturbances = DisturbanceArea.objects.count()
    active_alerts = DisturbanceArea.objects.filter(status='active').count()
    high_risk = RiskArea.objects.filter(risk_level='high').count()
    
    # Query recent disturbances for the alerts panel
    recent_disturbances = DisturbanceArea.objects.all().order_by('-detection_date')[:2]
    
    # Query highest risk areas
    recent_risks = RiskArea.objects.filter(risk_level='high').order_by('-risk_score')[:1]
    
    context = {
        'total_disturbances': total_disturbances,
        'active_alerts': active_alerts,
        'high_risk_count': high_risk,
        'recent_disturbances': recent_disturbances,
        'recent_risks': recent_risks,
    }
    return render(request, 'dashboard/dashboard.html', context)

def disturbance_detection(request):
    return render(request, 'disturbance/disturbance.html')

def api_disturbances(request):
    areas = DisturbanceArea.objects.all()
    features = []
    
    for area in areas:
        features.append({
            "type": "Feature",
            "properties": {
                "area_id": area.area_id,
                "severity": area.severity,
                "status": area.status,
                "confidence": area.confidence,
                "area_m2": area.area_m2,
                "ndvi_change": area.ndvi_change,
                "detection_date": area.detection_date.strftime('%Y-%m-%d'),
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