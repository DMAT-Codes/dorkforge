from app import db
from app.models import Template

# Seed data for the template library
SEED_TEMPLATES = [
    {
        'category': 'Documents',
        'name': 'Public PDF Documents',
        'query_string': 'site:example.com filetype:pdf',
        'explanation': 'Finds all PDF files publicly indexed on the domain.',
        'security_context': 'Exposes potentially sensitive documents.'
    },
    {
        'category': 'Documents',
        'name': 'Internal Documents',
        'query_string': 'site:example.com intitle:"internal" filetype:pdf',
        'explanation': 'Finds PDFs with "internal" in the title.',
        'security_context': 'Internal documents should not be publicly indexed.'
    },
    {
        'category': 'Documents',
        'name': 'Financial Reports',
        'query_string': 'site:example.com filetype:pdf intitle:"report" OR "financial"',
        'explanation': 'Finds financial or annual reports.',
        'security_context': 'Financial documents may contain sensitive data.'
    },
    {
        'category': 'Web Interfaces',
        'name': 'Login Pages',
        'query_string': 'site:example.com intitle:"login" OR intitle:"admin"',
        'explanation': 'Searches for pages with login or admin in the title.',
        'security_context': 'Helps identify exposed admin panels.'
    },
    {
        'category': 'Web Interfaces',
        'name': 'Admin Panel Discovery',
        'query_string': 'site:example.com intitle:"admin panel"',
        'explanation': 'Explicitly searches for admin panel in page titles.',
        'security_context': 'Exposed admin panels are a critical security risk.'
    },
    {
        'category': 'Exposure',
        'name': 'Directory Listings',
        'query_string': 'site:example.com intitle:"index of"',
        'explanation': 'Finds open directory listings.',
        'security_context': 'Directory listings can expose sensitive files.'
    },
    {
        'category': 'Exposure',
        'name': 'Backup Files',
        'query_string': 'site:example.com filetype:sql OR filetype:bak',
        'explanation': 'Finds backup files that may be exposed.',
        'security_context': 'Backup files often contain sensitive data.'
    },
    {
        'category': 'Exposure',
        'name': 'Configuration Files',
        'query_string': 'site:example.com filetype:conf OR filetype:config',
        'explanation': 'Finds configuration files.',
        'security_context': 'Config files may contain credentials.'
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

    # Fallback to in-memory list if DB is empty
    if not rows:
        rows = SEED_TEMPLATES
        grouped = {}
        for t in rows:
            grouped.setdefault(t['category'], []).append(t)
        return grouped

    grouped = {}
    for t in rows:
        grouped.setdefault(t.category, []).append({
            'name': t.name,
            'category': t.category,
            'description': t.explanation,
            'query': t.query_string,
            'explanation': t.explanation,
            'security': t.security_context,
        })
    return grouped