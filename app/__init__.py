import secrets
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    from app.routes.auth import auth
    from app.routes.onboarding import onboarding
    from app.routes.dashboard import dashboard
    from app.routes.chatbot import chatbot
    from app.routes.test_routes import test
    from app.routes.scheduler import scheduler as scheduler_blueprint
    from app.routes.gamification import gamification

    app.register_blueprint(auth)
    app.register_blueprint(onboarding)
    app.register_blueprint(dashboard)
    app.register_blueprint(chatbot)
    app.register_blueprint(test)
    app.register_blueprint(scheduler_blueprint)
    app.register_blueprint(gamification)

    # ── Security headers ──────────────────────────────────────────────────────
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # ── CSRF token injected into every template ───────────────────────────────
    @app.context_processor
    def inject_csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return dict(csrf_token=session.get('csrf_token'))

    # ── Custom error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template('errors/429.html'), 429

    # ── Health check at /health ───────────────────────────────────────────────
    @app.route('/health')
    def health():
        import os
        from datetime import datetime
        from flask import jsonify
        from app.models import User, ChatMessage

        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception:
            db_status = 'error'

        gemini_key = app.config.get('GEMINI_API_KEY')
        gemini_status = 'configured' if (gemini_key and gemini_key != 'paste_your_key_here') else 'missing'

        try:
            total_users = User.query.count()
            total_messages = ChatMessage.query.count()
        except Exception:
            total_users = 0
            total_messages = 0

        return jsonify({
            'status': 'healthy',
            'app': 'SKILL PILOT',
            'version': '1.0.0',
            'database': db_status,
            'gemini_api': gemini_status,
            'total_users': total_users,
            'total_messages': total_messages,
            'uptime': 'running',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        })

    with app.app_context():
        from app import models
        from app.services.gamification import seed_badges, seed_challenges
        db.create_all()
        seed_badges()
        seed_challenges()
        print("✅ SKILL PILOT database ready")

    return app
