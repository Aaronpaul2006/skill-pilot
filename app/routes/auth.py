import re
import html
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt, limiter
from app.models import User, LearningProfile

auth = Blueprint('auth', __name__)

# ── Helpers ───────────────────────────────────────────────────────────────────
def sanitize_input(text):
    """Strip HTML tags and extra whitespace."""
    return html.escape(str(text).strip())

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ── Register ──────────────────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        name     = sanitize_input(request.form.get('name', ''))
        email    = sanitize_input(request.form.get('email', '').lower())
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Required-field check
        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for('auth.register'))

        # Length limits
        if len(name) > 100:
            flash("Name too long (max 100 characters).", "error")
            return redirect(url_for('auth.register'))
        if len(email) > 120:
            flash("Email too long (max 120 characters).", "error")
            return redirect(url_for('auth.register'))
        if len(password) > 128:
            flash("Password too long (max 128 characters).", "error")
            return redirect(url_for('auth.register'))

        # Email format
        if not validate_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for('auth.register'))

        try:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(name=name, email=email, password=hashed_pw)
            db.session.add(user)
            db.session.commit()

            profile = LearningProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()

            flash("Account created! Please complete your learning profile.", "success")
            return redirect('/onboarding')
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


# ── Login ─────────────────────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        email    = sanitize_input(request.form.get('email', '').lower())
        password = request.form.get('password', '')

        # Login-attempt throttle (session-based, in addition to rate limiter)
        session['login_attempts'] = session.get('login_attempts', 0) + 1
        if session['login_attempts'] >= 5:
            flash("Too many failed attempts. Please wait and try again.", "error")
            return redirect(url_for('auth.login'))

        try:
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                session['login_attempts'] = 0   # reset on success
                login_user(user)
                flash(f"Welcome back, {user.name}!", "success")

                if user.learning_profile and user.learning_profile.onboarding_done:
                    return redirect('/dashboard')
                else:
                    return redirect('/onboarding')
            else:
                flash("Invalid email or password.", "error")
                return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f"Login error: {str(e)}", "error")
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


# ── Logout ────────────────────────────────────────────────────────────────────
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('login_attempts', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))


# ── Profile ───────────────────────────────────────────────────────────────────
@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)
