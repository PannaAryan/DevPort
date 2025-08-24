from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Portfolio, Education, Experience, Skill, Project, Certification
from .image_utils import image_handler


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile with enhanced image handling"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'location', 'website', 'github_url', 'linkedin_url', 'twitter_url']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-400 transition p-3'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 bg-white shadow-sm focus:border-purple-500 focus:ring-2 focus:ring-purple-400 transition p-2'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-400 transition p-2'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 bg-white shadow-sm focus:border-gray-600 focus:ring-2 focus:ring-gray-400 transition p-2'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 bg-white shadow-sm focus:border-blue-600 focus:ring-2 focus:ring-blue-400 transition p-2'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 bg-white shadow-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-400 transition p-2'
            }),
        }
    
    def clean_profile_picture(self):
        """Validate and process profile picture"""
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture:
            # Validate the image
            is_valid, message = image_handler.validate_image(profile_picture)
            if not is_valid:
                raise forms.ValidationError(message)
            
            # Process the image
            processed_image = image_handler.process_profile_picture(
                profile_picture, 
                self.instance.user.id if self.instance.user else 'temp'
            )
            
            if processed_image:
                return processed_image
            else:
                raise forms.ValidationError("Failed to process the image. Please try a different image.")
        
        return profile_picture


class PortfolioForm(forms.ModelForm):
    """Form for creating/editing portfolio"""
    class Meta:
        model = Portfolio
        fields = ['title', 'theme', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border border-gray-400 bg-white px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm placeholder-gray-400 italic',
                'placeholder': 'Target Position or Current Role (e.g., "Full Stack Developer")',
            }),
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class EducationForm(forms.ModelForm):
    """Form for education entries"""
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-input'}),
            'degree': forms.TextInput(attrs={'class': 'form-input'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }


class ExperienceForm(forms.ModelForm):
    """Form for experience entries"""
    class Meta:
        model = Experience
        fields = ['company', 'position', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-input'}),
            'position': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
        }


class SkillForm(forms.ModelForm):
    """Form for skill entries"""
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'proficiency': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-input'}),
        }


class ProjectForm(forms.ModelForm):
    """Form for project entries with enhanced image handling"""
    class Meta:
        model = Project
        fields = ['name', 'description', 'tech_stack', 'github_url', 'live_url', 'image', 'featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Project name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea', 'placeholder': 'Describe your project...'}),
            'tech_stack': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Python, Django, JavaScript, React'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/yourusername/project'}),
            'live_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://yourproject.com'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    def clean_image(self):
        """Validate and process project image"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Validate the image
            is_valid, message = image_handler.validate_image(image)
            if not is_valid:
                raise forms.ValidationError(message)
            
            # Process the image
            project_name = self.cleaned_data.get('name', 'project')
            processed_image = image_handler.process_project_image(image, project_name)
            
            if processed_image:
                return processed_image
            else:
                raise forms.ValidationError("Failed to process the image. Please try a different image.")
        
        return image


class CertificationForm(forms.ModelForm):
    """Form for certification entries"""
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiry_date', 'credential_id', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-input'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'credential_id': forms.TextInput(attrs={'class': 'form-input'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-input'}),
        }

