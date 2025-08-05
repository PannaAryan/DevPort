from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class PortfolioPDFGenerator:
    def generate_pdf(self, portfolio, user_profile, request):
        """Generate PDF from portfolio data"""
        
        context = {
            'portfolio': portfolio,
            'user_profile': user_profile,
            'education_list': portfolio.education.all(),
            'experience_list': portfolio.experience.all(),
            'skills_by_category': self._group_skills_by_category(portfolio.skills.all()),
            'projects_list': portfolio.projects.all(),
            'certifications_list': portfolio.certifications.all(),
        }
        
        # Render HTML template for PDF
        html_content = render_to_string('portfolio/pdf/portfolio_pdf.html', context)
        
        # Generate PDF
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        css = CSS(string=self._get_pdf_css())
        
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer, stylesheets=[css], font_config=font_config)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    def create_response(self, pdf_bytes, filename):
        """Create HTTP response for PDF download"""
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def _group_skills_by_category(self, skills):
        """Group skills by category"""
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        return skills_by_category
    
    def _get_pdf_css(self):
        """Return CSS for PDF styling"""
        return """
        @page {
            margin: 1in;
            size: A4;
        }
        
        body {
            font-family: Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            color: #333;
        }
        
        h1 {
            font-size: 24pt;
            margin-bottom: 10pt;
            color: #2c3e50;
        }
        
        h2 {
            font-size: 18pt;
            margin-top: 20pt;
            margin-bottom: 10pt;
            color: #34495e;
            border-bottom: 2pt solid #3498db;
            padding-bottom: 5pt;
        }
        
        h3 {
            font-size: 14pt;
            margin-top: 15pt;
            margin-bottom: 5pt;
            color: #2c3e50;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30pt;
        }
        
        .section {
            margin-bottom: 25pt;
        }
        
        .skill-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10pt;
        }
        
        .project {
            margin-bottom: 15pt;
            padding: 10pt;
            border: 1pt solid #bdc3c7;
            border-radius: 5pt;
        }
        
        .tech-stack {
            font-style: italic;
            color: #7f8c8d;
        }
        """