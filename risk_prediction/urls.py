# risk_prediction/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.risk_prediction, name='risk_prediction'),
]