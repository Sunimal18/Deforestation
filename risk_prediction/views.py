# risk_prediction/views.py

from django.shortcuts import render
from .models import RiskArea

def risk_prediction(request):
    areas = RiskArea.objects.all().order_by('-risk_score')
    
    high_risk_count = areas.filter(risk_level='high').count()
    total_monitored = areas.count()
    
    context = {
        'areas': areas,
        'high_risk_count': high_risk_count,
        'total_monitored': total_monitored,
    }
    return render(request, 'risk_prediction/risk_prediction.html', context)