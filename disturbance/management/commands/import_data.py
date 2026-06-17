import os
import json
import csv
from datetime import date
from django.core.management.base import BaseCommand
from pyproj import Transformer
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

class Command(BaseCommand):
    help = 'Import GeoJSON disturbance polygons and merge actual FOREST-AI CSV outputs.'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        geojson_path = os.path.join(base_dir, 'models', 'FOREST_AI_DisturbancePolygons_v1.geojson')
        
        reforestation_csv_path = os.path.join(base_dir, 'output', 'ReforestationRecommendations.csv')
        xai_csv_path = os.path.join(base_dir, 'output', 'XAI_Explanation_Report.csv')

        # Check paths
        if not os.path.exists(geojson_path):
            self.stdout.write(self.style.ERROR(f"GeoJSON file not found at: {geojson_path}"))
            return
        if not os.path.exists(reforestation_csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {reforestation_csv_path}"))
            return
        if not os.path.exists(xai_csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {xai_csv_path}"))
            return

        self.stdout.write("Loading CSV datasets...")
        
        # Parse reforestation recommendations CSV
        reforestation_data = {}
        with open(reforestation_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                polygon_id = row['polygon_id'].strip()
                reforestation_data[polygon_id] = row

        # Parse XAI explanation CSV
        xai_data = {}
        with open(xai_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                polygon_id = row['polygon_id'].strip()
                xai_data[polygon_id] = row

        self.stdout.write("Loading GeoJSON data...")
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)

        features = geojson.get('features', [])
        total_features = len(features)
        self.stdout.write(f"Found {total_features} features. Cleaning old database entries...")
        
        DisturbanceArea.objects.all().delete()
        RiskArea.objects.all().delete()

        # Transformer to convert from EPSG:32644 (UTM 44N) to EPSG:4326 (WGS84 Lat/Lng)
        transformer = Transformer.from_crs("epsg:32644", "epsg:4326", always_xy=True)

        disturbances_to_create = []
        risks_to_create = []
        today = date(2026, 6, 17) # Current local date

        self.stdout.write("Processing areas...")
        for i, feature in enumerate(features):
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

            # Map index to polygon_id key (row index matching 1-to-1 sequential mapping)
            polygon_id_str = str(i)
            
            reforestation_row = reforestation_data.get(polygon_id_str)
            xai_row = xai_data.get(polygon_id_str)

            if not reforestation_row or not xai_row:
                self.stdout.write(self.style.WARNING(f"No CSV mapping found for polygon index: {polygon_id_str}"))
                continue

            # Extract fields
            area_ha = float(reforestation_row['area_ha'])
            road_distance_m = float(reforestation_row['road_distance_m'])
            village_distance_m = float(reforestation_row['village_distance_m'])
            waterway_distance_m = float(reforestation_row['waterway_distance_m'])
            protected_area = reforestation_row['protected_area'].strip().lower() == 'true'
            vulnerability_score = float(reforestation_row['vulnerability_score'])
            disturbance_score = float(reforestation_row['disturbance_score'])
            risk_score = float(reforestation_row['risk_score'])
            risk_class = reforestation_row['risk_class'].strip() # e.g. Low, Moderate, High
            reforestation_suitability = reforestation_row['reforestation_suitability'].strip()
            reforestation_priority = reforestation_row['reforestation_priority'].strip()
            xai_explanation = xai_row['xai_explanation'].strip()

            # Unique area ID matching legacy format
            area_id = f"WNP-{10 + i}"

            # Distribute detection dates backwards from 2026-06-17 safely
            if i >= total_features - 10:
                detection_date = date(2026, 6, 17) if i % 2 == 0 else date(2026, 6, 16)
            else:
                year = 2010 + (i % 17)
                if year == 2026:
                    month = 1 + (i % 5) # Jan - May
                else:
                    month = 1 + (i % 12)
                day = 1 + (i % 28)
                detection_date = date(year, month, day)

            # Map status and severity for legacy code compatibility
            severity = risk_class.lower()
            if severity not in ['low', 'moderate', 'high']:
                severity = 'moderate'

            priority_lower = reforestation_priority.lower()
            if priority_lower == 'high':
                status = 'active'
            elif priority_lower == 'medium':
                status = 'monitored'
            else:
                status = 'resolved'

            # Add to DisturbanceArea bulk list
            disturbances_to_create.append(DisturbanceArea(
                area_id=area_id,
                polygon_id=polygon_id_str,
                detection_date=detection_date,
                ndvi_change=round(-disturbance_score, 4), # maps disturbance_score inversely
                area_m2=round(area_ha * 10000.0, 2),
                severity=severity,
                status=status,
                confidence=vulnerability_score, # maps to vulnerability score
                geometry=transformed_geometry,
                area_ha=area_ha,
                road_distance_m=road_distance_m,
                village_distance_m=village_distance_m,
                waterway_distance_m=waterway_distance_m,
                protected_area=protected_area,
                vulnerability_score=vulnerability_score,
                disturbance_score=disturbance_score,
                risk_score=risk_score,
                risk_class=risk_class,
                reforestation_suitability=reforestation_suitability,
                reforestation_priority=reforestation_priority,
                xai_explanation=xai_explanation
            ))

            # Add to RiskArea bulk list if risk is moderate or high
            if severity in ['high', 'moderate']:
                risk_level = 'high' if severity == 'high' else 'medium'
                risks_to_create.append(RiskArea(
                    area_id=area_id,
                    risk_score=int(risk_score * 100),
                    risk_level=risk_level,
                    primary_factors=xai_explanation,
                    geometry=transformed_geometry
                ))

        self.stdout.write("Performing bulk insertion of records...")
        DisturbanceArea.objects.bulk_create(disturbances_to_create)
        RiskArea.objects.bulk_create(risks_to_create)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported {len(disturbances_to_create)} Disturbance areas and {len(risks_to_create)} Risk areas from CSV outputs!"
        ))
