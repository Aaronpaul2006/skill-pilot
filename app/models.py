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
    study_plans = db.relationship('StudyPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    earned_badges = db.relationship('UserBadge', backref='user', lazy=True, cascade='all, delete-orphan')
    xp_events = db.relationship('XPEvent', backref='user', lazy=True, cascade='all, delete-orphan')
    challenges = db.relationship('UserChallenge', backref='user', lazy=True, cascade='all, delete-orphan')

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

class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_name = db.Column(db.String(255), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    subjects_json = db.Column(db.Text, nullable=False)
    generated_plan_json = db.Column(db.Text, nullable=False)
    is_cram_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = db.relationship('StudySession', backref='plan', lazy=True, cascade='all, delete-orphan')

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    duration_hours = db.Column(db.Float, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

class PlayerProfile(db.Model):
    __tablename__ = 'player_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    xp_total = db.Column(db.Integer, default=0)
    xp_current_level = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_current = db.Column(db.Integer, default=0)
    streak_longest = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    total_sessions_completed = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    total_chat_messages = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon_emoji = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    xp_reward = db.Column(db.Integer, nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    
    earned_by = db.relationship('UserBadge', backref='badge', lazy=True, cascade='all, delete-orphan')

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='_user_badge_uc'),)

class XPEvent(db.Model):
    __tablename__ = 'xp_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    xp_amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Challenge(db.Model):
    __tablename__ = 'challenges'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    challenge_type = db.Column(db.String(20), nullable=False) # daily, weekly
    goal_type = db.Column(db.String(50), nullable=False)
    goal_count = db.Column(db.Integer, nullable=False)
    xp_reward = db.Column(db.Integer, nullable=False)
    badge_slug = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    user_challenges = db.relationship('UserChallenge', backref='challenge_ref', lazy=True, cascade='all, delete-orphan')

class UserChallenge(db.Model):
    __tablename__ = 'user_challenges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    goal = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    assigned_date = db.Column(db.Date, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
