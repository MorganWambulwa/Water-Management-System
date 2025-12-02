from django.urls import path
from . import views

urlpatterns = [
    # --- Main Pages ---
    path('', views.index, name='index'),
    path('about/', views.about, name='about'), # We added this earlier
    
    # --- Authentication ---
    path('accounts/signup/', views.signup, name='signup'),
    
    # --- Map Features (The missing parts!) ---
    path('map/', views.water_source_map, name='water_source_map'),
    path('api/map-data/', views.water_source_map_data, name='water_source_map_data'),

    # --- Sources CRUD ---
    path('sources/', views.water_source_list, name='water_source_list'),
    path('sources/<int:pk>/', views.water_source_detail, name='water_source_detail'),
    path('sources/add/', views.water_source_create_update, name='water_source_create'),
    path('sources/edit/<int:pk>/', views.water_source_create_update, name='water_source_update'),
    
    # --- Issues & Repairs ---
    path('report/new/', views.issue_report_create, name='issue_report_create'),
    path('repair/log/<int:source_pk>/', views.repair_log_create, name='repair_log_create'),
    path('issue/resolve/<int:pk>/', views.issue_toggle_resolve, name='issue_toggle_resolve'),
    
    # --- Admin Dashboard ---
    path('dashboard/', views.dashboard, name='dashboard'),
]