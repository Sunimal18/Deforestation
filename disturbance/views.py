from django.shortcuts import render
from django.db.models import Avg, Sum
from .models import DisturbanceArea

def disturbance_detection(request):
    areas = DisturbanceArea.objects.all().order_by('-detection_date')
    
    active_count = areas.filter(status='active').count()
    
    # Calculate total area in hectares (1 hectare = 10,000 m2)
    total_area_m2 = areas.aggregate(Sum('area_m2'))['area_m2__sum'] or 0
    total_area_ha = round(total_area_m2 / 10000.0, 1)
    
    avg_ndvi = areas.aggregate(Avg('ndvi_change'))['ndvi_change__avg'] or 0
    avg_ndvi = round(avg_ndvi, 2)
    
    context = {
        'areas': areas,
        'active_count': active_count,
        'total_area_ha': total_area_ha,
        'avg_ndvi': avg_ndvi,
    }
    return render(request, 'disturbance/disturbance.html', context)