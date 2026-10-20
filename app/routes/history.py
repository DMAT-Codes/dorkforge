from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import SavedQuery, User

bp = Blueprint('history', __name__, url_prefix='/history')

@bp.route('/')
def index():
    """History and Saved Queries page."""
    return render_template('history.html')

# --- API Endpoints for Saved Queries ---

@bp.route('/api/saved', methods=['GET'])
def get_saved_queries():
    """Fetch all saved queries from the database, newest first."""
    queries = SavedQuery.query.order_by(SavedQuery.Date_Saved.desc()).all()
    results = []
    for q in queries:
        results.append({
            'id': q.Query_ID,
            'query': q.Query_String,
            'title': q.Title,
            'date': q.Date_Saved.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(results)

@bp.route('/api/saved', methods=['POST'])
def save_query():
    """Save a new query to the database."""
    data = request.get_json()
    query_string = data.get('query')
    title = data.get('title', 'Untitled Query')
    
    if not query_string:
        return jsonify({'error': 'Query string is required'}), 400

    # Get the Guest user ID (created automatically on startup)
    guest_user = User.query.filter_by(Username='Guest').first()
    user_id = guest_user.User_ID if guest_user else None

    new_query = SavedQuery(
        User_ID=user_id,
        Query_String=query_string,
        Title=title
    )
    db.session.add(new_query)
    db.session.commit()

    return jsonify({'message': 'Query saved successfully', 'id': new_query.Query_ID}), 201

@bp.route('/api/saved/<int:query_id>', methods=['DELETE'])
def delete_saved_query(query_id):
    """Delete a saved query by its ID."""
    query = SavedQuery.query.get(query_id)
    if not query:
        return jsonify({'error': 'Query not found'}), 404
    
    db.session.delete(query)
    db.session.commit()
    return jsonify({'message': 'Query deleted successfully'})