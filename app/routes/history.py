from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import SavedQuery

bp = Blueprint('history', __name__, url_prefix='/history')

@bp.route('/')
def index():
    return render_template('history.html')

@bp.route('/api/saved', methods=['GET'])
@login_required
def get_saved_queries():
    queries = SavedQuery.query.filter_by(User_ID=current_user.User_ID).order_by(SavedQuery.Date_Saved.desc()).all()
    results = [{'id': q.Query_ID, 'query': q.Query_String, 'title': q.Title, 'date': q.Date_Saved.strftime('%Y-%m-%d %H:%M')} for q in queries]
    return jsonify(results)

@bp.route('/api/saved', methods=['POST'])
@login_required
def save_query():
    data = request.get_json()
    query_string = data.get('query')
    title = data.get('title', 'Untitled Query')
    
    if not query_string:
        return jsonify({'error': 'Query string is required'}), 400

    new_query = SavedQuery(User_ID=current_user.User_ID, Query_String=query_string, Title=title)
    db.session.add(new_query)
    db.session.commit()

    return jsonify({'message': 'Query saved successfully', 'id': new_query.Query_ID}), 201

@bp.route('/api/saved/<int:query_id>', methods=['DELETE'])
@login_required
def delete_saved_query(query_id):
    query = SavedQuery.query.filter_by(Query_ID=query_id, User_ID=current_user.User_ID).first()
    if not query:
        return jsonify({'error': 'Query not found or unauthorized'}), 404
    
    db.session.delete(query)
    db.session.commit()
    return jsonify({'message': 'Query deleted successfully'})