from django.test import TestCase
from .models import WaterSource

class WaterSourceModelTest(TestCase):
    def setUp(self):
        WaterSource.objects.create(
            name="Test Pump", 
            source_type="P", 
            latitude=1.23, 
            longitude=36.78
        )

    def test_water_source_creation(self):
        source = WaterSource.objects.get(name="Test Pump")
        self.assertEqual(source.source_type, "P")
        self.assertEqual(source.status, "O") # Check default is Operational