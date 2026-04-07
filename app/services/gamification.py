import json
import random
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app import db
from app.models import User, PlayerProfile, Badge, UserBadge, XPEvent, Challenge, UserChallenge

# Static seed data
ANCHOR_LEVELS = {
    1: {"xp": 0, "rank": "Curious Learner"},
    2: {"xp": 100, "rank": "Eager Student"},
    3: {"xp": 250, "rank": "Knowledge Seeker"},
    5: {"xp": 600, "rank": "Dedicated Scholar"},
    10: {"xp": 2000, "rank": "Academic Warrior"},
    15: {"xp": 4000, "rank": "Knowledge Knight"},
    20: {"xp": 7000, "rank": "Wisdom Keeper"},
    25: {"xp": 11000, "rank": "Grand Scholar"},
    30: {"xp": 16000, "rank": "Enlightened Mind"},
    40: {"xp": 28000, "rank": "Academic Sage"},
    50: {"xp": 45000, "rank": "SKILL PILOT Legend"}
}

LEVEL_THRESHOLDS = {}
def _build_levels():
    anchors = sorted(ANCHOR_LEVELS.keys())
    for i in range(len(anchors) - 1):
        start_lvl = anchors[i]
        end_lvl = anchors[i+1]
        start_xp = ANCHOR_LEVELS[start_lvl]["xp"]
        end_xp = ANCHOR_LEVELS[end_lvl]["xp"]
        rank = ANCHOR_LEVELS[start_lvl]["rank"]
        
        diff_xp = int(end_xp) - int(start_xp)
        diff_lvl = int(end_lvl) - int(start_lvl)
        step = diff_xp / diff_lvl
        
        for curr in range(int(start_lvl), int(end_lvl)):
            LEVEL_THRESHOLDS[curr] = {
                "xp": int(int(start_xp) + step * (curr - int(start_lvl))),
                "rank": rank
            }
    LEVEL_THRESHOLDS[50] = ANCHOR_LEVELS[50]
_build_levels()

def seed_badges():
    """Seeds static badges into the database securely."""
    badges_data = [
        {"slug": "first_login", "name": "First Steps", "description": "Complete your first login", "icon_emoji": "🌟", "category": "achievement", "xp_reward": 10, "rarity": "common"},
        {"slug": "first_chat", "name": "Conversation Starter", "description": "Send your first message", "icon_emoji": "💬", "category": "achievement", "xp_reward": 10, "rarity": "common"},
        {"slug": "first_session", "name": "Study Starter", "description": "Complete your first study session", "icon_emoji": "📚", "category": "achievement", "xp_reward": 15, "rarity": "common"},
        {"slug": "messages_50", "name": "Chatterbox", "description": "Send 50 chat messages", "icon_emoji": "🗣️", "category": "achievement", "xp_reward": 30, "rarity": "rare"},
        {"slug": "messages_100", "name": "100 Questions", "description": "Answer 100 questions", "icon_emoji": "📢", "category": "achievement", "xp_reward": 50, "rarity": "rare"},
        {"slug": "messages_500", "name": "Debate Champion", "description": "Send 500 messages", "icon_emoji": "🎤", "category": "achievement", "xp_reward": 75, "rarity": "epic"},
        {"slug": "sessions_10", "name": "Consistent Learner", "description": "Complete 10 study sessions", "icon_emoji": "🏅", "category": "achievement", "xp_reward": 40, "rarity": "rare"},
        {"slug": "sessions_50", "name": "Session Veteran", "description": "Complete 50 study sessions", "icon_emoji": "🎖️", "category": "achievement", "xp_reward": 100, "rarity": "epic"},
        {"slug": "level_10", "name": "Level 10 Warrior", "description": "Reach Level 10", "icon_emoji": "⚔️", "category": "achievement", "xp_reward": 50, "rarity": "rare"},
        {"slug": "level_25", "name": "Grand Scholar", "description": "Reach Level 25", "icon_emoji": "🔮", "category": "achievement", "xp_reward": 100, "rarity": "epic"},
        {"slug": "level_50", "name": "SKILL PILOT Legend", "description": "Reach Level 50", "icon_emoji": "👑", "category": "achievement", "xp_reward": 200, "rarity": "legendary"},
        {"slug": "streak_3", "name": "On Fire", "description": "3-day study streak", "icon_emoji": "🔥", "category": "streak", "xp_reward": 20, "rarity": "common"},
        {"slug": "streak_7", "name": "Week Warrior", "description": "7-day study streak", "icon_emoji": "🔥🔥", "category": "streak", "xp_reward": 50, "rarity": "rare"},
        {"slug": "streak_30", "name": "Monthly Master", "description": "30-day study streak", "icon_emoji": "💎", "category": "streak", "xp_reward": 200, "rarity": "legendary"},
        {"slug": "subject_python", "name": "Python Master", "description": "Study Python 20+ sessions", "icon_emoji": "🐍", "category": "mastery", "xp_reward": 75, "rarity": "epic"},
        {"slug": "subject_maths", "name": "Math Wizard", "description": "Study Maths 20+ sessions", "icon_emoji": "➗", "category": "mastery", "xp_reward": 75, "rarity": "epic"},
        {"slug": "subject_dsa", "name": "DSA Expert", "description": "Study DSA 20+ sessions", "icon_emoji": "🌳", "category": "mastery", "xp_reward": 75, "rarity": "epic"},
        {"slug": "speed_demon", "name": "Speed Demon", "description": "Send 10 messages in under 5 min", "icon_emoji": "⚡", "category": "speed", "xp_reward": 40, "rarity": "rare"},
        {"slug": "quick_learner", "name": "Quick Learner", "description": "Complete 3 sessions in one day", "icon_emoji": "🚀", "category": "speed", "xp_reward": 40, "rarity": "rare"},
        {"slug": "leaderboard_top10", "name": "Top 10 This Week", "description": "Enter weekly top 10 leaderboard", "icon_emoji": "🏆", "category": "social", "xp_reward": 50, "rarity": "rare"},
        {"slug": "leaderboard_top3", "name": "Podium Finish", "description": "Reach top 3 on weekly leaderboard", "icon_emoji": "🥇", "category": "social", "xp_reward": 150, "rarity": "legendary"}
    ]
    
    for b in badges_data:
        existing = Badge.query.filter_by(slug=b['slug']).first()
        if existing:
            existing.name = b['name']
            existing.description = b['description']
            existing.icon_emoji = b['icon_emoji']
            existing.category = b['category']
            existing.xp_reward = b['xp_reward']
            existing.rarity = b['rarity']
        else:
            db.session.add(Badge(**b))
    db.session.commit()

def seed_challenges():
    """Seeds daily/weekly challenges."""
    challenges_data = [
        {"title": "Quick Learner", "description": "Send 5 chat messages today", "challenge_type": "daily", "goal_type": "chat_messages", "goal_count": 5, "xp_reward": 40},
        {"title": "Study Sprint", "description": "Complete 1 study session today", "challenge_type": "daily", "goal_type": "sessions_complete", "goal_count": 1, "xp_reward": 40},
        {"title": "Deep Diver", "description": "Send 15 messages in one day", "challenge_type": "daily", "goal_type": "chat_messages", "goal_count": 15, "xp_reward": 60},
        {"title": "Session Pro", "description": "Complete 2 sessions today", "challenge_type": "daily", "goal_type": "sessions_complete", "goal_count": 2, "xp_reward": 70},
        {"title": "XP Grinder", "description": "Earn 100 XP today", "challenge_type": "daily", "goal_type": "xp_earned", "goal_count": 100, "xp_reward": 40},
        {"title": "Keep It Going", "description": "Maintain your streak", "challenge_type": "daily", "goal_type": "streak_days", "goal_count": 1, "xp_reward": 30},
        {"title": "Week Warrior", "description": "Send 50 messages this week", "challenge_type": "weekly", "goal_type": "chat_messages", "goal_count": 50, "xp_reward": 150},
        {"title": "Session Champion", "description": "Complete 7 sessions this week", "challenge_type": "weekly", "goal_type": "sessions_complete", "goal_count": 7, "xp_reward": 150},
        {"title": "Badge Hunter", "description": "Earn 3 badges this week", "challenge_type": "weekly", "goal_type": "badges_earned", "goal_count": 3, "xp_reward": 120},
        {"title": "XP Collector", "description": "Earn 500 XP this week", "challenge_type": "weekly", "goal_type": "xp_earned", "goal_count": 500, "xp_reward": 150}
    ]
    for c in challenges_data:
        existing = Challenge.query.filter_by(title=c['title']).first()
        if not existing:
            db.session.add(Challenge(**c))
    db.session.commit()

class GamificationService:
    @staticmethod
    def award_xp(user_id, event_type, xp_amount, description, metadata=None):
        """Awards XP, saves event, triggers level up check."""
        player = PlayerProfile.query.filter_by(user_id=user_id).first()
        if not player:
            return None
            
        event = XPEvent(
            user_id=user_id,
            event_type=event_type,
            xp_amount=xp_amount,
            description=description,
            metadata_json=json.dumps(metadata) if metadata else None
        )
        db.session.add(event)
        
        player.xp_total += xp_amount
        player.xp_current_level += xp_amount
        
        levelup_res = GamificationService.check_level_up(player)
        db.session.commit()
        
        GamificationService.update_challenge_progress(user_id, "xp_earned", xp_amount)
        
        return {
            "xp_awarded": xp_amount,
            "new_total": player.xp_total,
            "leveled_up": levelup_res["leveled_up"],
            "new_level": player.level,
            "new_rank": LEVEL_THRESHOLDS.get(player.level, {}).get("rank", "Scholar")
        }

    @staticmethod
    def check_level_up(player):
        """Checks if player crossed level threshold."""
        leveled_up = False
        initial_level = player.level
        
        while player.level < 50:
            next_level = player.level + 1
            next_threshold = LEVEL_THRESHOLDS.get(next_level, {}).get("xp", 999999)
            current_level_base_xp = LEVEL_THRESHOLDS.get(player.level, {}).get("xp", 0)
            
            if player.xp_total >= next_threshold:
                player.level = next_level
                player.xp_current_level = player.xp_total - next_threshold
                leveled_up = True
            else:
                player.xp_current_level = player.xp_total - current_level_base_xp
                break
                
        if leveled_up:
            if player.level >= 10:
                GamificationService.award_badge(player.user_id, "level_10")
            if player.level >= 25:
                GamificationService.award_badge(player.user_id, "level_25")
            if player.level >= 50:
                GamificationService.award_badge(player.user_id, "level_50")
                
        return {"leveled_up": leveled_up, "levels_gained": player.level - initial_level}

    @staticmethod
    def update_streak(user_id):
        """Calculates and updates daily streak."""
        player = PlayerProfile.query.filter_by(user_id=user_id).first()
        if not player:
            return None
            
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        milestone_hit = False
        if not player.last_activity_date:
            player.streak_current = 1
            player.last_activity_date = today
        elif player.last_activity_date == yesterday:
            player.streak_current += 1
            player.last_activity_date = today
            GamificationService.update_challenge_progress(user_id, "streak_days", 1)
        elif player.last_activity_date < yesterday:
            player.streak_current = 1
            player.last_activity_date = today
            
        if player.streak_current > player.streak_longest:
            player.streak_longest = player.streak_current
            
        if player.last_activity_date == today:
            # Check milestone badges
            badges_to_check = {3: "streak_3", 7: "streak_7", 30: "streak_30"}
            for days, slug in badges_to_check.items():
                if player.streak_current >= days:
                    res = GamificationService.award_badge(user_id, slug)
                    if res: milestone_hit = True
                    
        db.session.commit()
        return {"streak_current": player.streak_current, "streak_longest": player.streak_longest, "milestone_hit": milestone_hit}

    @staticmethod
    def award_badge(user_id, badge_slug):
        """Awards a specific badge to a user if not already earned."""
        badge = Badge.query.filter_by(slug=badge_slug).first()
        if not badge:
            return None
            
        existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
        if existing:
            return None
            
        user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
        db.session.add(user_badge)
        
        XPEvent(
            user_id=user_id,
            event_type="badge_earned",
            xp_amount=badge.xp_reward,
            description=f"Earned badge: {badge.name}"
        )
        player = PlayerProfile.query.filter_by(user_id=user_id).first()
        player.xp_total += badge.xp_reward
        GamificationService.check_level_up(player)
        
        GamificationService.update_challenge_progress(user_id, "badges_earned", 1)
        
        return {
            "name": badge.name,
            "emoji": badge.icon_emoji,
            "xp_awarded": badge.xp_reward,
            "rarity": badge.rarity
        }

    @staticmethod
    def check_and_award_badges(user_id, event_type, context=None):
        """Evaluates thresholds for action-based badges."""
        if not context: context = {}
        awarded = []
        
        if event_type == "chat_message":
            msgs = context.get("message_count", 0)
            if msgs == 1: awarded.append(GamificationService.award_badge(user_id, "first_chat"))
            if msgs >= 50: awarded.append(GamificationService.award_badge(user_id, "messages_50"))
            if msgs >= 100: awarded.append(GamificationService.award_badge(user_id, "messages_100"))
            if msgs >= 500: awarded.append(GamificationService.award_badge(user_id, "messages_500"))
            
        elif event_type == "session_complete":
            sess = context.get("session_count", 0)
            subj = str(context.get("subject", "")).lower()
            if sess == 1: awarded.append(GamificationService.award_badge(user_id, "first_session"))
            if sess >= 10: awarded.append(GamificationService.award_badge(user_id, "sessions_10"))
            if sess >= 50: awarded.append(GamificationService.award_badge(user_id, "sessions_50"))
            
            if "python" in subj: awarded.append(GamificationService.award_badge(user_id, "subject_python"))
            elif "math" in subj: awarded.append(GamificationService.award_badge(user_id, "subject_maths"))
            elif "data structure" in subj or "dsa" in subj: awarded.append(GamificationService.award_badge(user_id, "subject_dsa"))
            
        elif event_type == "daily_login":
            awarded.append(GamificationService.award_badge(user_id, "first_login"))
            
        db.session.commit()
        return [b for b in awarded if b is not None]

    @staticmethod
    def get_leaderboard(period="weekly", limit=10):
        """Fetches ranked list of players by XP."""
        if period == "weekly":
            last_monday = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
            last_monday = last_monday.replace(hour=0, minute=0, second=0)
            
            results = db.session.query(
                User.id, User.name, PlayerProfile.level, 
                func.sum(XPEvent.xp_amount).label('period_xp')
            ).join(PlayerProfile, User.id == PlayerProfile.user_id)\
             .join(XPEvent, User.id == XPEvent.user_id)\
             .filter(XPEvent.created_at >= last_monday)\
             .group_by(User.id, User.name, PlayerProfile.level)\
             .order_by(func.sum(XPEvent.xp_amount).desc())\
             .limit(limit).all()
        else:
            results = db.session.query(
                User.id, User.name, PlayerProfile.level, 
                PlayerProfile.xp_total.label('period_xp')
            ).join(PlayerProfile, User.id == PlayerProfile.user_id)\
             .order_by(PlayerProfile.xp_total.desc())\
             .limit(limit).all()
             
        board = []
        for idx, r in enumerate(results):
            board.append({
                "rank_num": idx + 1,
                "user_id": r.id,
                "name": r.name,
                "level": r.level,
                "rank_title": LEVEL_THRESHOLDS.get(r.level, {}).get("rank", "Scholar"),
                "xp": r.period_xp or 0
            })
        return board

    @staticmethod
    def assign_daily_challenges(user_id):
        """Assign daily challenges to the user if they don't have them yet for today."""
        today = date.today()
        existing = UserChallenge.query.join(Challenge).filter(
            UserChallenge.user_id == user_id,
            UserChallenge.assigned_date == today,
            Challenge.challenge_type == 'daily'
        ).first()
        
        if not existing:
            challenges = Challenge.query.filter_by(challenge_type='daily', is_active=True).all()
            if len(challenges) >= 3:
                chosen = random.sample(challenges, 3)
                end_of_day = datetime.combine(today, datetime.max.time())
                for c in chosen:
                    uc = UserChallenge(
                        user_id=user_id,
                        challenge_id=c.id,
                        goal=c.goal_count,
                        assigned_date=today,
                        expires_at=end_of_day
                    )
                    db.session.add(uc)
                db.session.commit()

    @staticmethod
    def assign_weekly_challenges(user_id):
        """Assign weekly challenges on Monday (or first interaction in the week)."""
        today = date.today()
        last_m = today - timedelta(days=today.weekday())
        end_sun = datetime.combine(last_m + timedelta(days=6), datetime.max.time())
        
        existing = UserChallenge.query.join(Challenge).filter(
            UserChallenge.user_id == user_id,
            UserChallenge.assigned_date >= last_m,
            Challenge.challenge_type == 'weekly'
        ).first()
        
        if not existing:
            challenges = Challenge.query.filter_by(challenge_type='weekly', is_active=True).all()
            if len(challenges) >= 2:
                chosen = random.sample(challenges, 2)
                for c in chosen:
                    uc = UserChallenge(
                        user_id=user_id,
                        challenge_id=c.id,
                        goal=c.goal_count,
                        assigned_date=today,
                        expires_at=end_sun
                    )
                    db.session.add(uc)
                db.session.commit()

    @staticmethod
    def update_challenge_progress(user_id, goal_type, increment=1):
        """Increments progress of active matching challenges."""
        now = datetime.utcnow()
        ucs = UserChallenge.query.join(Challenge).filter(
            UserChallenge.user_id == user_id,
            UserChallenge.is_completed == False,
            UserChallenge.expires_at > now,
            Challenge.goal_type == goal_type
        ).all()
        
        completed = []
        for uc in ucs:
            uc.progress += increment
            if uc.progress >= uc.goal:
                uc.is_completed = True
                uc.completed_at = now
                c = uc.challenge_ref
                # Award XP immediately
                XPEvent(
                    user_id=user_id,
                    event_type="challenge_complete",
                    xp_amount=c.xp_reward,
                    description=f"Completed challenge: {c.title}"
                )
                p = PlayerProfile.query.filter_by(user_id=user_id).first()
                p.xp_total += c.xp_reward
                GamificationService.check_level_up(p)
                
                completed.append({
                    "title": c.title,
                    "xp_reward": c.xp_reward
                })
        db.session.commit()
        return completed

    @staticmethod
    def get_player_stats(user_id):
        """Aggregates player stat profile."""
        p = PlayerProfile.query.filter_by(user_id=user_id).first()
        if not p: return {}
        
        next_threshold = LEVEL_THRESHOLDS.get(p.level + 1, {}).get("xp", 999999)
        current_base = LEVEL_THRESHOLDS.get(p.level, {}).get("xp", 0)
        to_next = int(next_threshold) - int(current_base)
        pct = int(((p.xp_total - int(current_base)) / to_next) * 100) if to_next > 0 else 100
        
        badges = UserBadge.query.filter_by(user_id=user_id).order_by(UserBadge.earned_at.desc()).all()
        
        return {
            "level": p.level,
            "rank": LEVEL_THRESHOLDS.get(p.level, {}).get("rank", "Scholar"),
            "xp_total": p.xp_total,
            "xp_current_level": p.xp_total - current_base,
            "xp_to_next_level": to_next,
            "level_progress_pct": min(100, max(0, pct)),
            "streak_current": p.streak_current,
            "streak_longest": p.streak_longest,
            "badges_earned_count": len(badges),
            "recent_badges": [{"emoji": b.badge.icon_emoji, "name": b.badge.name} for b in badges[:3]],
            "total_messages": p.total_chat_messages,
            "total_sessions": p.total_sessions_completed
        }
