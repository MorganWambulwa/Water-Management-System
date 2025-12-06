from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path
from .models import WaterSource, IssueReport, RepairLog
from .forms import RepairLogForm, WaterSourceForm, IssueReportForm, AdminRepairLogForm, AdminWaterSourceForm
from . import views 

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
    form = IssueReportForm
    list_display = ('water_source', 'priority_level', 'is_resolved', 'reported_at')
    list_filter = ('is_resolved', 'priority_level')


@admin.register(RepairLog)
class RepairLogAdmin(admin.ModelAdmin):
    form = AdminRepairLogForm
    list_display = ('water_source', 'technician', 'repair_date', 'cost')
    
    class Media:
        css = {
            'all': ('waterapp/css/admin_custom.css',)
        }


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