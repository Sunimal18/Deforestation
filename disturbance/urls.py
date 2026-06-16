from django.urls import path
from . import views

urlpatterns = [
    path('', views.disturbance_detection, name='disturbance_detection'),
]