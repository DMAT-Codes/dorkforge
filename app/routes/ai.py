from flask import Blueprint, render_template, request, jsonify
from app.services.groq_service import generate_dorks, GroqError

bp = Blueprint('ai', __name__, url_prefix='/ai')

# Maximum allowed characters for a user goal
MAX_GOAL_LENGTH = 500


@bp.route('/')
def index():
    """AI Assistant page."""
    return render_template('ai.html')


@bp.route('/api/generate', methods=['POST'])
def generate():
    """API endpoint: validate input, then delegate to the Groq service."""
    data = request.get_json() or {}
    goal = (data.get('goal') or '').strip()

    # --- Input validation ---
    if not goal:
        return jsonify({'error': 'Please enter a goal.'}), 400

    if len(goal) > MAX_GOAL_LENGTH:
        return jsonify({
            'error': f'Goal is too long. Maximum {MAX_GOAL_LENGTH} characters allowed.'
        }), 400

    # --- Delegate to service layer ---
    try:
        result = generate_dorks(goal)
        return jsonify(result)
    except GroqError as exc:
        return jsonify({'error': exc.message}), exc.status_code