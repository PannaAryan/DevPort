import os
import zipfile
import tempfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

class PortfolioZipExporter:
    def create_portfolio_zip(self, portfolio, user_profile, request):
        """Create a ZIP file containing the portfolio website"""
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Render HTML content
            context = {
                'portfolio': portfolio,
                'user_profile': user_profile,
                'education_list': portfolio.education.all(),
                'experience_list': portfolio.experience.all(),
                'skills_by_category': self._group_skills_by_category(portfolio.skills.all()),
                'projects_list': portfolio.projects.all(),
                'certifications_list': portfolio.certifications.all(),
            }
            
            html_content = render_to_string(f'portfolio/themes/{portfolio.theme}.html', context)
            
            # Write HTML file
            html_file_path = os.path.join(temp_dir, 'index.html')
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(html_file_path, 'index.html')
                
                # Add assets if needed
                # TODO: Add CSS, JS, images
            
            zip_buffer.seek(0)
            
            # Create response
            response = HttpResponse(zip_buffer.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{portfolio.slug}_portfolio.zip"'
            
            return response
    
    def _group_skills_by_category(self, skills):
        """Group skills by category"""
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        return skills_by_category

zip_exporter = PortfolioZipExporter()