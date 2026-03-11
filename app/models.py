from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    learning_profile = db.relationship('LearningProfile', backref='user', uselist=False, lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)

class LearningProfile(db.Model):
    __tablename__ = 'learning_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_style = db.Column(db.String(20), default='reading')
    learning_pace = db.Column(db.String(10), default='medium')
    subject_focus = db.Column(db.String(100), default='General')
    slow_signals = db.Column(db.Integer, default=0)
    fast_signals = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float, default=0.0)
    onboarding_done = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), default='General')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'subject': self.subject,
            'timestamp': self.timestamp.strftime('%H:%M') if self.timestamp else ''
        }
