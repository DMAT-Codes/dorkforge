from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(Username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(Email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(Username=username, Email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(Username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# =========================================================
# DELETE PROFILE ROUTE
# =========================================================
@bp.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
    """Allow a logged-in user to delete their own account."""
    user = User.query.get(current_user.User_ID)
    
    # Log the user out before deleting them
    logout_user()
    
    # Delete user from database (saved queries will cascade delete automatically)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Your account and all saved queries have been permanently deleted.', 'success')
        
    return redirect(url_for('auth.register'))