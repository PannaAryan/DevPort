# DevPort - Developer Portfolio Builder

🚀 **A complete Django-based web platform where developers can create, preview, and export professional portfolios in minutes.**

![DevPort Banner](https://via.placeholder.com/800x200/1e293b/ffffff?text=DevPort+-+Build+Your+Developer+Portfolio)

## 🎯 Overview

DevPort is a comprehensive web application that allows developers to:

- **Sign up and authenticate** with a secure user system
- **Build portfolios** using intuitive form-based builders
- **Preview in real-time** with professional themes
- **Export portfolios** as ZIP files or PDFs
- **Share public links** to showcase their work

## ✨ Features

### 🔐 Authentication System
- User registration and login
- Secure password handling
- Session management
- Profile management

### 📝 Portfolio Builder
- **Personal Information**: Bio, contact details, profile picture
- **Work Experience**: Company, role, duration, descriptions
- **Education**: Degrees, institutions, achievements
- **Skills**: Categorized technical skills with proficiency levels
- **Projects**: Showcase with descriptions, tech stacks, and links
- **Certifications**: Professional credentials and achievements

### 🎨 Live Preview & Themes
- **Real-time preview** as you build
- **Professional themes**:
  - Minimal Dark (default)
  - Modern Light
  - Creative
- **Responsive design** for all devices

### 📤 Export & Share
- **ZIP Export**: Download complete portfolio as HTML/CSS
- **PDF Export**: Professional PDF version
- **Public Links**: Share portfolio with custom URLs
- **Download tracking**: Monitor portfolio views

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django 4.2.23 (Python) |
| **Database** | PostgreSQL |
| **Frontend** | HTML5, Tailwind CSS, JavaScript |
| **Authentication** | Django Auth |
| **Export** | WeasyPrint (PDF), Python zipfile |
| **Styling** | Tailwind CSS |

## 📋 Requirements

- Python 3.11+
- PostgreSQL 12+
- Node.js 18+ (for frontend assets)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd devport
```

### 2. Set Up Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database
```bash
# Create PostgreSQL database
createdb devport_db

# Update settings.py with your database credentials
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access DevPort!




## License

This project is not open-source.  
© 2025 Panna Das. All rights reserved.
