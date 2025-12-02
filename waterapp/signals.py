from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import IssueReport, WaterSource

@receiver(post_save, sender=IssueReport)
def update_source_status(sender, instance, created, **kwargs):
    """
    If a High Priority (Level 3) issue is created, 
    automatically set the WaterSource status to Maintenance.
    """
    if created and instance.priority_level == 3:
        source = instance.water_source
        source.status = 'M' # Maintenance
        source.save()