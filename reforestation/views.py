from django.shortcuts import render
import csv
import os
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

def reforestation(request):
    # Query recent disturbances for alerts
    recent_disturbances = DisturbanceArea.objects.all().order_by('-detection_date')[:2]
    
    # Query highest risk area
    recent_risks = RiskArea.objects.all().order_by('-risk_score')[:1]
    
    # Load reforestation statistics from Tables 3 & 4 CSVs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suitability_path = os.path.join(base_dir, 'output', 'Table3_ReforestationSuitability.csv')
    priority_path = os.path.join(base_dir, 'output', 'Table4_ReforestationPriority.csv')
    
    suitability_counts = {}
    if os.path.exists(suitability_path):
        with open(suitability_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for row in reader:
                if len(row) >= 2:
                    suitability_counts[row[0].strip()] = int(float(row[1].strip()))
                    
    priority_counts = {}
    if os.path.exists(priority_path):
        with open(priority_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for row in reader:
                if len(row) >= 2:
                    priority_counts[row[0].strip()] = int(float(row[1].strip()))
    
    context = {
        'recent_disturbances': recent_disturbances,
        'recent_risks': recent_risks,
        'suitability_counts': suitability_counts,
        'priority_counts': priority_counts,
    }
    return render(request, 'reforestation/reforestation.html', context)