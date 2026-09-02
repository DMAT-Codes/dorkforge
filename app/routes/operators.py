from flask import Blueprint, render_template

bp = Blueprint('operators', __name__, url_prefix='/guide')

@bp.route('/')
def index():
    operators = [
        {'name': 'site:', 'syntax': 'site:example.com', 'description': 'Restricts search results to a specific domain or subdomain.', 'example': 'site:example.com "annual report"', 'security': 'Useful for checking what content of your domain is indexed by Google.'},
        {'name': 'filetype:', 'syntax': 'filetype:pdf', 'description': 'Limits results to files of a specific type (pdf, doc, xls, etc.).', 'example': 'site:example.com filetype:pdf', 'security': 'Helps discover sensitive documents that are publicly accessible.'},
        {'name': 'intitle:', 'syntax': 'intitle:"login"', 'description': 'Searches for pages with specific words in the page title.', 'example': 'intitle:"admin" site:example.com', 'security': 'Can reveal admin panels or login pages that should be restricted.'},
        {'name': 'inurl:', 'syntax': 'inurl:admin', 'description': 'Searches for pages with specific words in the URL.', 'example': 'inurl:login site:example.com', 'security': 'Identifies potentially sensitive directories or pages.'},
        {'name': 'intext:', 'syntax': 'intext:"confidential"', 'description': 'Searches for pages that contain specific words in the page text.', 'example': 'site:example.com intext:"internal use"', 'security': 'Can find confidential information exposed on public pages.'},
        {'name': 'exact phrase', 'syntax': '"exact phrase"', 'description': 'Searches for an exact sequence of words.', 'example': '"annual report" site:example.com', 'security': 'Helps find specific documents or pages containing sensitive phrases.'},
        {'name': 'exclusion (-)', 'syntax': '-term', 'description': 'Excludes results containing the specified term.', 'example': 'site:example.com -"test"', 'security': 'Helps filter out irrelevant results.'},
        {'name': 'OR', 'syntax': 'term1 OR term2', 'description': 'Searches for either term.', 'example': 'site:example.com "report" OR "analysis"', 'security': 'Broadens search to cover multiple variants.'},
        {'name': 'before:', 'syntax': 'before:2020-01-01', 'description': 'Filters results by date range.', 'example': 'site:example.com before:2020-01-01', 'security': 'Can find older documents that may contain outdated info.'},
        {'name': 'after:', 'syntax': 'after:2020-01-01', 'description': 'Filters results by date range.', 'example': 'site:example.com after:2020-01-01', 'security': 'Can find recent documents that may be relevant.'},
    ]
    return render_template('operators.html', operators=operators)