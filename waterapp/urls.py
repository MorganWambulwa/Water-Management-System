from django.urls import path
from . import views
from . import mpesa_views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    path('map/', views.water_source_map, name='water_source_map'),
    path('api/map-data/', views.water_source_map_data, name='water_source_map_data'),

    path('sources/', views.water_source_list, name='water_source_list'),
    path('sources/<int:pk>/', views.water_source_detail, name='water_source_detail'),
    path('sources/add/', views.water_source_create_update, name='water_source_create'),
    path('sources/edit/<int:pk>/', views.water_source_create_update, name='water_source_update'),
    path('sources/delete/<int:pk>/', views.water_source_delete, name='water_source_delete'),
    
    path('report/new/', views.issue_report_create, name='issue_report_create'),
    path('repair/log/<int:source_pk>/', views.repair_log_create, name='repair_log_create'),
    path('issue/resolve/<int:pk>/', views.issue_toggle_resolve, name='issue_toggle_resolve'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('legal/<str:page_type>/', views.legal_page, name='legal_page'),
    path('contact/', views.contact, name='contact'),
    path('admin/export/issues/', views.export_issues_csv, name='export_issues_csv'),
    path('donate/', mpesa_views.mpesa_pay, name='mpesa_pay'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('partner/', views.vendor_signup, name='vendor_signup'),
    path('vendor/edit/', views.vendor_profile_edit, name='vendor_profile_edit'),
]