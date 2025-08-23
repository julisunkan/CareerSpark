# PythonAnywhere Deployment Instructions

## Prerequisites
- PythonAnywhere account (Hacker plan or higher for custom domains)
- Python 3.10 environment

## Step 1: Upload Files
1. Upload all project files to your PythonAnywhere files section
2. Place them in `/home/yourusername/mysite/` directory

## Step 2: Install Dependencies
Open a Bash console in PythonAnywhere and run:

```bash
cd ~/mysite
pip3.10 install --user email-validator flask flask-sqlalchemy fpdf2 gunicorn jinja2 language-tool-python nltk numpy psycopg2-binary pypdf2 python-docx scikit-learn spacy weasyprint werkzeug
```

## Step 3: Download spaCy Model
```bash
python3.10 -m spacy download en_core_web_sm
```

## Step 4: Create Directories
```bash
mkdir -p uploads downloads static/generated_images data logs
chmod 755 uploads downloads data logs
```

## Step 5: Configure WSGI
1. Go to Web tab in PythonAnywhere dashboard
2. Create a new web app (Flask, Python 3.10)
3. Update the WSGI configuration file with the content from `wsgi.py`
4. Update the path in wsgi.py: `/home/yourusername/mysite` (replace 'yourusername')

## Step 6: Environment Variables
Generate a secure secret key and update the WSGI file:
```bash
python3.10 -c "import secrets; print('SECRET_KEY:', secrets.token_hex(32))"
```

Update these in the WSGI file:
- `SESSION_SECRET`: Use the generated secret key
- `FLASK_ENV`: Set to 'production'
- Update the project path: `/home/yourusername/mysite`

## Step 7: Static Files
Configure static files mapping in the Web tab:
- URL: `/static/`
- Directory: `/home/yourusername/mysite/static/`

## Step 8: Initialize Data
The app will automatically create the `data/resume_data.json` file on first use.

## Step 9: Reload and Test
1. Click "Reload" button in Web tab
2. Visit your PythonAnywhere URL to test the application

## Important Notes
- The app includes automatic file cleanup (24-hour deletion)
- Grammar checking uses LanguageTool API (rate limited)
- PDF generation has fallback to FPDF if WeasyPrint fails
- Application works offline as a Progressive Web App

## Troubleshooting
- Check error logs in PythonAnywhere dashboard
- Ensure all dependencies are installed correctly
- Verify file permissions for uploads/downloads directories
- Check that static files are serving correctly