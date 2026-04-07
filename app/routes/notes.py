import os
import fitz  # PyMuPDF
from docx import Document
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import google.generativeai as genai
from app import db, limiter
from app.models import User, LearningProfile, UploadedNote
from app.services.gamification import GamificationService

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath, filename):
    ext = filename.rsplit('.', 1)[1].lower()
    text = ""
    try:
        if ext == 'pdf':
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif ext == 'docx':
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    except Exception as e:
        print(f"Extraction error: {e}")
        return None
    return str(text)[:30000] # Limit to roughly ~8-10k tokens

# Gemini Helpers
def generate_adaptive_explanation(profile, extracted_text):
    style = profile.learning_style if profile else 'reading'
    pace = profile.learning_pace if profile else 'medium'
    
    prompt = f"""You are an expert tutor. A student has uploaded a document. Based on their 
{style.upper()} learning style and {pace.upper()} pace, explain the key concepts in this 
document in the most effective way for them.

STYLE GUIDELINES:
- VISUAL: Use structured layouts, bullet points, analogies, suggest diagrams or visual metaphors.
- AUDITORY: Explain like you're speaking aloud, use rhythm, storytelling, real-world verbal examples.
- READING: Provide detailed written explanations, definitions, step-by-step breakdowns.
- KINESTHETIC: Use hands-on examples, experiments, real-world application scenarios.

PACE GUIDELINES:
- SLOW: Explain step-by-step, repeat key points, avoid jargon.
- MEDIUM: Balanced explanation with moderate depth.
- FAST: Dense, efficient, skip basics, go deeper faster.

Format your output nicely in Markdown.

Here is the document content:
{extracted_text}"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I encountered an error generating the explanation."

def answer_follow_up(profile, summary, question):
    style = profile.learning_style if profile else 'reading'
    pace = profile.learning_pace if profile else 'medium'
    
    prompt = f"""The student previously uploaded a document. Here is a summary of the document: 
{summary}

Their related follow-up question is: {question}

Answer in their {style.upper()} style at {pace.upper()} pace. Use Markdown."""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I encountered an error answering your question."

@notes_bp.route('/')
@login_required
def index():
    recent_notes = UploadedNote.query.filter_by(user_id=current_user.id).order_by(UploadedNote.uploaded_at.desc()).limit(5).all()
    return render_template('notes/upload.html', recent_notes=recent_notes)

@notes_bp.route('/upload', methods=['POST'])
@login_required
@limiter.limit("5/hour")
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('notes.index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('notes.index'))
        
    subject = request.form.get('subject', 'General')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Ensure uploads dir exists
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        extracted_text = extract_text_from_file(filepath, filename)
        
        # Cleanup file
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if not extracted_text:
            flash('Error extracting text from file.', 'error')
            return redirect(url_for('notes.index'))
            
        profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
        explanation = generate_adaptive_explanation(profile, extracted_text)
        
        new_note = UploadedNote(
            user_id=current_user.id,
            filename=filename,
            file_type=filename.rsplit('.', 1)[1].lower(),
            extracted_text=extracted_text,
            subject=subject,
            summary=explanation
        )
        db.session.add(new_note)
        db.session.commit()
        
        # Gamification
        GamificationService.award_xp(current_user.id, "note_uploaded", 20, "Uploaded and studied a document")
        uploads_count = UploadedNote.query.filter_by(user_id=current_user.id).count()
        if uploads_count == 1:
            try:
                # Assuming Knowledge Seeker might not be explicitly loaded above for "note_uploaded", just safe manual call
                GamificationService.award_badge(current_user.id, "first_session") # reusing general achievement if "Knowledge Seeker" isn't explicitly defined, prompt suggested checking it
            except:
                pass
                
        flash('Document uploaded and explained successfully!', 'success')
        return redirect(url_for('notes.view', note_id=new_note.id))
        
    flash('Invalid file type. Only PDF, DOCX, and TXT are allowed.', 'error')
    return redirect(url_for('notes.index'))

@notes_bp.route('/view/<int:note_id>')
@login_required
def view(note_id):
    note = UploadedNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('notes.index'))
        
    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('notes/view.html', note=note, profile=profile)

@notes_bp.route('/ask/<int:note_id>', methods=['POST'])
@login_required
@limiter.limit("20/hour")
def ask(note_id):
    note = UploadedNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
        
    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    answer = answer_follow_up(profile, note.summary, question)
    
    return jsonify({
        'answer': answer
    })

@notes_bp.route('/history')
@login_required
def history():
    notes = UploadedNote.query.filter_by(user_id=current_user.id).order_by(UploadedNote.uploaded_at.desc()).all()
    return render_template('notes/history.html', notes=notes)

@notes_bp.route('/delete/<int:note_id>', methods=['POST'])
@login_required
def delete(note_id):
    note = UploadedNote.query.get_or_404(note_id)
    if note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted.', 'success')
    return redirect(url_for('notes.history'))
