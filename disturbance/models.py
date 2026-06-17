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
    polygon_id = models.CharField(max_length=50, null=True, blank=True)
    detection_date = models.DateField()
    ndvi_change = models.FloatField()
    area_m2 = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    confidence = models.FloatField() # e.g. 0.89 for 89%
    geometry = models.JSONField() # Stores the GeoJSON geometry feature dict

    # CSV attributes
    area_ha = models.FloatField(null=True, blank=True)
    road_distance_m = models.FloatField(null=True, blank=True)
    village_distance_m = models.FloatField(null=True, blank=True)
    waterway_distance_m = models.FloatField(null=True, blank=True)
    protected_area = models.BooleanField(default=False)
    vulnerability_score = models.FloatField(null=True, blank=True)
    disturbance_score = models.FloatField(null=True, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    risk_class = models.CharField(max_length=20, null=True, blank=True) # low, moderate, high
    reforestation_suitability = models.CharField(max_length=50, null=True, blank=True)
    reforestation_priority = models.CharField(max_length=20, null=True, blank=True)
    xai_explanation = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.area_id} - {self.severity} ({self.status})"
