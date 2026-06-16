import os
import json
from datetime import date
from django.core.management.base import BaseCommand
from pyproj import Transformer
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

class Command(BaseCommand):
    help = 'Import GeoJSON disturbance polygons and generate risk prediction areas.'

    def handle(self, *args, **options):
        # Define paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        geojson_path = os.path.join(base_dir, 'models', 'FOREST_AI_DisturbancePolygons_v1.geojson')

        if not os.path.exists(geojson_path):
            self.stdout.write(self.style.ERROR(f"GeoJSON file not found at: {geojson_path}"))
            return

        self.stdout.write("Loading GeoJSON data...")
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        features = data.get('features', [])
        self.stdout.write(f"Found {len(features)} features. Cleaning old database entries...")
        
        # Clear existing data to avoid duplicates
        DisturbanceArea.objects.all().delete()
        RiskArea.objects.all().delete()

        # Initialize pyproj transformer to convert from EPSG:32644 (UTM 44N) to EPSG:4326 (WGS84 Lat/Lng)
        transformer = Transformer.from_crs("epsg:32644", "epsg:4326", always_xy=True)

        disturbance_count = 0
        risk_count = 0

        self.stdout.write("Importing areas into database...")
        for i, feature in enumerate(features):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            geom_type = geometry.get('type')
            coordinates = geometry.get('coordinates', [])

            if not coordinates or geom_type != 'Polygon':
                continue

            # Transform UTM coordinates to Lat/Lng
            new_coordinates = []
            for ring in coordinates:
                new_ring = []
                for pt in ring:
                    if len(pt) >= 2:
                        lon, lat = transformer.transform(pt[0], pt[1])
                        new_ring.append([lon, lat])
                new_coordinates.append(new_ring)

            transformed_geometry = {
                'type': 'Polygon',
                'coordinates': new_coordinates
            }

            # Generate unique area ID
            area_id = f"WNP-{10 + i}"
            area_m2 = properties.get('area_m2', 0)
            
            # Generate demonstration stats
            ndvi_change = round(-0.15 - (i % 5) * 0.08, 2)
            confidence = round(0.80 + (i % 20) * 0.009, 2)

            # Calculate severity based on ndvi_change and area
            if ndvi_change < -0.35:
                severity = 'high'
                status = 'active'
            elif ndvi_change < -0.22:
                severity = 'moderate'
                status = 'monitored'
            else:
                severity = 'low'
                status = 'resolved' if i % 3 == 0 else 'monitored'

            # 1. Create DisturbanceArea record
            DisturbanceArea.objects.create(
                area_id=area_id,
                detection_date=date(2026, 5, 12) if i % 2 == 0 else date(2026, 6, 22),
                ndvi_change=ndvi_change,
                area_m2=round(area_m2, 2),
                severity=severity,
                status=status,
                confidence=confidence,
                geometry=transformed_geometry
            )
            disturbance_count += 1

            # 2. Generate related Risk Area
            if severity in ['high', 'moderate']:
                risk_score = int(60 + (i % 40))
                risk_level = 'high' if risk_score >= 80 else 'medium'
                
                factors_list = [
                    "Proximity to road, Low rainfall",
                    "Recent logging activity",
                    "Human settlement nearby",
                    "Agricultural expansion, Forest edge"
                ]
                primary_factors = factors_list[i % len(factors_list)]

                RiskArea.objects.create(
                    area_id=area_id,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    primary_factors=primary_factors,
                    geometry=transformed_geometry
                )
                risk_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported {disturbance_count} Disturbance areas and {risk_count} Risk areas into Supabase!"
        ))
