from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.conf import settings
import json
import zipfile
import os
import tempfile
from weasyprint import HTML, CSS

from .models import Portfolio, UserProfile, Education, Experience, Skill, Project, Certification
from .forms import (
    CustomUserCreationForm, UserProfileForm, PortfolioForm, 
    EducationForm, ExperienceForm, SkillForm, ProjectForm, CertificationForm,
    CVUploadForm
)

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('portfolio:dashboard')
    return render(request, 'portfolio/home.html')

class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('portfolio:dashboard')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('portfolio:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('portfolio:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """User dashboard view"""
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/dashboard.html', {'portfolios': portfolios})

@login_required
def profile_edit(request):
    """Edit user profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('portfolio:dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'portfolio/profile_edit.html', {'form': form})

@login_required
def portfolio_create(request):
    """Create new portfolio view"""
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.slug = slugify(portfolio.title)
            
            # Ensure unique slug
            original_slug = portfolio.slug
            counter = 1
            while Portfolio.objects.filter(slug=portfolio.slug).exists():
                portfolio.slug = f"{original_slug}-{counter}"
                counter += 1
            
            portfolio.save()
            messages.success(request, 'Portfolio created successfully!')
            return redirect('portfolio:portfolio_edit', slug=portfolio.slug)
    else:
        form = PortfolioForm()
    
    return render(request, 'portfolio/portfolio_create.html', {'form': form})
