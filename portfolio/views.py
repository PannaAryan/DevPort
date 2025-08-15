from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
import json
import zipfile
import os
import tempfile
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from .models import Portfolio, UserProfile, Education, Experience, Skill, Project, Certification
from .forms import (
    CustomUserCreationForm, UserProfileForm, PortfolioForm, 
    EducationForm, ExperienceForm, SkillForm, ProjectForm, CertificationForm
)
from .pdf_utils import PortfolioPDFGenerator
from .zip_utils import zip_exporter


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
    total_public_portfolios = Portfolio.objects.filter(is_public=True).count()

    context = {
        'portfolios': portfolios,
        'total_public_portfolios': total_public_portfolios,
    }

    return render(request, 'portfolio/dashboard.html', context)


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
            return redirect('portfolio:edit', slug=portfolio.slug)
    else:
        form = PortfolioForm()
    
    return render(request, 'portfolio/portfolio_create.html', {'form': form})


@login_required
def portfolio_edit(request, slug):
    """Edit portfolio view"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    context = {
        'portfolio': portfolio,
        'education_list': portfolio.education.all(),
        'experience_list': portfolio.experience.all(),
        'skills_list': portfolio.skills.all(),
        'projects_list': portfolio.projects.all(),
        'certifications_list': portfolio.certifications.all(),
    }
    
    return render(request, 'portfolio/portfolio_edit.html', context)


@login_required
def portfolio_preview(request, slug):
    """Portfolio preview view"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    context = {
        'portfolio': portfolio,
        'user_profile': portfolio.user.profile,
        'education_list': portfolio.education.all(),
        'experience_list': portfolio.experience.all(),
        'skills_by_category': {},
        'projects_list': portfolio.projects.all(),
        'certifications_list': portfolio.certifications.all(),
    }
    
    # Group skills by category
    for skill in portfolio.skills.all():
        if skill.category not in context['skills_by_category']:
            context['skills_by_category'][skill.category] = []
        context['skills_by_category'][skill.category].append(skill)
    
    return render(request, f'portfolio/themes/{portfolio.theme}.html', context)


def portfolio_public(request, slug):
    """Public portfolio view"""
    portfolio = get_object_or_404(Portfolio, slug=slug, is_public=True)
    
    context = {
        'portfolio': portfolio,
        'user_profile': portfolio.user.profile,
        'education_list': portfolio.education.all(),
        'experience_list': portfolio.experience.all(),
        'skills_by_category': {},
        'projects_list': portfolio.projects.all(),
        'certifications_list': portfolio.certifications.all(),
    }
    
    # Group skills by category
    for skill in portfolio.skills.all():
        if skill.category not in context['skills_by_category']:
            context['skills_by_category'][skill.category] = []
        context['skills_by_category'][skill.category].append(skill)
    
    return render(request, f'portfolio/themes/{portfolio.theme}.html', context)


@login_required
def portfolio_delete(request, slug):
    """Delete portfolio view"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, 'Portfolio deleted successfully!')
        return redirect('portfolio:dashboard')
    
    return render(request, 'portfolio/portfolio_delete.html', {'portfolio': portfolio})


@login_required
def portfolio_export_zip(request, slug):
    """Export portfolio as ZIP file with enhanced assets"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    user_profile = getattr(portfolio.user, 'profile', None)
    
    if not user_profile:
        user_profile, created = UserProfile.objects.get_or_create(user=portfolio.user)
    
    # Generate ZIP using enhanced utility
    return zip_exporter.create_portfolio_zip(portfolio, user_profile, request)


@login_required
def portfolio_export_pdf(request, slug):
    """Export portfolio as PDF file with enhanced formatting"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    user_profile = getattr(portfolio.user, 'profile', None)
    
    if not user_profile:
        user_profile, created = UserProfile.objects.get_or_create(user=portfolio.user)
    
    # Generate PDF using enhanced utility
    pdf_generator = PortfolioPDFGenerator()
    pdf_bytes = pdf_generator.generate_pdf(portfolio, user_profile, request)
    
    # Create response
    filename = f"{portfolio.slug}_portfolio.pdf"
    return pdf_generator.create_response(pdf_bytes, filename)


# AJAX views for dynamic form handling
@login_required
def add_education(request, slug):
    """Add education entry via AJAX"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.portfolio = portfolio
            education.save()
            return JsonResponse({'success': True, 'message': 'Education added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def add_experience(request, slug):
    """Add experience entry via AJAX"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.portfolio = portfolio
            experience.save()
            return JsonResponse({'success': True, 'message': 'Experience added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def add_skill(request, slug):
    """Add skill entry via AJAX"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.portfolio = portfolio
            skill.save()
            return JsonResponse({'success': True, 'message': 'Skill added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def add_project(request, slug):
    """Add project entry via AJAX"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.portfolio = portfolio
            project.save()
            return JsonResponse({'success': True, 'message': 'Project added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def add_certification(request, slug):
    """Add certification entry via AJAX"""
    portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.portfolio = portfolio
            certification.save()
            return JsonResponse({'success': True, 'message': 'Certification added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

