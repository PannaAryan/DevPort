from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Portfolio(models.Model):
    THEME_CHOICES = [
        ('minimal_dark', 'Minimal Dark'),
        ('modern_light', 'Modern Light'),
        ('creative_burst', 'Creative Burst'),
        ('tech_noir', 'Tech Noir'),
        ('professional_corporate', 'Professional Corporate'),
        ('gradient_showcase', 'Gradient Showcase'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='minimal_dark')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Education(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    grade = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.position} at {self.company}"

class Skill(models.Model):
    SKILL_CATEGORIES = [
        ('programming', 'Programming Languages'),
        ('frameworks', 'Frameworks & Libraries'),
        ('databases', 'Databases'),
        ('tools', 'Tools & Technologies'),
        ('soft_skills', 'Soft Skills'),
        ('other', 'Other'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=SKILL_CATEGORIES, default='programming')
    proficiency = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return self.name

class Project(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=500, help_text="Comma-separated list of technologies")
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-featured', '-start_date']

    def __str__(self):
        return self.title

class Certification(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return self.name