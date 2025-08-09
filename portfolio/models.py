from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid


class UserProfile(models.Model):
    """Extended user profile for additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Portfolio(models.Model):
    """Main portfolio model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    is_public = models.BooleanField(default=False)
    theme = models.CharField(max_length=50, default='minimal_dark')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def get_absolute_url(self):
        return reverse('portfolio:detail', kwargs={'slug': self.slug})


class Education(models.Model):
    """Education information"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.degree} at {self.institution}"


class Experience(models.Model):
    """Work experience information"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.position} at {self.company}"


class Skill(models.Model):
    """Skills information"""
    SKILL_CATEGORIES = [
        ('programming', 'Programming Languages'),
        ('frameworks', 'Frameworks & Libraries'),
        ('tools', 'Tools & Technologies'),
        ('databases', 'Databases'),
        ('other', 'Other'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES, default='other')
    proficiency = models.IntegerField(default=3, help_text="1-5 scale")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']
        unique_together = ['portfolio', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Project(models.Model):
    """Project information"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.CharField(max_length=500, help_text="Comma-separated list of technologies")
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name

    def get_tech_list(self):
        """Return tech stack as a list"""
        return [tech.strip() for tech in self.tech_stack.split(',') if tech.strip()]


class Certification(models.Model):
    """Certification information"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-issue_date']

    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"

