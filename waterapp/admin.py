from django.contrib import admin
from .models import WaterSource, IssueReport, RepairLog
from .forms import RepairLogForm, WaterSourceForm, IssueReportForm, AdminRepairLogForm

@admin.register(WaterSource)
class WaterSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'status', 'is_verified', 'last_updated')
    list_filter = ('status', 'source_type', 'is_verified')
    search_fields = ('name', 'description')

@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ('water_source', 'priority_level', 'is_resolved', 'reported_at')
    list_filter = ('is_resolved', 'priority_level')

@admin.register(RepairLog)
class RepairLogAdmin(admin.ModelAdmin):
    form = AdminRepairLogForm
    list_display = ('water_source', 'technician', 'repair_date', 'cost')
    

    
