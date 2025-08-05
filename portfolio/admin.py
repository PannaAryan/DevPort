from django.contrib import admin
from .models import UserProfile, Portfolio, Education, Experience, Skill, Project, Certification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'created_at']
    list_filter = ['created_at', 'location']
    search_fields = ['user__username', 'user__email']

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'theme', 'is_public', 'created_at']
    list_filter = ['theme', 'is_public', 'created_at']
    search_fields = ['title', 'user__username']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'portfolio', 'start_date']
    list_filter = ['start_date', 'institution']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'portfolio', 'start_date', 'is_current']
    list_filter = ['is_current', 'start_date', 'company']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'portfolio']
    list_filter = ['category', 'proficiency']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'portfolio', 'featured', 'start_date']
    list_filter = ['featured', 'start_date']

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuing_organization', 'portfolio', 'issue_date']
    list_filter = ['issue_date', 'issuing_organization']