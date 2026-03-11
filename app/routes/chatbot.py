import html
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
import google.generativeai as genai
from app import db, limiter
from app.models import ChatMessage, LearningProfile
from config import Config
from datetime import datetime

chatbot = Blueprint('chatbot', __name__)
genai.configure(api_key=Config.GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

def build_system_prompt(learning_style, learning_pace, subject):
    base = f"You are SKILL PILOT, an expert adaptive tutor for college students.\nStudent profile — Style: {learning_style.upper()}, Pace: {learning_pace.upper()}.\nSTRICT RULES:\n"
    
    if learning_style == 'visual' and learning_pace == 'slow':
        rules = """- Always use structured formatting: numbered steps, bullet points, tables
- Describe diagrams and charts in text (e.g., 'Imagine a flowchart where...')
- Use analogies with visual comparisons (e.g., 'Think of it like a tree diagram')
- Go step by step — NEVER skip steps
- After each concept ask: 'Does this make sense so far?'
- Use simple vocabulary, avoid jargon unless explained
- Give at least 2 examples per concept
- End every response with: 'What part would you like me to visualize further?'"""
    elif learning_style == 'visual' and learning_pace == 'fast':
        rules = """- Use structured formatting but be concise
- Include diagrams described in text for complex topics only
- Jump to advanced aspects quickly
- Challenge with follow-up questions
- End with: 'Want to go deeper into any part of this?'"""
    elif learning_style == 'auditory' and learning_pace == 'slow':
        rules = """- Write in a conversational talking tone, like explaining to a friend
- Use phrases like 'So what this means is...' and 'Think of it this way...'
- Repeat key ideas in different words
- Use storytelling and verbal analogies
- Ask comprehension check questions frequently
- End with: 'How does that sound to you?'"""
    elif learning_style == 'auditory' and learning_pace == 'fast':
        rules = """- Conversational and punchy tone
- Quick verbal analogies
- Skip basics, go to insights directly
- End with: 'Want me to walk through a harder example?'"""
    elif learning_style == 'reading' and learning_pace == 'slow':
        rules = """- Write in detailed paragraph form like a textbook
- Define every technical term when first used
- Provide thorough explanations with full context
- Include written examples with line-by-line breakdown
- Summarize key points at the end of each response
- End with: 'Would you like me to elaborate on any section?'"""
    elif learning_style == 'reading' and learning_pace == 'fast':
        rules = """- Dense, documentation-style responses
- Technical depth with precise terminology
- Reference advanced concepts freely
- End with: 'Want the technical deep-dive on any part?'"""
    elif learning_style == 'kinesthetic' and learning_pace == 'slow':
        rules = """- Always tie concepts to hands-on examples and mini projects
- Break every concept into small actionable steps
- Give beginner-friendly practice exercises
- Use real-world applications relevant to college projects
- Guide through each step patiently
- End with: 'Try this small exercise and tell me what happens'"""
    elif learning_style == 'kinesthetic' and learning_pace == 'fast':
        rules = """- Jump straight to practical application
- Give challenging real-world problems
- Minimal theory, maximum practice
- Push with harder follow-up exercises
- End with: 'Here is a harder challenge for you:'"""
    else:
        rules = "Be clear, helpful and encouraging."
        
    return base + rules + f"\nSubject focus: {subject}"

def detect_and_update_pace(user_message, profile):
    msg_lower = user_message.lower()
    
    slow_keywords = ["don't understand", "confused", "again", "explain more", "what does", "i'm lost", "can you repeat", "not clear", "what is", "help me understand"]
    fast_keywords = ["got it", "i know", "skip", "next", "already know", "what else", "more advanced", "harder", "i understand", "what about", "and then"]
    
    if any(k in msg_lower for k in slow_keywords):
        profile.slow_signals += 1
    elif any(k in msg_lower for k in fast_keywords):
        profile.fast_signals += 1
        
    total_signals = profile.slow_signals + profile.fast_signals
    if total_signals > 0 and total_signals % 5 == 0:
        if profile.slow_signals > profile.fast_signals * 2:
            profile.learning_pace = 'slow'
        elif profile.fast_signals > profile.slow_signals * 2:
            profile.learning_pace = 'fast'
        else:
            profile.learning_pace = 'medium'
        print(f"🔄 Pace updated to {profile.learning_pace} for user {profile.user_id}")
    
    db.session.commit()

@chatbot.route('/chat')
@login_required
def chat():
    if not current_user.learning_profile or not current_user.learning_profile.onboarding_done:
        flash("Please complete onboarding first.", "error")
        return redirect(url_for('onboarding.quiz'))
        
    topic = request.args.get('topic', '')
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).limit(20).all()
    
    return render_template('chatbot/chat.html', profile=current_user.learning_profile, messages=messages, prefill_topic=topic, user=current_user)

@chatbot.route('/chat/send', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def send():
    user_message = request.json.get('message', '').strip()
    profile = current_user.learning_profile
    subject = request.json.get('subject', profile.subject_focus)

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    # Length limit
    if len(user_message) > 2000:
        return jsonify({'error': 'Message too long. Max 2000 characters.'}), 400

    # Sanitize
    user_message = html.escape(user_message)

    user_msg_db = ChatMessage(user_id=current_user.id, role='user', content=user_message, subject=subject)
    db.session.add(user_msg_db)
    db.session.commit()
    
    detect_and_update_pace(user_message, profile)
    db.session.refresh(profile)
    
    history_db = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.desc()).limit(11).all()
    history_db.reverse()
    
    conversation_history = [{"role": msg.role, "content": msg.content} for msg in history_db]
    
    system_prompt = build_system_prompt(profile.learning_style, profile.learning_pace, subject)
    
    try:
        gemini_history = []
        for msg in conversation_history[:-1]:
            gemini_role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({
                "role": gemini_role,
                "parts": [{"text": msg["content"]}]
            })
            
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_prompt
        )
        
        chat_session = model.start_chat(history=gemini_history)
        latest_message = conversation_history[-1]["content"]
        response = chat_session.send_message(latest_message)
        
        if not response.text:
            raise ValueError("Empty response")
        
        ai_response = response.text
        
        ai_msg_db = ChatMessage(user_id=current_user.id, role='assistant', content=ai_response, subject=subject)
        db.session.add(ai_msg_db)
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'learning_style': profile.learning_style,
            'learning_pace': profile.learning_pace,
            'subject': subject,
            'slow_signals': profile.slow_signals,
            'fast_signals': profile.fast_signals
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot.route('/chat/history')
@login_required
def get_history():
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).all()
    return jsonify([msg.to_dict() for msg in messages])

@chatbot.route('/chat/clear', methods=['POST'])
@login_required
def clear():
    ChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'status': 'cleared', 'message': 'Chat history cleared'})

@chatbot.route('/chat/profile-status')
@login_required
def profile_status():
    p = current_user.learning_profile
    total_messages = ChatMessage.query.filter_by(user_id=current_user.id).count()
    return jsonify({
        'learning_style': p.learning_style,
        'learning_pace': p.learning_pace,
        'subject_focus': p.subject_focus,
        'slow_signals': p.slow_signals,
        'fast_signals': p.fast_signals,
        'total_messages': total_messages
    })
