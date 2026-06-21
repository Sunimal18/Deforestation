from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('disturbance-detection/', views.disturbance_detection, name='disturbance_detection'),
    path('reports/', views.reports, name='reports'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    path('api/disturbances/', views.api_disturbances, name='api_disturbances'),
    path('api/risk-areas/', views.api_risk_areas, name='api_risk_areas'),
]


