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
from django.views.decorators.http import require_http_methods
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


@login_required
@require_http_methods(["POST"])
def delete_portfolio_item(request, slug, item_type, item_id):
    """Delete portfolio items via AJAX"""
    try:
        # Get the portfolio first to ensure user owns it
        portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)


        model_map = {
            'experience': Experience,
            'education': Education,
            'skill': Skill,
            'project': Project,
            'certification': Certification,
        }

        if item_type not in model_map:
            return JsonResponse({'error': 'Invalid item type'}, status=400)

        Model = model_map[item_type]

        # Get the item and ensure it belongs to the current portfolio
        item = get_object_or_404(Model, id=item_id, portfolio=portfolio)

        # Delete the item
        item.delete()

        return JsonResponse({
            'success': True,
            'message': f'{item_type.title()} deleted successfully'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_portfolio_item(request, slug, item_type, item_id):
    """Get portfolio item data for editing"""
    try:
        # Get the portfolio first to ensure user owns it
        portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)

        from .models import Experience, Education, Project, Certification

        model_map = {
            'experience': Experience,
            'education': Education,
            'project': Project,
            'certification': Certification,
        }

        if item_type not in model_map:
            return JsonResponse({'error': 'Invalid item type'}, status=400)

        Model = model_map[item_type]
        item = get_object_or_404(Model, id=item_id, portfolio=portfolio)

        # Serialize the item data based on type
        if item_type == 'experience':
            data = {
                'id': item.id,
                'position': item.position,
                'company': item.company,
                'location': getattr(item, 'location', ''),
                'start_date': item.start_date.strftime('%Y-%m-%d') if item.start_date else '',
                'end_date': item.end_date.strftime('%Y-%m-%d') if item.end_date else '',
                'is_current': getattr(item, 'is_current', False),
                'description': item.description,
            }
        elif item_type == 'education':
            data = {
                'id': item.id,
                'institution': item.institution,
                'degree': item.degree,
                'field_of_study': getattr(item, 'field_of_study', ''),
                'start_date': item.start_date.strftime('%Y-%m-%d') if item.start_date else '',
                'end_date': item.end_date.strftime('%Y-%m-%d') if item.end_date else '',
                'grade': getattr(item, 'grade', ''),
                'description': getattr(item, 'description', ''),
            }
        elif item_type == 'project':
            data = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'technologies': getattr(item, 'technologies', ''),
                'github_url': getattr(item, 'github_url', ''),
                'live_url': getattr(item, 'live_url', ''),
                'start_date': item.start_date.strftime('%Y-%m-%d') if hasattr(item,
                                                                              'start_date') and item.start_date else '',
                'end_date': item.end_date.strftime('%Y-%m-%d') if hasattr(item, 'end_date') and item.end_date else '',
            }
        elif item_type == 'certification':
            data = {
                'id': item.id,
                'name': item.name,
                'issuing_organization': item.issuing_organization,
                'issue_date': item.issue_date.strftime('%Y-%m-%d') if item.issue_date else '',
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
                'credential_id': getattr(item, 'credential_id', ''),
                'credential_url': getattr(item, 'credential_url', ''),
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_portfolio_item(request, slug, item_type, item_id):
    """Update portfolio items via AJAX"""
    try:
        # Get the portfolio first to ensure user owns it
        portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)

        from .models import Experience, Education, Project, Certification

        model_map = {
            'experience': Experience,
            'education': Education,
            'project': Project,
            'certification': Certification,
        }

        if item_type not in model_map:
            return JsonResponse({'error': 'Invalid item type'}, status=400)

        Model = model_map[item_type]
        item = get_object_or_404(Model, id=item_id, portfolio=portfolio)

        # Parse JSON data from request
        data = json.loads(request.body)

        # Update fields based on item type
        if item_type == 'experience':
            item.position = data.get('position', item.position)
            item.company = data.get('company', item.company)
            if hasattr(item, 'location'):
                item.location = data.get('location', getattr(item, 'location', ''))
            item.start_date = data.get('start_date') or item.start_date
            item.end_date = data.get('end_date') or item.end_date
            if hasattr(item, 'is_current'):
                item.is_current = data.get('is_current', getattr(item, 'is_current', False))
            item.description = data.get('description', item.description)

        elif item_type == 'education':
            item.institution = data.get('institution', item.institution)
            item.degree = data.get('degree', item.degree)
            if hasattr(item, 'field_of_study'):
                item.field_of_study = data.get('field_of_study', getattr(item, 'field_of_study', ''))
            item.start_date = data.get('start_date') or item.start_date
            item.end_date = data.get('end_date') or item.end_date
            if hasattr(item, 'grade'):
                item.grade = data.get('grade', getattr(item, 'grade', ''))
            if hasattr(item, 'description'):
                item.description = data.get('description', getattr(item, 'description', ''))

        elif item_type == 'project':
            item.name = data.get('name', item.name)
            item.description = data.get('description', item.description)
            if hasattr(item, 'technologies'):
                item.technologies = data.get('technologies', getattr(item, 'technologies', ''))
            if hasattr(item, 'github_url'):
                item.github_url = data.get('github_url', getattr(item, 'github_url', ''))
            if hasattr(item, 'live_url'):
                item.live_url = data.get('live_url', getattr(item, 'live_url', ''))
            if hasattr(item, 'start_date'):
                item.start_date = data.get('start_date') or getattr(item, 'start_date', None)
            if hasattr(item, 'end_date'):
                item.end_date = data.get('end_date') or getattr(item, 'end_date', None)

        elif item_type == 'certification':
            item.name = data.get('name', item.name)
            item.issuing_organization = data.get('issuing_organization', item.issuing_organization)
            item.issue_date = data.get('issue_date') or item.issue_date
            item.expiry_date = data.get('expiry_date') or getattr(item, 'expiry_date', None)
            if hasattr(item, 'credential_id'):
                item.credential_id = data.get('credential_id', getattr(item, 'credential_id', ''))
            if hasattr(item, 'credential_url'):
                item.credential_url = data.get('credential_url', getattr(item, 'credential_url', ''))

        item.save()

        return JsonResponse({
            'success': True,
            'message': f'{item_type.title()} updated successfully'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_skill(request, slug, skill_id):
    """Delete skill via AJAX"""
    try:
        # Get the portfolio first to ensure user owns it
        portfolio = get_object_or_404(Portfolio, slug=slug, user=request.user)

        from .models import Skill
        skill = get_object_or_404(Skill, id=skill_id, portfolio=portfolio)

        skill.delete()

        return JsonResponse({
            'success': True,
            'message': 'Skill deleted successfully'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

