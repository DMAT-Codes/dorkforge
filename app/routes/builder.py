from flask import Blueprint, render_template

bp = Blueprint('builder', __name__, url_prefix='/builder')

@bp.route('/')
def index():
    return render_template('builder.html')