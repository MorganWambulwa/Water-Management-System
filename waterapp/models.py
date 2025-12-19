from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

class WaterSource(models.Model):
    """Represents a physical water source."""

    SOURCE_TYPES = [
        ('BH', 'Borehole'),
        ('WL', 'Well'),
        ('TP', 'Tap'),
        ('RI', 'River Intake'),
        ('PP', 'Public Pump'),
    ]
    
    STATUS_CHOICES = [
        ('O', 'Operational'), 
        ('M', 'Maintenance'),
        ('B', 'Broken/Non-Operational'),
        ('C', 'Contaminated'),  
    ]

    name = models.CharField(max_length=100, help_text="E.g., Nairobi Zone A")
    source_type = models.CharField(max_length=2, choices=SOURCE_TYPES)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude coordinate")
    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='O')
    is_verified = models.BooleanField(default=False, help_text="Has this source been verified for water quality?")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_sources')

    installation_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def status_color(self):
        """Helper to return the CSS color class based on status."""
        if self.status == 'O':
            return 'success'
        elif self.status == 'M':
            return 'warning' 
        elif self.status == 'C':
            return 'danger'    
        elif self.status == 'B':
            return 'brown-custom' 
        return 'secondary'

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

class WaterVendor(models.Model):
    """
    Represents a commercial water seller (Shop, Truck, or Individual).
    Linked to a User account so they can manage their own orders.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, help_text="Contact number for orders")
    
    location_name = models.CharField(max_length=100, help_text="e.g., 'Kasarani, Near Naivas'")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_open = models.BooleanField(default=True, help_text="Toggle this to show/hide on the map")
    is_verified = models.BooleanField(default=False, help_text="Admin must check this for vendor to appear on map")
    

    price_per_20l = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=50.00,
        validators=[MinValueValidator(Decimal('0.00'))], 
        help_text="Price for one 20L Jerrycan"
    )
    delivery_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.00, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Fixed delivery fee (0 for free delivery)"
    )

    def __str__(self):
        status = "Open" if self.is_open else "Closed"
        return f"{self.business_name} ({status})"

    @property
    def whatsapp_number(self):
        number = str(self.phone_number).strip().replace('+', '').replace(' ', '').replace('-', '')
        
        if number.startswith('0'):
            return '254' + number[1:]
        
        return number

class WaterOrder(models.Model):
    """
    Tracks a delivery order placed by a customer.
    """
    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DELIVERING', 'Out for Delivery'),
        ('COMPLETED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(WaterVendor, on_delete=models.CASCADE, related_name='received_orders')
    
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], help_text="Number of 20L Jerrycans")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    delivery_address = models.TextField(help_text="Detailed address or landmarks")
    customer_phone = models.CharField(max_length=15, help_text="Phone number for this specific order")
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.vendor:
            item_cost = self.vendor.price_per_20l * self.quantity
            self.total_cost = item_cost + self.vendor.delivery_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}: {self.customer.username} -> {self.vendor.business_name}"