from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Portfolio, Education, Experience, Skill, Project, Certification

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date', 'profile_picture', 'phone', 'website', 
                 'github_url', 'linkedin_url', 'twitter_url']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'theme', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter portfolio title'
            }),
            'theme': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description', 'grade']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'position', 'location', 'start_date', 'end_date', 'description', 'is_current']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'github_url', 'live_url', 'image', 
                 'start_date', 'end_date', 'featured']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiration_date', 'credential_id', 'credential_url']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CVUploadForm(forms.Form):
    cv_file = forms.FileField(
        label='Upload CV/Resume',
        help_text='Upload your CV/Resume in PDF format to auto-fill portfolio data',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.doc,.docx',
            'class': 'form-control'
        })
    )