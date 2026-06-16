from django.db import models

class DisturbanceArea(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('monitored', 'Monitored'),
        ('resolved', 'Resolved'),
    ]

    area_id = models.CharField(max_length=50, unique=True)
    detection_date = models.DateField()
    ndvi_change = models.FloatField()
    area_m2 = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    confidence = models.FloatField() # e.g. 0.89 for 89%
    geometry = models.JSONField() # Stores the GeoJSON geometry feature dict

    def __str__(self):
        return f"{self.area_id} - {self.severity} ({self.status})"
