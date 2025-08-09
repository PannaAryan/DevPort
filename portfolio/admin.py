from django.contrib import admin
from .models import UserProfile, Portfolio, Education, Experience, Skill, Project, Certification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'theme', 'is_public', 'created_at']
    list_filter = ['theme', 'is_public', 'created_at']
    search_fields = ['title', 'user__username', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    ordering = ['order', '-start_date']


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0
    ordering = ['order', '-start_date']


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
    ordering = ['category', 'order']


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    ordering = ['order', '-created_at']


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    ordering = ['order', '-issue_date']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution', 'degree', 'portfolio', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['institution', 'degree', 'portfolio__title']
    ordering = ['-start_date']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['company', 'position', 'portfolio', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'start_date', 'end_date']
    search_fields = ['company', 'position', 'portfolio__title']
    ordering = ['-start_date']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'portfolio']
    list_filter = ['category', 'proficiency']
    search_fields = ['name', 'portfolio__title']
    ordering = ['category', 'name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'portfolio', 'featured', 'created_at']
    list_filter = ['featured', 'created_at']
    search_fields = ['name', 'description', 'portfolio__title']
    ordering = ['-created_at']


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuing_organization', 'portfolio', 'issue_date', 'expiry_date']
    list_filter = ['issue_date', 'expiry_date']
    search_fields = ['name', 'issuing_organization', 'portfolio__title']
    ordering = ['-issue_date']

