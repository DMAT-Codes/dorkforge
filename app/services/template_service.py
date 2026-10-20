from app import db
from app.models import Template

# Seed data for the template library
SEED_TEMPLATES = [
    {
        'Category': 'Documents',
        'Name': 'Public PDF Documents',
        'Query_String': 'site:example.com filetype:pdf',
        'Explanation': 'Finds all PDF files publicly indexed on the domain.',
        'Security_Context': 'Exposes potentially sensitive documents.'
    },
    {
        'Category': 'Documents',
        'Name': 'Internal Documents',
        'Query_String': 'site:example.com intitle:"internal" filetype:pdf',
        'Explanation': 'Finds PDFs with "internal" in the title.',
        'Security_Context': 'Internal documents should not be publicly indexed.'
    },
    {
        'Category': 'Documents',
        'Name': 'Financial Reports',
        'Query_String': 'site:example.com filetype:pdf intitle:"report" OR "financial"',
        'Explanation': 'Finds financial or annual reports.',
        'Security_Context': 'Financial documents may contain sensitive data.'
    },
    {
        'Category': 'Web Interfaces',
        'Name': 'Login Pages',
        'Query_String': 'site:example.com intitle:"login" OR intitle:"admin"',
        'Explanation': 'Searches for pages with login or admin in the title.',
        'Security_Context': 'Helps identify exposed admin panels.'
    },
    {
        'Category': 'Web Interfaces',
        'Name': 'Admin Panel Discovery',
        'Query_String': 'site:example.com intitle:"admin panel"',
        'Explanation': 'Explicitly searches for admin panel in page titles.',
        'Security_Context': 'Exposed admin panels are a critical security risk.'
    },
    {
        'Category': 'Exposure',
        'Name': 'Directory Listings',
        'Query_String': 'site:example.com intitle:"index of"',
        'Explanation': 'Finds open directory listings.',
        'Security_Context': 'Directory listings can expose sensitive files.'
    },
    {
        'Category': 'Exposure',
        'Name': 'Backup Files',
        'Query_String': 'site:example.com filetype:sql OR filetype:bak',
        'Explanation': 'Finds backup files that may be exposed.',
        'Security_Context': 'Backup files often contain sensitive data.'
    },
    {
        'Category': 'Exposure',
        'Name': 'Configuration Files',
        'Query_String': 'site:example.com filetype:conf OR filetype:config',
        'Explanation': 'Finds configuration files.',
        'Security_Context': 'Config files may contain credentials.'
    },
]

def seed_templates():
    """Insert seed templates into the database if none exist."""
    if Template.query.count() > 0:
        return
    for item in SEED_TEMPLATES:
        db.session.add(Template(**item))
    db.session.commit()

def get_templates_grouped():
    """Return templates grouped by category."""
    rows = Template.query.all()

    if not rows:
        return {}

    grouped = {}
    for t in rows:
        grouped.setdefault(t.Category, []).append({
            'name': t.Name,
            'category': t.Category,
            'description': t.Explanation,
            'query': t.Query_String,
            'explanation': t.Explanation,
            'security': t.Security_Context,
        })
    return grouped