from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Portfolio management
    path('portfolio/create/', views.portfolio_create, name='create'),
    path('portfolio/<slug:slug>/edit/', views.portfolio_edit, name='edit'),
    path('portfolio/<slug:slug>/preview/', views.portfolio_preview, name='preview'),
    path('portfolio/<slug:slug>/delete/', views.portfolio_delete, name='delete'),
    
    # Public portfolio
    path('u/<slug:slug>/', views.portfolio_public, name='public'),
    
    # Export functionality
    path('portfolio/<slug:slug>/export/zip/', views.portfolio_export_zip, name='export_zip'),
    path('portfolio/<slug:slug>/export/pdf/', views.portfolio_export_pdf, name='export_pdf'),
    
    # AJAX endpoints for adding portfolio items
    path('portfolio/<slug:slug>/add/education/', views.add_education, name='add_education'),
    path('portfolio/<slug:slug>/add/experience/', views.add_experience, name='add_experience'),
    path('portfolio/<slug:slug>/add/skill/', views.add_skill, name='add_skill'),
    path('portfolio/<slug:slug>/add/project/', views.add_project, name='add_project'),
    path('portfolio/<slug:slug>/add/certification/', views.add_certification, name='add_certification'),
]

