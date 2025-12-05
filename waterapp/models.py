from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

class WaterSource(models.Model):
    """Represents a physical water source."""
    SOURCE_TYPES = [
        ('B', 'Borehole'),
        ('W', 'Well'),
        ('T', 'Tap'),
        ('R', 'River Intake'),
        ('P', 'Public Pump'),
    ]
    
    STATUS_CHOICES = [
        ('O', 'Operational'),
        ('M', 'Maintenance'),
        ('B', 'Broken/Non-Operational'),
        ('C', 'Contaminated'),
    ]

    name = models.CharField(max_length=100, help_text="E.g., Nairobi Zone A")
    source_type = models.CharField(max_length=1, choices=SOURCE_TYPES)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude coordinate")
    
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    is_verified = models.BooleanField(default=False, help_text="Has this source been verified for water quality?")
    
    # --- NEW FIELD: Tracks who created this source ---
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_sources')
    # -----------------------------------------------

    installation_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def status_color(self):
        """Helper to return the CSS color class based on status."""
        if self.status == 'O':
            return 'success' # Green
        elif self.status == 'M':
            return 'warning' # Yellow/Orange
        return 'danger' # Red

class IssueReport(models.Model):
    """Report submitted by a resident about a water source issue."""
    water_source = models.ForeignKey(WaterSource, on_delete=models.CASCADE, related_name='issues')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    
    is_resolved = models.BooleanField(default=False)
    
    priority_level = models.IntegerField(
        default=1, 
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ['-reported_at']

    def __str__(self):
        return f"Issue on {self.water_source.name} - Resolved: {self.is_resolved}"

class RepairLog(models.Model):
    """Log of maintenance/repair work done on a water source."""
    water_source = models.ForeignKey(WaterSource, on_delete=models.CASCADE, related_name='repairs')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    repair_date = models.DateField(default=timezone.now)
    work_done = models.TextField()
    
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        ordering = ['-repair_date']

    def __str__(self):
        return f"Repair on {self.water_source.name} on {self.repair_date}"