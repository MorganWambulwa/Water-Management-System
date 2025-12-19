from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path
from .models import WaterSource, IssueReport, RepairLog, WaterVendor, WaterOrder
from . import views 
from .forms import (
    RepairLogForm, 
    WaterSourceForm, 
    IssueReportForm, 
    AdminRepairLogForm, 
    AdminWaterSourceForm, 
    AdminIssueReportForm
)

original_get_urls = admin.site.get_urls

def get_admin_urls():
    urls = original_get_urls()
    
    custom_urls = [
        path('export/issues/', views.export_issues_csv, name='export_issues_csv'),
    ]
    
    return custom_urls + urls

admin.site.get_urls = get_admin_urls


@admin.register(WaterSource)
class WaterSourceAdmin(admin.ModelAdmin):
    form = AdminWaterSourceForm
    list_display = ('name', 'source_type', 'status', 'is_verified', 'last_updated')
    list_filter = ('status', 'source_type', 'is_verified')
    search_fields = ('name', 'description')


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    form = AdminIssueReportForm
    
    list_display = ('water_source', 'priority_level', 'is_resolved', 'reported_at')
    list_filter = ('is_resolved', 'priority_level')
    search_fields = ('water_source__name', 'description')


@admin.register(RepairLog)
class RepairLogAdmin(admin.ModelAdmin):
    form = AdminRepairLogForm
    list_display = ('water_source', 'technician', 'repair_date', 'cost')
    
    class Media:
        css = {
            'all': ('waterapp/css/admin_custom.css',)
        }


@admin.register(WaterVendor)
class WaterVendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'location_name', 'is_open', 'price_per_20l', 'phone_number')
    list_filter = ('is_open', 'location_name')
    search_fields = ('business_name', 'user__username', 'location_name')
    list_editable = ('is_open', 'price_per_20l')

@admin.register(WaterOrder)
class WaterOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vendor', 'quantity', 'total_cost', 'status', 'created_at')
    list_filter = ('status', 'vendor', 'created_at')
    search_fields = ('customer__username', 'vendor__business_name', 'delivery_address')
    readonly_fields = ('total_cost', 'created_at')


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    class Media:
        css = {
            'all': ('waterapp/css/admin_custom.css',)
        }
        js = (
            'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap',
        ) 

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].help_text = ''
        return form