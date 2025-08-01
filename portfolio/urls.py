from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Portfolio management
    path('portfolio/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolio/<slug:slug>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('portfolio/<slug:slug>/preview/', views.portfolio_preview, name='portfolio_preview'),
    path('portfolio/<slug:slug>/delete/', views.portfolio_delete, name='portfolio_delete'),
    
    # Export functionality
    path('portfolio/<slug:slug>/export/zip/', views.portfolio_export_zip, name='portfolio_export_zip'),
    path('portfolio/<slug:slug>/export/pdf/', views.portfolio_export_pdf, name='portfolio_export_pdf'),
    
    # Public portfolio
    path('u/<slug:slug>/', views.portfolio_public, name='portfolio_public'),
    
    # AJAX endpoints for dynamic forms
    path('portfolio/<slug:slug>/add/education/', views.add_education, name='add_education'),
    path('portfolio/<slug:slug>/add/experience/', views.add_experience, name='add_experience'),
    path('portfolio/<slug:slug>/add/skill/', views.add_skill, name='add_skill'),
    path('portfolio/<slug:slug>/add/project/', views.add_project, name='add_project'),
    path('portfolio/<slug:slug>/add/certification/', views.add_certification, name='add_certification'),
]