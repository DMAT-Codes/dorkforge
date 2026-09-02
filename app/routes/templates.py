from flask import Blueprint, render_template

bp = Blueprint('templates', __name__, url_prefix='/templates')

TEMPLATES = [
    {'name': 'Public PDF Documents', 'category': 'Documents', 'description': 'Find PDF documents publicly indexed.', 'query': 'site:example.com filetype:pdf', 'explanation': 'Searches for PDF files on the specified domain.', 'security': 'Exposes potentially sensitive documents.'},
    {'name': 'Login Pages', 'category': 'Web Interfaces', 'description': 'Discover login panels and admin interfaces.', 'query': 'site:example.com intitle:"login" OR intitle:"admin"', 'explanation': 'Searches for pages with login or admin in the title.', 'security': 'Helps identify exposed admin panels.'},
    {'name': 'Admin Panel Discovery', 'category': 'Web Interfaces', 'description': 'Find admin panel pages.', 'query': 'site:example.com intitle:"admin panel"', 'explanation': 'Explicitly searches for admin panel in page titles.', 'security': 'Exposed admin panels are a critical security risk.'},
    {'name': 'Directory Listings', 'category': 'Exposure', 'description': 'Find open directory listings.', 'query': 'site:example.com intitle:"index of"', 'explanation': 'Finds open directory listings.', 'security': 'Directory listings can expose sensitive files.'},
    {'name': 'Backup Files', 'category': 'Exposure', 'description': 'Find exposed backup files.', 'query': 'site:example.com filetype:sql OR filetype:bak', 'explanation': 'Finds backup files that may be exposed.', 'security': 'Backup files often contain sensitive data.'},
    {'name': 'Configuration Files', 'category': 'Exposure', 'description': 'Find exposed configuration files.', 'query': 'site:example.com filetype:conf OR filetype:config', 'explanation': 'Finds configuration files.', 'security': 'Config files may contain credentials.'},
    {'name': 'Internal Documents', 'category': 'Documents', 'description': 'Find internal documents.', 'query': 'site:example.com intitle:"internal" filetype:pdf', 'explanation': 'Finds PDFs with internal in the title.', 'security': 'Internal documents should not be public.'},
    {'name': 'Financial Reports', 'category': 'Documents', 'description': 'Find financial reports.', 'query': 'site:example.com filetype:pdf intitle:"report" OR "financial"', 'explanation': 'Finds financial or report documents.', 'security': 'Financial documents may contain sensitive data.'},
]

@bp.route('/')
def index():
    categories = {}
    for t in TEMPLATES:
        cat = t['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t)
    return render_template('templates.html', categories=categories)