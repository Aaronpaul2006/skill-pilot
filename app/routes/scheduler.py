import json
import html
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
import google.generativeai as genai

from app import db, limiter
from app.models import StudyPlan, StudySession, PlayerProfile
from app.services.gamification import GamificationService as GS

scheduler = Blueprint('scheduler', __name__, url_prefix='/scheduler')

def parse_json_safely(text):
    """Safely extracts JSON from Gemini output, stripping markdown formatting."""
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse study plan JSON: {str(e)}")

def generate_study_plan(exam_name, exam_date, topics_with_priorities, learning_style, learning_pace, is_cram_mode, catchup_mode=False, prev_sessions=None):
    """Calls Gemini to generate a JSON study plan."""
    days_remaining = (exam_date - date.today()).days
    if days_remaining <= 0:
        raise ValueError("Exam date must be in the future.")
        
    prompt = f"""You are an expert AI tutor. Please create a daily study schedule for a student.
Exam Name: {exam_name}
Days Remaining: {days_remaining}
Learning Style: {learning_style}
Learning Pace: {learning_pace}
Cram Mode: {is_cram_mode}
Topics and Priorities: {json.dumps(topics_with_priorities)}
"""
    if catchup_mode and prev_sessions:
        prompt += f"\nThe student is behind schedule. Please re-balance the remaining days to cover these missed topics: {json.dumps(prev_sessions)}\n"
        
    prompt += """
Requirement: Output MUST be strictly valid JSON without explanation or markdown formatting. 
Output format:
{
  "overview": "brief motivational overview string",
  "daily_sessions": [
    {
      "date": "YYYY-MM-DD",
      "sessions": [
        {"topic": "Topic Name", "duration_hours": 2.0, "session_type": "learn|review|practice", "tips": "brief tip"}
      ],
      "total_hours": 3.0,
      "daily_goal": "what to achieve today"
    }
  ],
  "warnings": ["any scheduling warnings"],
  "estimated_readiness": "percentage string like 85%"
}
Make sure dates start from tomorrow (or today if cramming/behind schedule) and end by the exam date. 
If cram mode is True, compress the plan and focus only on high-priority topics.
"""
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'paste_your_key_here':
        raise ValueError("GEMINI_API_KEY is not configured.")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = model.generate_content(prompt)
        return parse_json_safely(response.text)
    except Exception as e:
        current_app.logger.error(f"Gemini API Error: {str(e)}")
        raise ValueError("AI failed to generate a valid study plan. Please try again.")

@scheduler.route('/')
@login_required
def dashboard():
    """Main scheduler dashboard page"""
    plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.exam_date.asc()).all()
    plan_data = []
    for plan in plans:
        total = len(plan.sessions)
        completed = sum(1 for s in plan.sessions if s.is_completed)
        progress = int((completed / total * 100)) if total > 0 else 0
        days_rem = (plan.exam_date - date.today()).days
        plan_data.append({
            'plan': plan,
            'progress': progress,
            'days_remaining': max(0, days_rem)
        })
    return render_template('scheduler/dashboard.html', active_plans=plan_data)

@scheduler.route('/create', methods=['POST'])
@login_required
@limiter.limit("5/hour")
def create_plan():
    """Creates a new study plan"""
    try:
        exam_name = html.escape(request.form.get('exam_name', '').strip())
        exam_date_str = request.form.get('exam_date')
        if not exam_name or not exam_date_str:
            flash("Exam name and date are required.", "error")
            return redirect(url_for('scheduler.dashboard'))
            
        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
        days_remaining = (exam_date - date.today()).days
        
        if days_remaining <= 0:
            flash("Exam date must be at least 1 day in the future.", "error")
            return redirect(url_for('scheduler.dashboard'))
            
        topics = request.form.getlist('topics[]')
        priorities = request.form.getlist('priorities[]')
        
        if not topics or not priorities or len(topics) != len(priorities):
            flash("At least one valid topic must be provided.", "error")
            return redirect(url_for('scheduler.dashboard'))
            
        if len(topics) > 15:
            flash("Maximum of 15 topics allowed.", "error")
            return redirect(url_for('scheduler.dashboard'))
            
        topics_with_priorities = []
        for t, p in zip(topics, priorities):
            clean_t = html.escape(t.strip())
            clean_p = html.escape(p.strip())
            if clean_t:
                topics_with_priorities.append({'topic': clean_t, 'priority': clean_p})
                
        if not topics_with_priorities:
            flash("Valid topics are required.", "error")
            return redirect(url_for('scheduler.dashboard'))
            
        is_cram_mode = request.form.get('is_cram_mode') == 'on'
        
        if days_remaining < 3:
            is_cram_mode = True
            flash("Exam is very soon. Cram mode automatically enabled.", "warning")
            
        profile = current_user.learning_profile
        learning_style = profile.learning_style if profile else 'reading'
        learning_pace = profile.learning_pace if profile else 'medium'
        
        plan_json = generate_study_plan(
            exam_name, exam_date, topics_with_priorities, 
            learning_style, learning_pace, is_cram_mode
        )
        
        new_plan = StudyPlan(
            user_id=current_user.id,
            exam_name=exam_name,
            exam_date=exam_date,
            subjects_json=json.dumps(topics_with_priorities),
            generated_plan_json=json.dumps(plan_json),
            is_cram_mode=is_cram_mode
        )
        db.session.add(new_plan)
        db.session.commit()
        
        for day in plan_json.get('daily_sessions', []):
            try:
                s_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            except ValueError:
                continue
            for s in day.get('sessions', []):
                new_session = StudySession(
                    plan_id=new_plan.id,
                    session_date=s_date,
                    topic=html.escape(s.get('topic', 'Study Session')),
                    duration_hours=float(s.get('duration_hours', 1.0))
                )
                db.session.add(new_session)
                
        db.session.commit()
        flash("Study plan created successfully!", "success")
        return redirect(url_for('scheduler.plan_detail', plan_id=new_plan.id))
        
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('scheduler.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Plan creation error: {str(e)}")
        flash("An error occurred while creating the plan.", "error")
        return redirect(url_for('scheduler.dashboard'))

@scheduler.route('/<int:plan_id>')
@login_required
def plan_detail(plan_id):
    """View details of a study plan"""
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    plan_data = json.loads(plan.generated_plan_json)
    
    today = date.today()
    missed_count = StudySession.query.filter(
        StudySession.plan_id == plan.id,
        StudySession.is_completed == False,
        StudySession.session_date < today
    ).count()
    
    sessions = StudySession.query.filter_by(plan_id=plan.id).order_by(StudySession.session_date.asc()).all()
    
    days_dict = {}
    for session in sessions:
        ds = session.session_date.strftime('%Y-%m-%d')
        if ds not in days_dict:
            days_dict[ds] = {'date': ds, 'sessions': [], 'date_obj': session.session_date}
        days_dict[ds]['sessions'].append(session)
        
    days_list = [days_dict[k] for k in sorted(days_dict.keys())]
    
    days_remaining = max(0, (plan.exam_date - today).days)
    
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.is_completed)
    progress = int((completed_sessions / total_sessions * 100)) if total_sessions > 0 else 0
    
    return render_template('scheduler/plan_detail.html', 
                            plan=plan, 
                            plan_data=plan_data, 
                            days_list=days_list, 
                            missed_count=missed_count,
                            days_remaining=days_remaining,
                            progress=progress,
                            today_str=today.strftime('%Y-%m-%d'))

@scheduler.route('/<int:plan_id>/complete-session', methods=['POST'])
@login_required
def complete_session(plan_id):
    """Mark a specific session as completed via JSON API"""
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    session_id = data.get('session_id')
    
    session = StudySession.query.filter_by(id=session_id, plan_id=plan.id).first()
    if session:
        session.is_completed = True
        session.completed_at = datetime.utcnow()
        player = PlayerProfile.query.filter_by(user_id=current_user.id).first()
        if player:
            player.total_sessions_completed += 1
            db.session.commit()
            
        xp_result = GS.award_xp(current_user.id, "session_complete", 25, f"Completed {session.topic} session")
        streak_result = GS.update_streak(current_user.id)
        
        player_now = PlayerProfile.query.filter_by(user_id=current_user.id).first()
        sess_count = player_now.total_sessions_completed if player_now else 0
        new_badges = GS.check_and_award_badges(current_user.id, "session_complete", {
            "session_count": sess_count,
            "subject": session.topic
        })
        completed_challenges = GS.update_challenge_progress(current_user.id, "sessions_complete")
        
        return jsonify({
            'success': True, 
            'message': 'Session complete',
            'gamification': {
                'xp_awarded': xp_result["xp_awarded"] if xp_result else 25,
                'leveled_up': xp_result["leveled_up"] if xp_result else False,
                'new_level': xp_result.get("new_level") if xp_result else 1,
                'new_rank': xp_result.get("new_rank") if xp_result else "",
                'new_badges': new_badges,
                'completed_challenges': completed_challenges,
                'streak': streak_result['streak_current'] if streak_result else 1
            }
        })
    return jsonify({'success': False, 'message': 'Session not found'}), 404

@scheduler.route('/<int:plan_id>/progress')
@login_required
def plan_progress(plan_id):
    """Return JSON stats for progress tab"""
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    sessions = StudySession.query.filter_by(plan_id=plan.id).order_by(StudySession.session_date.asc()).all()
    
    history = {}
    topic_coverage = {}
    for s in sessions:
        ds = s.session_date.strftime('%b %d')
        if ds not in history:
            history[ds] = 0
            
        t = s.topic
        if t not in topic_coverage:
            topic_coverage[t] = {'total': 0, 'completed': 0}
        
        topic_coverage[t]['total'] += s.duration_hours
        
        if s.is_completed:
            history[ds] += s.duration_hours
            topic_coverage[t]['completed'] += s.duration_hours
            
    return jsonify({
        'dates': list(history.keys()), 
        'hours': list(history.values()),
        'topics': topic_coverage
    })

@scheduler.route('/<int:plan_id>/regenerate', methods=['POST'])
@login_required
@limiter.limit("5/hour")
def regenerate_plan(plan_id):
    """Regenerates the complete plan if behind schedule"""
    try:
        plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
        today = date.today()
        
        missed_sessions = StudySession.query.filter(
            StudySession.plan_id == plan.id,
            StudySession.is_completed == False,
            StudySession.session_date < today
        ).all()
        
        if not missed_sessions:
            flash("You are not behind schedule.", "info")
            return redirect(url_for('scheduler.plan_detail', plan_id=plan.id))
            
        topics_with_priorities = json.loads(plan.subjects_json)
        profile = current_user.learning_profile
        learning_style = profile.learning_style if profile else 'reading'
        learning_pace = profile.learning_pace if profile else 'medium'
        
        missed_topics = [s.topic for s in missed_sessions]
        
        plan_json = generate_study_plan(
            plan.exam_name, plan.exam_date, topics_with_priorities, 
            learning_style, learning_pace, plan.is_cram_mode, 
            catchup_mode=True, prev_sessions=missed_topics
        )
        plan.generated_plan_json = json.dumps(plan_json)
        
        uncompleted_sessions = StudySession.query.filter_by(plan_id=plan.id, is_completed=False).all()
        for session in uncompleted_sessions:
            db.session.delete(session)
        db.session.commit()
        
        for day in plan_json.get('daily_sessions', []):
            try:
                s_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
            except ValueError:
                continue
            if s_date < today:
                s_date = today
            for s in day.get('sessions', []):
                new_session = StudySession(
                    plan_id=plan.id,
                    session_date=s_date,
                    topic=s.get('topic', 'Study Session'),
                    duration_hours=float(s.get('duration_hours', 1.0))
                )
                db.session.add(new_session)
                
        db.session.commit()
        flash("Study plan regenerated!", "success")
        
    except ValueError as ve:
        flash(str(ve), "error")
    except Exception as e:
        current_app.logger.error(f"Regen error: {str(e)}")
        flash("Error regenerating the plan.", "error")
        
    return redirect(url_for('scheduler.plan_detail', plan_id=plan_id))

@scheduler.route('/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_plan(plan_id):
    """Deletes a study plan"""
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})
