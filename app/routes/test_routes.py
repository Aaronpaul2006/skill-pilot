from flask import Blueprint, jsonify, render_template_string
from app import db
from sqlalchemy import text
import os

test = Blueprint('test', __name__, url_prefix='/test')

# ─────────────────────────────────────────────────────────────────────────────
# Test panel HTML
# ─────────────────────────────────────────────────────────────────────────────
@test.route('/')
def test_panel():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SKILL PILOT — Test Panel</title>
        <style>
            body { background-color: #0a0a0f; color: white; font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            .accent { color: #6c63ff; } .warn { color: #f7971e; } .green { color: #43e97b; }
            h1 { text-align: center; } h2 { margin-top: 0; }
            .container { max-width: 860px; margin: 0 auto; }
            .status { background-color: #1a1a24; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .btn-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
            .btn { background-color: #6c63ff; color: white; text-decoration: none; padding: 10px 15px; border-radius: 5px; display: inline-block; transition: background-color 0.3s; }
            .btn:hover { background-color: #5750d4; }
            .btn.orange { background: #f7971e; } .btn.orange:hover { background: #d4840e; }
            .btn.red { background: #ff6584; } .btn.red:hover { background: #d44060; }
            .btn.green { background: #43e97b; color: #0a0a0f; } .btn.green:hover { background: #2dc760; }
            .section-label { color: #888899; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ SKILL PILOT — Test Panel</h1>
            <div class="status">
                <h2>Status</h2>
                <p>Flask running: <span class="accent">✅</span></p>
                <p>Blueprints registered: <span class="accent">✅</span></p>
                <p>Database ready: <span class="accent">✅</span></p>
                <p>Phase 7 (Polish + Security): <span class="green">✅ ACTIVE</span></p>
            </div>

            <h2>🎬 Demo Controls</h2>
            <div class="btn-group">
                <a href="/test/setup-demo" class="btn green" target="_blank">🚀 Setup Full Demo</a>
                <a href="/test/reset-demo" class="btn red" target="_blank">🔄 Reset Demo</a>
            </div>

            <h2>🔍 System Reports</h2>
            <div class="btn-group">
                <a href="/health" class="btn green" target="_blank">❤️ Health Check</a>
                <a href="/test/full-report" class="btn" target="_blank">📊 Full Report</a>
            </div>

            <h2>📋 Test Data Routes</h2>
            <div class="btn-group">
                <a href="/test/db" class="btn" target="_blank">Test DB</a>
                <a href="/test/config" class="btn" target="_blank">Test Config</a>
                <a href="/test/models" class="btn" target="_blank">Test Models</a>
                <a href="/test/auth" class="btn" target="_blank">👤 Test Auth</a>
                <a href="/test/create-dummy-user" class="btn" target="_blank">➕ Create Dummy User</a>
                <a href="/test/delete-dummy-user" class="btn" target="_blank">🗑 Delete Dummy User</a>
                <a href="/test/onboarding" class="btn" target="_blank">🧠 Onboarding Data</a>
                <a href="/test/simulate-onboarding" class="btn" target="_blank">⚡ Simulate Onboarding</a>
                <a href="/test/reset-onboarding" class="btn" target="_blank">🔄 Reset Onboarding</a>
                <a href="/test/dashboard" class="btn" target="_blank">📊 Dashboard Data</a>
                <a href="/test/add-dummy-messages" class="btn" target="_blank">💬 Add Dummy Messages</a>
                <a href="/test/clear-messages" class="btn" target="_blank">🗑 Clear Messages</a>
                <a href="/test/chatbot" class="btn" target="_blank">🤖 Chatbot Data</a>
                <a href="/test/api-check" class="btn orange" target="_blank">🔌 Check API</a>
                <a href="/test/simulate-chat" class="btn" target="_blank">💬 Simulate Chat</a>
            </div>

            <h2>🔗 Blueprint Routes</h2>
            <div class="btn-group">
                <a href="/login" class="btn" target="_blank">🔐 Login</a>
                <a href="/register" class="btn" target="_blank">📝 Register</a>
                <a href="/profile" class="btn" target="_blank">👤 Profile</a>
                <a href="/onboarding" class="btn" target="_blank">📝 Onboarding Quiz</a>
                <a href="/onboarding/result" class="btn" target="_blank">📊 Onboarding Result</a>
                <a href="/dashboard" class="btn" target="_blank">🏠 Dashboard</a>
                <a href="/dashboard/stats" class="btn" target="_blank">📈 Stats</a>
                <a href="/chat" class="btn" target="_blank">💬 Chat</a>
            </div>

            <h2>⚠️ Error Pages</h2>
            <div class="btn-group">
                <a href="/this-does-not-exist" class="btn red" target="_blank">404 Page</a>
                <a href="/test/trigger-500" class="btn red" target="_blank">500 Page</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


# ─────────────────────────────────────────────────────────────────────────────
# 🎬 DEMO SETUP
# ─────────────────────────────────────────────────────────────────────────────
@test.route('/setup-demo')
def setup_demo():
    try:
        from app.models import User, LearningProfile, ChatMessage
        from app import bcrypt, db

        # Step 1 — Create demo user if not exists
        existing = User.query.filter_by(email='demo@skillpilot.com').first()
        if not existing:
            hashed = bcrypt.generate_password_hash('demo123').decode('utf-8')
            user = User(name='Alex Student', email='demo@skillpilot.com', password=hashed)
            db.session.add(user)
            db.session.commit()
        else:
            user = existing

        # Step 2 — Set learning profile
        if not user.learning_profile:
            profile = LearningProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()

        profile = user.learning_profile
        profile.learning_style  = 'visual'
        profile.learning_pace   = 'medium'
        profile.subject_focus   = 'Computer Science'
        profile.onboarding_done = True
        profile.slow_signals    = 3
        profile.fast_signals    = 7
        db.session.commit()

        # Step 3 — Clear old messages then add 12 realistic ones
        ChatMessage.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        msgs = [
            # Pair 1 — Computer Science
            ('user', "Can you explain what an array is in Python?", 'Computer Science'),
            ('assistant', (
                "Great question! Think of an array like a **row of labeled boxes** 📦\n\n"
                "In Python, we use lists (which work like arrays):\n\n"
                "```python\nmy_list = [1, 2, 3, 4, 5]\n```\n\n"
                "Each box has a position number called an **index**, starting from 0:\n"
                "- my_list[0] → 1 (first box)\n"
                "- my_list[2] → 3 (third box)\n\n"
                "**Visual diagram:**\n"
                "```\nIndex: [0] [1] [2] [3] [4]\nValue:  1   2   3   4   5\n```\n\n"
                "You can add items with `.append()`, remove with `.remove()`, and get the length with `len()`.\n\n"
                "Does this visual make sense so far? What part would you like me to visualize further?"
            ), 'Computer Science'),

            # Pair 2 — Computer Science
            ('user', "got it! what about dictionaries?", 'Computer Science'),
            ('assistant', (
                "Since you picked that up fast, let's go deeper! 🚀\n\n"
                "A **dictionary** is like a real dictionary — you look up a **word** (key) to get its **definition** (value).\n\n"
                "```python\nstudent = {\n    'name': 'Alex',\n    'grade': 'A',\n    'age': 20\n}\n```\n\n"
                "**Visual representation:**\n"
                "```\n'name' → 'Alex'\n'grade' → 'A'\n'age'   → 20\n```\n\n"
                "Key operations:\n"
                "- Access: `student['name']` → 'Alex'\n"
                "- Add: `student['gpa'] = 3.9`\n"
                "- Check key exists: `'name' in student` → True\n\n"
                "Want to explore more advanced dictionary operations? What part would you like me to visualize further?"
            ), 'Computer Science'),

            # Pair 3 — Data Structures
            ('user', "Explain linked lists with a visual example", 'Data Structures'),
            ('assistant', (
                "Perfect topic for a visual learner! 🎨 Imagine a **treasure hunt** where each clue points to the next location.\n\n"
                "**Visual diagram of a linked list:**\n"
                "```\n[Node 1: Data='A' | Next →] → [Node 2: Data='B' | Next →] → [Node 3: Data='C' | Next=None]\n```\n\n"
                "Each **node** has two parts:\n"
                "1. **Data** — the value stored\n"
                "2. **Next pointer** — the arrow pointing to the next node\n\n"
                "In Python:\n"
                "```python\nclass Node:\n    def __init__(self, data):\n        self.data = data\n        self.next = None\n```\n\n"
                "Unlike arrays, linked lists don't need continuous memory — each node can live anywhere!\n\n"
                "What part would you like me to visualize further?"
            ), 'Data Structures'),

            # Pair 4 — Data Structures
            ('user', "i don't understand the pointer part, can you explain again?", 'Data Structures'),
            ('assistant', (
                "No worries! Let me paint a clearer picture 🖼️\n\n"
                "Think of **pointers like arrows** drawn between boxes:\n\n"
                "```\n[Box A] ──arrow──→ [Box B] ──arrow──→ [Box C] ──→ (end)\n```\n\n"
                "Each box **remembers the address** of the next box — that address IS the pointer.\n\n"
                "Real-world analogy: Imagine a linked list as a **relay race** 🏃\n"
                "- Runner 1 passes the baton to Runner 2\n"
                "- Runner 2 passes it to Runner 3\n"
                "- Runner 3 finishes (points to None/null)\n\n"
                "The baton handoff = the pointer. Without it, the chain breaks!\n\n"
                "Does this make sense now? What part would you like me to visualize further?"
            ), 'Data Structures'),

            # Pair 5 — Computer Science
            ('user', "What is recursion? Give me a visual explanation", 'Computer Science'),
            ('assistant', (
                "Recursion is like standing **between two mirrors** 🪞🪞\n\n"
                "You see a reflection of a reflection of a reflection... going deeper each time!\n\n"
                "**In code:**\n"
                "```python\ndef countdown(n):\n    if n == 0:\n        return 'Done!'\n    print(n)\n    return countdown(n-1)  # calls itself!\n```\n\n"
                "**Visual trace for countdown(3):**\n"
                "```\ncountdown(3) → prints 3\n  countdown(2) → prints 2\n    countdown(1) → prints 1\n      countdown(0) → returns 'Done!'\n```\n\n"
                "Two essential parts of every recursive function:\n"
                "1. **Base case** — the stopping condition (n == 0)\n"
                "2. **Recursive case** — calls itself with a smaller problem\n\n"
                "What part would you like me to visualize further?"
            ), 'Computer Science'),

            # Pair 6 — Algorithms
            ('user', "give me a harder problem about sorting algorithms", 'Algorithms'),
            ('assistant', (
                "Challenge accepted! Let's compare **Bubble Sort vs Quick Sort** visually 🏆\n\n"
                "**Bubble Sort — O(n²):**\n"
                "```\n[5, 3, 8, 1] → compare pairs, swap if needed:\nPass 1: [3, 5, 1, 8]  ← 8 bubbled to end\nPass 2: [3, 1, 5, 8]  ← 5 moved right\nPass 3: [1, 3, 5, 8]  ← sorted!\n```\n\n"
                "**Quick Sort — O(n log n) average:**\n"
                "```\n[5, 3, 8, 1]  pivot=5\nLeft:  [3, 1]  (less than 5)\nRight: [8]     (greater than 5)\nResult: [1,3] + [5] + [8] = [1,3,5,8] ✅\n```\n\n"
                "**Your Challenge 🎯:**\n"
                "Implement merge sort and explain:\n"
                "1. Why is merge sort O(n log n) and NOT O(n²)?\n"
                "2. Draw the split-and-merge tree for [4, 2, 7, 1, 3]\n"
                "3. When would you prefer merge sort over quick sort?\n\n"
                "Give it a try and share your answer! What part would you like me to visualize further?"
            ), 'Algorithms'),
        ]

        for role, content, subject in msgs:
            msg = ChatMessage(user_id=user.id, role=role, content=content, subject=subject)
            db.session.add(msg)
        db.session.commit()

        subjects_used = list(set(m[2] for m in msgs))

        return jsonify({
            'status': 'demo ready',
            'login_email': 'demo@skillpilot.com',
            'login_password': 'demo123',
            'profile': {
                'style': 'visual',
                'pace': 'medium',
                'subject': 'Computer Science'
            },
            'messages_added': len(msgs),
            'subjects': subjects_used,
            'instructions': 'Login at /login with demo@skillpilot.com / demo123'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# 🔄 DEMO RESET
# ─────────────────────────────────────────────────────────────────────────────
@test.route('/reset-demo')
def reset_demo():
    try:
        from app.models import User, ChatMessage
        user = User.query.filter_by(email='demo@skillpilot.com').first()
        if not user:
            return jsonify({'status': 'not_found', 'message': 'Demo user does not exist. Run /test/setup-demo first.'})

        deleted = ChatMessage.query.filter_by(user_id=user.id).delete()
        if user.learning_profile:
            user.learning_profile.slow_signals = 0
            user.learning_profile.fast_signals = 0
            user.learning_profile.onboarding_done = False
        db.session.commit()

        return jsonify({
            'status': 'reset complete',
            'messages_deleted': deleted,
            'onboarding_done': False,
            'message': 'Demo account reset. Run /test/setup-demo to repopulate.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# 📊 FULL REPORT
# ─────────────────────────────────────────────────────────────────────────────
@test.route('/full-report')
def full_report():
    try:
        from app.models import User, ChatMessage, LearningProfile
        from flask import current_app
        from config import Config
        from datetime import datetime

        # Users
        users = User.query.all()
        user_report = []
        for u in users:
            p = u.learning_profile
            msgs = ChatMessage.query.filter_by(user_id=u.id).count()
            subjects = db.session.query(ChatMessage.subject).filter_by(user_id=u.id).distinct().all()
            user_report.append({
                'name': u.name,
                'email': u.email,
                'created_at': u.created_at.strftime('%Y-%m-%d') if u.created_at else None,
                'onboarding_done': p.onboarding_done if p else False,
                'learning_style': p.learning_style if p else None,
                'learning_pace': p.learning_pace if p else None,
                'subject_focus': p.subject_focus if p else None,
                'slow_signals': p.slow_signals if p else 0,
                'fast_signals': p.fast_signals if p else 0,
                'total_messages': msgs,
                'subjects_studied': [s[0] for s in subjects]
            })

        # DB table counts
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception:
            db_status = 'error'

        # All registered routes
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
                'path': str(rule)
            })

        # Security headers check
        gemini_key = Config.GEMINI_API_KEY
        security = {
            'X-Content-Type-Options': 'nosniff (active)',
            'X-Frame-Options': 'SAMEORIGIN (active)',
            'X-XSS-Protection': '1; mode=block (active)',
            'Referrer-Policy': 'strict-origin-when-cross-origin (active)',
            'session_httponly': current_app.config.get('SESSION_COOKIE_HTTPONLY', False),
            'session_samesite': current_app.config.get('SESSION_COOKIE_SAMESITE', 'None'),
        }

        return jsonify({
            'report': 'SKILL PILOT Full System Report',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'version': '1.0.0',
            'database': {
                'status': db_status,
                'total_users': User.query.count(),
                'total_messages': ChatMessage.query.count(),
                'total_profiles': LearningProfile.query.count()
            },
            'api': {
                'gemini_configured': bool(gemini_key and gemini_key != 'paste_your_key_here'),
                'model': 'gemini-2.5-flash'
            },
            'security': security,
            'rate_limits': {
                'chat_send': '30 per minute',
                'login_post': '10 per minute',
                'default': '200 per day / 50 per hour'
            },
            'users': user_report,
            'registered_routes': sorted(routes, key=lambda r: r['path'])
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Trigger 500 for testing error page
# ─────────────────────────────────────────────────────────────────────────────
@test.route('/trigger-500')
def trigger_500():
    raise RuntimeError("Intentional 500 — testing error page")


# ─────────────────────────────────────────────────────────────────────────────
# All existing routes below (unchanged)
# ─────────────────────────────────────────────────────────────────────────────
@test.route('/db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        tables = [row[0] for row in result if row[0] != 'sqlite_sequence']
        return jsonify({'status': 'success', 'tables': tables, 'db_path': db.engine.url.database})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/config')
def test_config():
    from flask import current_app
    return jsonify({
        'debug_mode': current_app.config.get('DEBUG'),
        'db_uri': current_app.config.get('SQLALCHEMY_DATABASE_URI'),
        'gemini_api_key_set': bool(current_app.config.get('GEMINI_API_KEY')),
        'secret_key_set': bool(current_app.config.get('SECRET_KEY')),
        'session_httponly': current_app.config.get('SESSION_COOKIE_HTTPONLY'),
        'session_samesite': current_app.config.get('SESSION_COOKIE_SAMESITE'),
    })

@test.route('/models')
def test_models():
    try:
        from app.models import User, LearningProfile, ChatMessage
        return jsonify({
            'status': 'success',
            'models': ['User', 'LearningProfile', 'ChatMessage'],
            'counts': {
                'User': User.query.count(),
                'LearningProfile': LearningProfile.query.count(),
                'ChatMessage': ChatMessage.query.count()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/auth')
def test_auth():
    try:
        from app.models import User
        users = User.query.all()
        user_list = [{'email': u.email, 'onboarding_done': u.learning_profile.onboarding_done if u.learning_profile else False} for u in users]
        return jsonify({'status': 'success', 'total_users': len(users), 'users': user_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/create-dummy-user')
def create_dummy_user():
    try:
        from app.models import User, LearningProfile
        from app import bcrypt, db
        existing = User.query.filter_by(email="test@skillpilot.com").first()
        if existing:
            return jsonify({'status': 'already exists', 'message': 'Dummy user already exists'})
        hashed = bcrypt.generate_password_hash("test123").decode('utf-8')
        user = User(name="Test Student", email="test@skillpilot.com", password=hashed)
        db.session.add(user)
        db.session.commit()
        profile = LearningProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        return jsonify({'status': 'created', 'user_id': user.id, 'email': user.email})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/delete-dummy-user')
def delete_dummy_user():
    try:
        from app.models import User
        user = User.query.filter_by(email="test@skillpilot.com").first()
        if user:
            if user.learning_profile:
                db.session.delete(user.learning_profile)
            db.session.delete(user)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Test user deleted'})
        return jsonify({'status': 'not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/onboarding')
def test_onboarding():
    try:
        from app.models import LearningProfile, User
        users = User.query.all()
        profiles = [{'email': u.email, 'learning_style': u.learning_profile.learning_style if u.learning_profile else None,
                     'learning_pace': u.learning_profile.learning_pace if u.learning_profile else None,
                     'onboarding_done': u.learning_profile.onboarding_done if u.learning_profile else False} for u in users]
        return jsonify({'status': 'success', 'total_profiles': len(profiles), 'profiles': profiles})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/simulate-onboarding')
def simulate_onboarding():
    try:
        from app.models import User
        user = User.query.filter_by(email="test@skillpilot.com").first()
        if not user:
            return jsonify({'status': 'error', 'message': 'Dummy user not found'})
        profile = user.learning_profile
        profile.learning_style = 'visual'
        profile.learning_pace  = 'fast'
        profile.subject_focus  = 'Computer Science'
        profile.onboarding_done = True
        db.session.commit()
        return jsonify({'status': 'success', 'user_email': user.email, 'profile_saved': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/reset-onboarding')
def reset_onboarding():
    try:
        from app.models import User
        user = User.query.filter_by(email="test@skillpilot.com").first()
        if user and user.learning_profile:
            user.learning_profile.onboarding_done = False
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Onboarding reset for test@skillpilot.com'})
        return jsonify({'status': 'not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/dashboard')
def test_dashboard():
    try:
        from app.models import User, ChatMessage
        users = User.query.all()
        user_list = [{'email': u.email,
                      'learning_style': u.learning_profile.learning_style if u.learning_profile else None,
                      'learning_pace': u.learning_profile.learning_pace if u.learning_profile else None,
                      'subject_focus': u.learning_profile.subject_focus if u.learning_profile else None,
                      'onboarding_done': u.learning_profile.onboarding_done if u.learning_profile else False,
                      'total_messages': ChatMessage.query.filter_by(user_id=u.id).count()} for u in users]
        return jsonify({'status': 'success', 'total_users': len(user_list), 'users': user_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/add-dummy-messages')
def add_dummy_messages():
    try:
        from app.models import User, ChatMessage
        user = User.query.filter_by(email="test@skillpilot.com").first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})
        msgs_data = [
            {'role': 'user', 'content': 'What is an array?', 'subject': 'Computer Science'},
            {'role': 'assistant', 'content': 'An array is a data structure...', 'subject': 'Computer Science'},
            {'role': 'user', 'content': 'How do trees work?', 'subject': 'Data Structures'},
            {'role': 'assistant', 'content': 'Trees are hierarchical...', 'subject': 'Data Structures'},
        ]
        for m in msgs_data:
            db.session.add(ChatMessage(user_id=user.id, role=m['role'], content=m['content'], subject=m['subject']))
        db.session.commit()
        return jsonify({'status': 'success', 'messages_added': len(msgs_data)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/clear-messages')
def clear_messages():
    try:
        from app.models import User, ChatMessage
        user = User.query.filter_by(email="test@skillpilot.com").first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})
        deleted_count = ChatMessage.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        return jsonify({'status': 'success', 'deleted_count': deleted_count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/chatbot')
def test_chatbot():
    try:
        from app.models import User, ChatMessage
        users = User.query.all()
        user_list = [{'email': u.email,
                      'learning_style': u.learning_profile.learning_style if u.learning_profile else None,
                      'slow_signals': u.learning_profile.slow_signals if u.learning_profile else 0,
                      'fast_signals': u.learning_profile.fast_signals if u.learning_profile else 0,
                      'total_messages': ChatMessage.query.filter_by(user_id=u.id).count()} for u in users]
        return jsonify({'status': 'success', 'users': user_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@test.route('/api-check')
def test_api_check():
    from config import Config
    key = Config.GEMINI_API_KEY
    if not key or key == 'paste_your_key_here':
        return jsonify({'status': 'error', 'response_received': False, 'message': 'API key not configured'})
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model   = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say exactly: SKILL PILOT Gemini API connected successfully")
        return jsonify({'status': 'connected', 'response_received': True,
                        'response_preview': response.text[:50], 'model_used': 'gemini-2.5-flash'})
    except Exception as e:
        return jsonify({'status': 'error', 'response_received': False, 'message': str(e)}), 500

@test.route('/simulate-chat')
def simulate_chat():
    try:
        from app.models import User, ChatMessage
        from app.routes.chatbot import detect_and_update_pace
        user = User.query.filter_by(email="test@skillpilot.com").first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})
        msgs_data = [
            ('user', 'Explain arrays in Python', 'Computer Science'),
            ('assistant', '[Arrays are like numbered containers...]', 'Computer Science'),
            ('user', "i don't understand, can you explain again", 'Computer Science'),
            ('assistant', '[Sure! Let me break it down more simply...]', 'Computer Science'),
        ]
        for role, content, subject in msgs_data:
            db.session.add(ChatMessage(user_id=user.id, role=role, content=content, subject=subject))
            if role == 'user':
                detect_and_update_pace(content, user.learning_profile)
        db.session.commit()
        return jsonify({'status': 'success', 'messages_added': len(msgs_data),
                        'updated_pace': user.learning_profile.learning_pace})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
