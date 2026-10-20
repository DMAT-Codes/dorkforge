from flask import Blueprint, render_template
from app.services.template_service import get_templates_grouped

bp = Blueprint('templates', __name__, url_prefix='/templates')


@bp.route('/')
def index():
    """Template Library page (reads from database)."""
    categories = get_templates_grouped()
    return render_template('templates.html', categories=categories)