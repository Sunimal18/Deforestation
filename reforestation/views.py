from django.shortcuts import render
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

def reforestation(request):
    # Query recent disturbances for alerts
    recent_disturbances = DisturbanceArea.objects.all().order_by('-detection_date')[:2]
    
    # Query highest risk area
    recent_risks = RiskArea.objects.all().order_by('-risk_score')[:1]
    
    context = {
        'recent_disturbances': recent_disturbances,
        'recent_risks': recent_risks,
    }
    return render(request, 'reforestation/reforestation.html', context)