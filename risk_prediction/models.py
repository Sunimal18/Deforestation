from django.db import models

class RiskArea(models.Model):
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    area_id = models.CharField(max_length=50, unique=True)
    risk_score = models.IntegerField() # 0 to 100
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='medium')
    primary_factors = models.CharField(max_length=255) # e.g. "Proximity to road, Low rainfall"
    geometry = models.JSONField() # Stores the GeoJSON geometry

    def __str__(self):
        return f"{self.area_id} - Risk: {self.risk_score} ({self.risk_level})"
