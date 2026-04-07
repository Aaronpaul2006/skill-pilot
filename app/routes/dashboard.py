import random
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import ChatMessage, LearningProfile, StudyPlan, StudySession
from datetime import datetime

dashboard = Blueprint('dashboard', __name__)

QUOTES = [
    ("The expert in anything was once a beginner.", "Helen Hayes"),
    ("Education is the most powerful weapon.", "Nelson Mandela"),
    ("Learning never exhausts the mind.", "Leonardo da Vinci"),
    ("The more that you read, the more things you will know.", "Dr. Seuss"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("Live as if you were to die tomorrow. Learn as if you were to live forever.", "Mahatma Gandhi"),
    ("The beautiful thing about learning is nobody can take it away from you.", "B.B. King"),
    ("Education is not preparation for life; education is life itself.", "John Dewey")
]

STYLE_TIPS = {
    "visual": [
        "Draw mind maps before studying a topic",
        "Use color-coded notes and highlights",
        "Watch video explanations before reading",
        "Create flowcharts for complex processes",
        "Use diagrams to summarize chapters"
    ],
    "auditory": [
        "Record yourself explaining concepts",
        "Join or form study discussion groups",
        "Read notes out loud while studying",
        "Listen to topic-related podcasts",
        "Teach concepts to a friend verbally"
    ],
    "reading": [
        "Write detailed summaries after each topic",
        "Make structured bullet-point notes",
        "Re-read key sections multiple times",
        "Use textbooks and documentation as primary resources",
        "Write practice answers in full sentences"
    ],
    "kinesthetic": [
        "Build mini projects to apply every concept",
        "Solve as many practice problems as possible",
        "Use lab time and hands-on experiments",
        "Break problems into small actionable steps",
        "Create prototypes or demos to test understanding"
    ]
}

PACE_ADVICE = {
    "slow": {
        "title": "Thorough Learner",
        "advice": "Take your time. Ask the AI to explain step by step with multiple examples. Never skip foundational concepts.",
        "chat_tip": "Try prompts like: 'Explain this very simply' or 'Give me 3 examples'"
    },
    "medium": {
        "title": "Balanced Learner", 
        "advice": "You balance depth and speed well. Mix conceptual understanding with practice problems.",
        "chat_tip": "Try prompts like: 'Explain then give me a practice problem'"
    },
    "fast": {
        "title": "Quick Learner",
        "advice": "You grasp concepts fast. Challenge yourself with harder problems and deeper topics.",
        "chat_tip": "Try prompts like: 'Give me an advanced problem' or 'What are edge cases?'"
    }
}

SUBJECT_TOPICS = {
    "General": ["Study Skills", "Time Management", "Critical Thinking", "Research Methods", "Exam Strategies"],
    "Mathematics": ["Calculus", "Linear Algebra", "Probability", "Differential Equations", "Number Theory"],
    "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Physics", "Optics"],
    "Chemistry": ["Organic Chemistry", "Thermochemistry", "Chemical Bonding", "Electrochemistry", "Kinetics"],
    "Computer Science": ["Data Structures", "Algorithms", "OOP", "Database Systems", "Operating Systems"],
    "Data Science": ["Statistics", "Machine Learning", "Data Visualization", "Python for Data", "SQL"],
    "Electronics": ["Circuit Theory", "Digital Electronics", "Microcontrollers", "Signal Processing", "VLSI"],
    "Civil Engineering": ["Structural Analysis", "Fluid Mechanics", "Surveying", "Concrete Design", "Geotechnics"],
    "Mechanical Engineering": ["Thermodynamics", "Fluid Mechanics", "Machine Design", "Manufacturing", "CAD"],
    "Biology": ["Cell Biology", "Genetics", "Ecology", "Human Physiology", "Biochemistry"]
}

@dashboard.route('/dashboard')
@login_required
def index():
    if not current_user.learning_profile or not current_user.learning_profile.onboarding_done:
        flash("Please complete your learning profile first.", "error")
        return redirect(url_for('onboarding.quiz'))
        
    profile = current_user.learning_profile
    recent_messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.desc()).limit(5).all()
    total_messages = ChatMessage.query.filter_by(user_id=current_user.id).count()
    subjects_studied = db.session.query(ChatMessage.subject).filter_by(user_id=current_user.id).distinct().count()
    
    style_tips = STYLE_TIPS.get(profile.learning_style, [])
    pace_info = PACE_ADVICE.get(profile.learning_pace, {})
    recommended_topics = SUBJECT_TOPICS.get(profile.subject_focus, [])
    
    active_plans_count = StudyPlan.query.filter_by(user_id=current_user.id).count()
    today = datetime.now().date()
    todays_sessions = StudySession.query.join(StudyPlan).filter(
        StudyPlan.user_id == current_user.id,
        StudySession.session_date == today,
        StudySession.is_completed == False
    ).all()

    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
        
    quote, quote_author = random.choice(QUOTES)

    return render_template(
        'dashboard/index.html',
        profile=profile,
        recent_messages=recent_messages,
        total_messages=total_messages,
        subjects_studied=subjects_studied,
        style_tips=style_tips,
        pace_info=pace_info,
        recommended_topics=recommended_topics,
        greeting=greeting,
        quote=quote,
        quote_author=quote_author,
        active_plans_count=active_plans_count,
        todays_sessions=todays_sessions
    )

@dashboard.route('/dashboard/profile-edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    profile = current_user.learning_profile
    if request.method == 'POST':
        subject_focus = request.form.get('subject_focus')
        if subject_focus:
            profile.subject_focus = subject_focus
            db.session.commit()
            flash(f"Subject focus updated to {subject_focus}!", "success")
            return redirect(url_for('dashboard.index'))
            
    return render_template('dashboard/profile_edit.html', profile=profile, subject_options=list(SUBJECT_TOPICS.keys()))

@dashboard.route('/dashboard/stats')
@login_required
def stats():
    total_messages = ChatMessage.query.filter_by(user_id=current_user.id).count()
    messages_by_subject = db.session.query(ChatMessage.subject, db.func.count(ChatMessage.id)).filter_by(user_id=current_user.id).group_by(ChatMessage.subject).all()
    recent_5 = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.desc()).limit(5).all()
    return render_template('dashboard/stats.html', total_messages=total_messages, messages_by_subject=messages_by_subject, recent_5=recent_5)
