from flask import Blueprint, render_template

bp = Blueprint('about', __name__, url_prefix='/about')

@bp.route('/')
def index():
    return render_template('about.html', section='osint')

@bp.route('/responsible')
def responsible():
    return render_template('about.html', section='responsible')