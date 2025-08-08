import os
import tempfile
from io import BytesIO
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from django.conf import settings


class PortfolioPDFGenerator:
    """Enhanced PDF generator for portfolios with better formatting and layout"""
    
    def __init__(self):
        self.font_config = FontConfiguration()
        
    def generate_pdf(self, portfolio, user_profile, request):
        """Generate a well-formatted PDF from portfolio data"""
        
        # Prepare context data
        context = {
            'portfolio': portfolio,
            'user_profile': user_profile,
            'education_list': portfolio.education.all(),
            'experience_list': portfolio.experience.all(),
            'skills_by_category': self._group_skills_by_category(portfolio.skills.all()),
            'projects_list': portfolio.projects.all(),
            'certifications_list': portfolio.certifications.all(),
            'base_url': request.build_absolute_uri('/'),
        }
        
        # Render HTML content using PDF-specific template
        html_content = render_to_string('portfolio/pdf/portfolio_pdf.html', context, request=request)
        
        # Create PDF with enhanced settings
        html_doc = HTML(
            string=html_content,
            base_url=request.build_absolute_uri('/'),
            encoding='utf-8'
        )
        
        # Enhanced CSS for better PDF formatting
        pdf_css = CSS(string=self._get_pdf_css())
        
        # Generate PDF with optimized settings
        pdf_bytes = html_doc.write_pdf(
            stylesheets=[pdf_css],
            font_config=self.font_config,
            optimize_images=True,
            presentational_hints=True,
        )
        
        return pdf_bytes
    
    def _group_skills_by_category(self, skills):
        """Group skills by category"""
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        return skills_by_category
    
    def _get_pdf_css(self):
        """Return optimized CSS for PDF generation"""
        return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
        
        /* Page setup */
        @page {
            size: A4;
            margin: 1.5cm;
            @top-center {
                content: "Portfolio - " attr(data-title);
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: counter(page) " / " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #2d3748;
            background: white;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Playfair Display', serif;
            font-weight: 600;
            margin-bottom: 0.5em;
            page-break-after: avoid;
        }
        
        h1 {
            font-size: 28pt;
            color: #1a202c;
            margin-bottom: 0.3em;
        }
        
        h2 {
            font-size: 18pt;
            color: #2d3748;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.3em;
        }
        
        h3 {
            font-size: 14pt;
            color: #2d3748;
            margin-bottom: 0.5em;
        }
        
        p {
            margin-bottom: 0.8em;
            text-align: justify;
        }
        
        /* Header section */
        .pdf-header {
            text-align: center;
            margin-bottom: 2em;
            padding-bottom: 1.5em;
            border-bottom: 3px solid #4299e1;
            page-break-after: avoid;
        }
        
        .pdf-name {
            font-size: 32pt;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 0.2em;
        }
        
        .pdf-title {
            font-size: 16pt;
            color: #4299e1;
            font-weight: 500;
            margin-bottom: 0.8em;
        }
        
        .pdf-bio {
            font-size: 12pt;
            color: #4a5568;
            max-width: 80%;
            margin: 0 auto 1em;
            line-height: 1.6;
        }
        
        .pdf-contact {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1.5em;
            font-size: 10pt;
            color: #718096;
        }
        
        .pdf-contact-item {
            display: flex;
            align-items: center;
            gap: 0.3em;
        }
        
        /* Profile picture */
        .pdf-profile-picture {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #e2e8f0;
            margin: 0 auto 1em;
            display: block;
        }
        
        /* Sections */
        .pdf-section {
            margin-bottom: 2em;
            page-break-inside: avoid;
        }
        
        .pdf-section-title {
            font-size: 18pt;
            color: #2d3748;
            margin-bottom: 1em;
            padding-bottom: 0.3em;
            border-bottom: 2px solid #e2e8f0;
            page-break-after: avoid;
        }
        
        /* Timeline items */
        .pdf-timeline-item {
            margin-bottom: 1.5em;
            padding-left: 1em;
            border-left: 3px solid #e2e8f0;
            page-break-inside: avoid;
        }
        
        .pdf-timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5em;
            flex-wrap: wrap;
            gap: 0.5em;
        }
        
        .pdf-timeline-title {
            font-size: 13pt;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.2em;
        }
        
        .pdf-timeline-company {
            font-size: 12pt;
            color: #4299e1;
            font-weight: 500;
            margin-bottom: 0.2em;
        }
        
        .pdf-timeline-location {
            font-size: 10pt;
            color: #718096;
        }
        
        .pdf-timeline-date {
            background: #4299e1;
            color: white;
            padding: 0.3em 0.8em;
            border-radius: 4px;
            font-size: 9pt;
            font-weight: 500;
            white-space: nowrap;
        }
        
        .pdf-timeline-description {
            color: #4a5568;
            font-size: 10pt;
            line-height: 1.5;
            margin-top: 0.5em;
        }
        
        /* Skills */
        .pdf-skills-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5em;
            margin-bottom: 1em;
        }
        
        .pdf-skill-category {
            background: #f7fafc;
            padding: 1em;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            page-break-inside: avoid;
        }
        
        .pdf-skill-category h3 {
            font-size: 12pt;
            color: #2d3748;
            margin-bottom: 0.8em;
            font-weight: 600;
        }
        
        .pdf-skill-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5em;
            font-size: 10pt;
        }
        
        .pdf-skill-name {
            color: #2d3748;
            font-weight: 500;
        }
        
        .pdf-skill-level {
            display: flex;
            gap: 2px;
        }
        
        .pdf-skill-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #e2e8f0;
        }
        
        .pdf-skill-dot.filled {
            background: #4299e1;
        }
        
        /* Projects */
        .pdf-projects-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5em;
        }
        
        .pdf-project-card {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 1.2em;
            page-break-inside: avoid;
        }
        
        .pdf-project-title {
            font-size: 12pt;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5em;
        }
        
        .pdf-project-description {
            font-size: 10pt;
            color: #4a5568;
            line-height: 1.4;
            margin-bottom: 0.8em;
        }
        
        .pdf-project-tech {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3em;
            margin-bottom: 0.8em;
        }
        
        .pdf-tech-tag {
            background: #4299e1;
            color: white;
            padding: 0.2em 0.5em;
            border-radius: 3px;
            font-size: 8pt;
            font-weight: 500;
        }
        
        .pdf-project-links {
            font-size: 9pt;
            color: #4299e1;
        }
        
        /* Certifications */
        .pdf-certifications-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1em;
        }
        
        .pdf-certification-item {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #48bb78;
            padding: 1em;
            border-radius: 0 6px 6px 0;
            page-break-inside: avoid;
        }
        
        .pdf-certification-name {
            font-size: 11pt;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.3em;
        }
        
        .pdf-certification-org {
            font-size: 10pt;
            color: #48bb78;
            font-weight: 500;
            margin-bottom: 0.3em;
        }
        
        .pdf-certification-date {
            font-size: 9pt;
            color: #718096;
        }
        
        /* Utilities */
        .pdf-two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2em;
        }
        
        .pdf-break-before {
            page-break-before: always;
        }
        
        .pdf-break-after {
            page-break-after: always;
        }
        
        .pdf-no-break {
            page-break-inside: avoid;
        }
        
        /* Links */
        a {
            color: #4299e1;
            text-decoration: none;
        }
        
        /* Images */
        img {
            max-width: 100%;
            height: auto;
        }
        
        /* Footer */
        .pdf-footer {
            margin-top: 3em;
            padding-top: 1em;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 9pt;
            color: #718096;
        }
        
        /* Responsive adjustments for smaller content */
        @media print {
            .pdf-skills-grid,
            .pdf-projects-grid,
            .pdf-certifications-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def create_response(self, pdf_bytes, filename):
        """Create HTTP response for PDF download"""
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)
        return response

