import os
import zipfile
import tempfile
import shutil
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Portfolio, UserProfile


class PortfolioZipExporter:
    """Enhanced ZIP export utility for portfolios"""
    
    def __init__(self):
        self.temp_dir = None
        self.zip_path = None
    
    def create_portfolio_zip(self, portfolio, user_profile, request):
        """Create a complete ZIP package of the portfolio"""
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            # Prepare context data
            context = {
                'portfolio': portfolio,
                'user_profile': user_profile,
                'education_list': portfolio.education.all(),
                'experience_list': portfolio.experience.all(),
                'skills_by_category': self._group_skills_by_category(portfolio.skills.all()),
                'projects_list': portfolio.projects.all(),
                'certifications_list': portfolio.certifications.all(),
                'base_url': '',  # Use relative paths for offline viewing
            }
            
            # Create portfolio structure
            self._create_portfolio_structure()
            
            # Generate HTML files
            self._generate_html_files(portfolio, context, request)
            
            # Copy CSS and JS assets
            self._copy_assets(portfolio.theme)
            
            # Copy images
            self._copy_images(user_profile, portfolio)
            
            # Create README file
            self._create_readme(portfolio, user_profile)
            
            # Create ZIP file
            zip_filename = f"{portfolio.slug}_portfolio.zip"
            self.zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
            
            self._create_zip_archive()
            
            # Read ZIP file and create response
            with open(self.zip_path, 'rb') as zip_file:
                response = HttpResponse(zip_file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                response['Content-Length'] = os.path.getsize(self.zip_path)
                return response
                
        finally:
            # Cleanup temporary files
            self._cleanup()
    
    def _create_portfolio_structure(self):
        """Create directory structure for the portfolio"""
        directories = [
            'assets',
            'assets/css',
            'assets/js',
            'assets/images',
            'assets/fonts',
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.temp_dir, directory), exist_ok=True)
    
    def _generate_html_files(self, portfolio, context, request):
        """Generate HTML files for the portfolio"""
        
        # Main portfolio HTML
        html_content = render_to_string(
            f'portfolio/themes/{portfolio.theme}.html', 
            context, 
            request=request
        )
        
        # Process HTML to use relative paths
        html_content = self._process_html_for_offline(html_content)
        
        # Write main HTML file
        with open(os.path.join(self.temp_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate alternative theme versions
        themes = ['minimal_dark', 'modern_light', 'creative_burst', 'tech_noir', 'professional_corporate', 'gradient_showcase']
        
        for theme in themes:
            if theme != portfolio.theme:
                try:
                    theme_context = context.copy()
                    theme_html = render_to_string(
                        f'portfolio/themes/{theme}.html',
                        theme_context,
                        request=request
                    )
                    theme_html = self._process_html_for_offline(theme_html)
                    
                    with open(os.path.join(self.temp_dir, f'{theme}.html'), 'w', encoding='utf-8') as f:
                        f.write(theme_html)
                except:
                    # Skip if theme template doesn't exist
                    pass
    
    def _copy_assets(self, theme):
        """Copy CSS, JS, and other assets"""
        
        # Create comprehensive CSS file
        css_content = self._generate_comprehensive_css(theme)
        with open(os.path.join(self.temp_dir, 'assets', 'css', 'style.css'), 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Create JavaScript file
        js_content = self._generate_comprehensive_js()
        with open(os.path.join(self.temp_dir, 'assets', 'js', 'script.js'), 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        # Copy theme switcher
        theme_switcher_js = self._generate_theme_switcher_js()
        with open(os.path.join(self.temp_dir, 'assets', 'js', 'theme-switcher.js'), 'w', encoding='utf-8') as f:
            f.write(theme_switcher_js)
    
    def _copy_images(self, user_profile, portfolio):
        """Copy all images to the assets folder"""
        images_dir = os.path.join(self.temp_dir, 'assets', 'images')
        
        # Copy profile picture
        if user_profile.profile_picture:
            try:
                if default_storage.exists(user_profile.profile_picture.name):
                    source_path = user_profile.profile_picture.path
                    if os.path.exists(source_path):
                        filename = os.path.basename(user_profile.profile_picture.name)
                        dest_path = os.path.join(images_dir, f'profile_{filename}')
                        shutil.copy2(source_path, dest_path)
            except Exception as e:
                print(f"Error copying profile picture: {e}")
        
        # Copy project images
        for project in portfolio.projects.all():
            if project.image:
                try:
                    if default_storage.exists(project.image.name):
                        source_path = project.image.path
                        if os.path.exists(source_path):
                            filename = os.path.basename(project.image.name)
                            dest_path = os.path.join(images_dir, f'project_{filename}')
                            shutil.copy2(source_path, dest_path)
                except Exception as e:
                    print(f"Error copying project image: {e}")
    
    def _create_readme(self, portfolio, user_profile):
        """Create README file for the portfolio"""
        readme_content = f"""# {user_profile.user.first_name} {user_profile.user.last_name} - Portfolio

## About This Portfolio

This is a professional portfolio for {user_profile.user.first_name} {user_profile.user.last_name}, created using DevPort.

**Portfolio Title:** {portfolio.title}
**Generated:** {portfolio.updated_at.strftime('%B %d, %Y')}

## Files Included

- `index.html` - Main portfolio page (Current theme: {portfolio.theme})
- `minimal_dark.html` - Minimal Dark theme version
- `modern_light.html` - Modern Light theme version  
- `creative_burst.html` - Creative Burst theme version
- `tech_noir.html` - Tech Noir theme version
- `professional_corporate.html` - Professional Corporate theme version
- `gradient_showcase.html` - Gradient Showcase theme version
- `assets/` - All CSS, JavaScript, and image files
  - `css/style.css` - Comprehensive styling
  - `js/script.js` - Interactive functionality
  - `js/theme-switcher.js` - Theme switching functionality
  - `images/` - Profile and project images

## How to Use

1. Open `index.html` in any modern web browser
2. All files work offline - no internet connection required
3. Try different theme versions by opening other HTML files
4. All images and assets are included for complete offline viewing

## Contact Information

"""
        
        if user_profile.user.email:
            readme_content += f"- **Email:** {user_profile.user.email}\n"
        if user_profile.location:
            readme_content += f"- **Location:** {user_profile.location}\n"
        if user_profile.website:
            readme_content += f"- **Website:** {user_profile.website}\n"
        if user_profile.github_url:
            readme_content += f"- **GitHub:** {user_profile.github_url}\n"
        if user_profile.linkedin_url:
            readme_content += f"- **LinkedIn:** {user_profile.linkedin_url}\n"
        
        readme_content += f"""
## Technical Details

- **Framework:** DevPort Portfolio Generator
- **Theme:** {portfolio.theme.replace('_', ' ').title()}
- **Responsive:** Yes, works on desktop and mobile
- **Browser Support:** Modern browsers (Chrome, Firefox, Safari, Edge)

---

*This portfolio was generated using DevPort - Professional Portfolio Generator*
"""
        
        with open(os.path.join(self.temp_dir, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_zip_archive(self):
        """Create the final ZIP archive"""
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.temp_dir)
                    zipf.write(file_path, arcname)
    
    def _process_html_for_offline(self, html_content):
        """Process HTML to work offline with relative paths"""
        # Replace CDN links with local fallbacks or remove them
        replacements = {
            # Font Awesome CDN
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css': 'assets/css/fontawesome.css',
            # Google Fonts
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap': 'assets/css/fonts.css',
            'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap': 'assets/css/fonts.css',
            'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap': 'assets/css/fonts.css',
            'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+Pro:wght@300;400;600;700&display=swap': 'assets/css/fonts.css',
            # Image paths
            '/media/': 'assets/images/',
        }
        
        for old, new in replacements.items():
            html_content = html_content.replace(old, new)
        
        return html_content
    
    def _group_skills_by_category(self, skills):
        """Group skills by category"""
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        return skills_by_category
    
    def _generate_comprehensive_css(self, theme):
        """Generate comprehensive CSS for offline viewing"""
        return """
/* DevPort Portfolio - Comprehensive Offline CSS */

/* Font Awesome Icons - Basic fallback */
.fa, .fas, .far, .fab {
    font-family: 'Font Awesome 5 Free', 'Font Awesome 5 Brands', sans-serif;
    font-weight: 900;
    display: inline-block;
}

/* Basic icon replacements */
.fa-envelope:before { content: '✉'; }
.fa-map-marker-alt:before { content: '📍'; }
.fa-globe:before { content: '🌐'; }
.fa-github:before { content: '💻'; }
.fa-linkedin:before { content: '💼'; }
.fa-twitter:before { content: '🐦'; }
.fa-external-link-alt:before { content: '🔗'; }
.fa-code:before { content: '💻'; }
.fa-layer-group:before { content: '🔧'; }
.fa-database:before { content: '🗄️'; }
.fa-tools:before { content: '🛠️'; }
.fa-paint-brush:before { content: '🎨'; }
.fa-star:before { content: '⭐'; }
.fa-certificate:before { content: '🏆'; }
.fa-graduation-cap:before { content: '🎓'; }

/* Base styles for all themes */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        padding: 0 1rem;
    }
    
    .grid {
        grid-template-columns: 1fr !important;
    }
    
    .flex {
        flex-direction: column;
    }
}

/* Theme-specific styles would be injected here based on the selected theme */
/* This is a fallback stylesheet for offline viewing */

.profile-picture {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto;
    display: block;
}

.section {
    margin-bottom: 3rem;
    padding: 2rem 0;
}

.section-title {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

.grid {
    display: grid;
    gap: 2rem;
}

.card {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background 0.3s ease;
}

.btn:hover {
    background: #0056b3;
}

/* Print styles */
@media print {
    body {
        font-size: 12pt;
        line-height: 1.4;
    }
    
    .no-print {
        display: none !important;
    }
    
    .section {
        page-break-inside: avoid;
    }
}
"""
    
    def _generate_comprehensive_js(self):
        """Generate comprehensive JavaScript for offline functionality"""
        return """
// DevPort Portfolio - Comprehensive Offline JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(50px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
    
    // Skill level animations
    const skillItems = document.querySelectorAll('.skill-item');
    skillItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            const dots = this.querySelectorAll('.skill-dot.filled, .skill-orb.filled');
            dots.forEach((dot, index) => {
                setTimeout(() => {
                    dot.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        dot.style.transform = 'scale(1)';
                    }, 200);
                }, index * 100);
            });
        });
    });
    
    // Project card hover effects
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Mobile menu toggle (if exists)
    const mobileToggle = document.querySelector('.mobile-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
        });
    }
    
    // Print functionality
    const printBtn = document.querySelector('.print-btn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Copy contact info functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const text = this.getAttribute('data-copy');
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = 'Copy';
                    }, 2000);
                });
            }
        });
    });
    
    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    console.log('DevPort Portfolio loaded successfully!');
});

// Utility functions
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = section.style.display === 'none' ? 'block' : 'none';
    }
}

// Theme switching functionality
function switchTheme(themeName) {
    const themeFiles = {
        'minimal_dark': 'minimal_dark.html',
        'modern_light': 'modern_light.html',
        'creative_burst': 'creative_burst.html',
        'tech_noir': 'tech_noir.html',
        'professional_corporate': 'professional_corporate.html',
        'gradient_showcase': 'gradient_showcase.html'
    };
    
    if (themeFiles[themeName]) {
        window.location.href = themeFiles[themeName];
    }
}
"""
    
    def _generate_theme_switcher_js(self):
        """Generate theme switcher JavaScript"""
        return """
// Theme Switcher for DevPort Portfolio

document.addEventListener('DOMContentLoaded', function() {
    // Create theme switcher UI
    createThemeSwitcher();
});

function createThemeSwitcher() {
    const themes = [
        { id: 'minimal_dark', name: 'Minimal Dark', file: 'minimal_dark.html' },
        { id: 'modern_light', name: 'Modern Light', file: 'modern_light.html' },
        { id: 'creative_burst', name: 'Creative Burst', file: 'creative_burst.html' },
        { id: 'tech_noir', name: 'Tech Noir', file: 'tech_noir.html' },
        { id: 'professional_corporate', name: 'Professional Corporate', file: 'professional_corporate.html' },
        { id: 'gradient_showcase', name: 'Gradient Showcase', file: 'gradient_showcase.html' }
    ];
    
    // Create theme switcher button
    const switcherBtn = document.createElement('button');
    switcherBtn.innerHTML = '🎨 Switch Theme';
    switcherBtn.className = 'theme-switcher-btn';
    switcherBtn.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: #007bff;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        transition: all 0.3s ease;
    `;
    
    // Create theme menu
    const themeMenu = document.createElement('div');
    themeMenu.className = 'theme-menu';
    themeMenu.style.cssText = `
        position: fixed;
        top: 70px;
        right: 20px;
        z-index: 999;
        background: white;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        padding: 15px;
        min-width: 200px;
        display: none;
        border: 1px solid #e0e0e0;
    `;
    
    // Add theme options
    themes.forEach(theme => {
        const themeOption = document.createElement('div');
        themeOption.className = 'theme-option';
        themeOption.innerHTML = theme.name;
        themeOption.style.cssText = `
            padding: 10px 15px;
            cursor: pointer;
            border-radius: 5px;
            margin-bottom: 5px;
            transition: background 0.2s ease;
            color: #333;
        `;
        
        themeOption.addEventListener('mouseenter', function() {
            this.style.background = '#f0f0f0';
        });
        
        themeOption.addEventListener('mouseleave', function() {
            this.style.background = 'transparent';
        });
        
        themeOption.addEventListener('click', function() {
            window.location.href = theme.file;
        });
        
        themeMenu.appendChild(themeOption);
    });
    
    // Toggle menu visibility
    let menuVisible = false;
    switcherBtn.addEventListener('click', function() {
        menuVisible = !menuVisible;
        themeMenu.style.display = menuVisible ? 'block' : 'none';
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!switcherBtn.contains(e.target) && !themeMenu.contains(e.target)) {
            menuVisible = false;
            themeMenu.style.display = 'none';
        }
    });
    
    // Add to page
    document.body.appendChild(switcherBtn);
    document.body.appendChild(themeMenu);
}
"""
    
    def _cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            if self.zip_path and os.path.exists(self.zip_path):
                os.remove(self.zip_path)
        except Exception as e:
            print(f"Error during cleanup: {e}")


# Global instance
zip_exporter = PortfolioZipExporter()

