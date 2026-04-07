from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db, limiter
from app.models import Badge, UserBadge, XPEvent, UserChallenge, Challenge
from app.services.gamification import GamificationService

gamification = Blueprint('gamification', __name__, url_prefix='/gamification')

@gamification.route('/')
@login_required
def hub():
    """Main gamification hub page."""
    stats = GamificationService.get_player_stats(current_user.id)
    leaderboard = GamificationService.get_leaderboard(period="weekly", limit=10)
    
    # Check if user in leaderboard
    user_in_top = any(r['user_id'] == current_user.id for r in leaderboard)
    # Get active challenges
    now = datetime.utcnow()
    active_challenges = UserChallenge.query.join(Challenge).filter(
        UserChallenge.user_id == current_user.id,
        UserChallenge.expires_at > now
    ).all()
    
    xp_events = XPEvent.query.filter_by(user_id=current_user.id).order_by(XPEvent.created_at.desc()).limit(10).all()
    
    return render_template('gamification/hub.html', stats=stats, leaderboard=leaderboard, 
                           user_in_top=user_in_top, active_challenges=active_challenges, xp_events=xp_events)

@gamification.route('/leaderboard')
@login_required
def leaderboard_view():
    """Detailed leaderboard page."""
    weekly = GamificationService.get_leaderboard(period="weekly", limit=50)
    alltime = GamificationService.get_leaderboard(period="alltime", limit=50)
    return render_template('gamification/leaderboard.html', weekly=weekly, alltime=alltime)

@gamification.route('/badges')
@login_required
def badges():
    """Badge collection page."""
    all_badges = Badge.query.all()
    earned_ids = {ub.badge_id: ub.earned_at for ub in UserBadge.query.filter_by(user_id=current_user.id).all()}
    
    badges_data = []
    for b in all_badges:
        bd = {
            "id": b.id,
            "slug": b.slug,
            "name": b.name,
            "description": b.description,
            "emoji": b.icon_emoji,
            "category": b.category,
            "rarity": b.rarity,
            "xp_reward": b.xp_reward,
            "earned": b.id in earned_ids,
            "earned_at": earned_ids.get(b.id)
        }
        badges_data.append(bd)
        
    earned_count = len(earned_ids)
    total_count = len(all_badges)
    
    return render_template('gamification/badges.html', badges=badges_data, earned=earned_count, total=total_count)

@gamification.route('/api/stats')
@login_required
@limiter.limit("60/minute")
def api_stats():
    """JSON stats for dashboard widget."""
    return jsonify(GamificationService.get_player_stats(current_user.id))

@gamification.route('/api/xp-log')
@login_required
@limiter.limit("60/minute")
def api_xp_log():
    """JSON XP log."""
    events = XPEvent.query.filter_by(user_id=current_user.id).order_by(XPEvent.created_at.desc()).limit(20).all()
    return jsonify([{
        "type": e.event_type,
        "xp": e.xp_amount,
        "description": e.description,
        "time": e.created_at.strftime('%Y-%m-%dT%H:%M:%S')
    } for e in events])
