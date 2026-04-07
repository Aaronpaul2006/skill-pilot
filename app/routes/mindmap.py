import json
import html
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import google.generativeai as genai
from app import db, limiter
from app.models import LearningProfile, MindMap, ConceptStatus
from app.services.gamification import GamificationService

mindmap_bp = Blueprint('mindmap', __name__, url_prefix='/mindmap')

# ── Gemini helpers ────────────────────────────────────────────────────────────

def _build_generation_prompt(topic, style, pace):
    return f"""Generate a detailed concept mind map for the topic: '{topic}'.
The student is a {style.upper()} learner with a {pace.upper()} learning pace.

Return ONLY this exact JSON structure (no markdown, no explanation, ONLY raw JSON):
{{
  "topic": "Main Topic Name",
  "description": "One sentence overview",
  "nodes": [
    {{
      "id": "unique_snake_case_id",
      "label": "Concept Name",
      "description": "Brief 1-2 sentence explanation",
      "difficulty": "beginner or intermediate or advanced",
      "learn_order": 1,
      "parent_id": null,
      "type": "root or branch or leaf",
      "prerequisites": [],
      "keywords": ["keyword1", "keyword2"]
    }}
  ],
  "edges": [
    {{
      "from": "node_id",
      "to": "node_id",
      "relationship": "contains or leads_to or requires or related_to"
    }}
  ],
  "learning_path": ["node_id_1", "node_id_2", "node_id_3"],
  "estimated_hours": 12
}}
Generate 15-25 nodes covering the topic thoroughly. Make sure all node IDs referenced in edges and learning_path exist in the nodes array."""


def _generate_map_data(topic, profile):
    style = profile.learning_style if profile else 'reading'
    pace = profile.learning_pace if profile else 'medium'
    prompt = _build_generation_prompt(topic, style, pace)

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        raw = response.text.strip()
        # Try to parse raw JSON
        data = json.loads(raw)
        # Basic validation
        if 'nodes' not in data or 'edges' not in data:
            raise ValueError("Missing nodes or edges")
        return data
    except Exception as e:
        print(f"Gemini mind-map error (attempt 1): {e}")
        # Retry with simpler prompt
        try:
            simple = f"Generate a concept mind map with 10 nodes for '{topic}'. Return ONLY valid JSON with keys: topic, description, nodes (id,label,description,difficulty,learn_order,parent_id,type,prerequisites,keywords), edges (from,to,relationship), learning_path, estimated_hours."
            response = model.generate_content(
                simple,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text.strip())
            return data
        except Exception as e2:
            print(f"Gemini mind-map error (attempt 2): {e2}")
            return None


def _generate_concept_notes(concept_name, topic, style, pace):
    prompt = f"""Explain the concept '{concept_name}' which is part of '{topic}' to a {style.upper()} learner at {pace.upper()} pace.

Include:
- Simple definition (1-2 sentences)
- Key idea or core principle
- A concrete real-world example
- Common mistakes or misconceptions
- What to study before this (prerequisites)
- What this unlocks next

Keep total response under 200 words. Use Markdown formatting appropriate for a {style.upper()} learner."""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini concept notes error: {e}")
        return f"Could not generate notes for **{concept_name}** at this time."


# ── Routes ────────────────────────────────────────────────────────────────────

@mindmap_bp.route('/')
@login_required
def index():
    saved = MindMap.query.filter_by(user_id=current_user.id).order_by(MindMap.created_at.desc()).limit(6).all()
    return render_template('mindmap/index.html', saved_maps=saved)


@mindmap_bp.route('/generate', methods=['POST'])
@login_required
@limiter.limit("10/hour")
def generate():
    topic = request.form.get('topic', '').strip()
    subject = request.form.get('subject', 'General')

    if not topic or len(topic) > 100:
        flash('Please enter a valid topic (max 100 characters).', 'error')
        return redirect(url_for('mindmap.index'))

    topic = html.escape(topic)
    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    data = _generate_map_data(topic, profile)

    if data is None:
        flash('AI could not generate a mind map. Please try a different topic.', 'error')
        return redirect(url_for('mindmap.index'))

    new_map = MindMap(
        user_id=current_user.id,
        topic=topic,
        subject=subject,
        map_data=json.dumps(data)
    )
    db.session.add(new_map)
    db.session.commit()

    # Gamification – award XP
    try:
        GamificationService.award_xp(current_user.id, "mindmap_generated", 25,
                                     f"Generated a mind map for {topic}")
        map_count = MindMap.query.filter_by(user_id=current_user.id).count()
        if map_count == 1:
            GamificationService.award_badge(current_user.id, "mind_mapper")
    except Exception:
        pass

    flash('Mind map generated successfully!', 'success')
    return redirect(url_for('mindmap.view', map_id=new_map.id))


@mindmap_bp.route('/view/<int:map_id>')
@login_required
def view(map_id):
    mm = MindMap.query.get_or_404(map_id)
    if mm.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('mindmap.index'))

    map_data = json.loads(mm.map_data)

    # Load concept statuses into a dict {concept_name: status}
    statuses = {}
    for cs in ConceptStatus.query.filter_by(user_id=current_user.id, mindmap_id=map_id).all():
        statuses[cs.concept_name] = cs.status

    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('mindmap/view.html', mm=mm, map_data=map_data,
                           statuses=statuses, profile=profile)


@mindmap_bp.route('/concept/notes', methods=['POST'])
@login_required
@limiter.limit("30/hour")
def concept_notes():
    data = request.get_json()
    concept = data.get('concept', '')
    topic = data.get('topic', '')
    if not concept:
        return jsonify({'success': False, 'error': 'No concept provided'}), 400

    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    style = profile.learning_style if profile else 'reading'
    pace = profile.learning_pace if profile else 'medium'

    notes = _generate_concept_notes(concept, topic, style, pace)
    return jsonify({'success': True, 'concept': concept, 'notes': notes})


@mindmap_bp.route('/concept/status', methods=['POST'])
@login_required
def concept_status():
    data = request.get_json()
    mindmap_id = data.get('mindmap_id')
    concept_name = data.get('concept_name')
    new_status = data.get('status')

    if new_status not in ('not_started', 'in_progress', 'understood', 'needs_review'):
        return jsonify({'success': False, 'error': 'Invalid status'}), 400

    mm = MindMap.query.get_or_404(mindmap_id)
    if mm.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    cs = ConceptStatus.query.filter_by(
        user_id=current_user.id, mindmap_id=mindmap_id, concept_name=concept_name
    ).first()

    if cs:
        cs.status = new_status
    else:
        cs = ConceptStatus(
            user_id=current_user.id, mindmap_id=mindmap_id,
            concept_name=concept_name, status=new_status
        )
        db.session.add(cs)
    db.session.commit()

    # Check if all concepts are understood → bonus XP
    try:
        map_data = json.loads(mm.map_data)
        total_nodes = len(map_data.get('nodes', []))
        understood = ConceptStatus.query.filter_by(
            user_id=current_user.id, mindmap_id=mindmap_id, status='understood'
        ).count()
        if total_nodes > 0 and understood >= total_nodes:
            GamificationService.award_xp(current_user.id, "mindmap_mastered", 50,
                                         f"Mastered all concepts in {mm.topic}")
    except Exception:
        pass

    return jsonify({'success': True, 'status': new_status})


@mindmap_bp.route('/path/<int:map_id>')
@login_required
def learning_path(map_id):
    mm = MindMap.query.get_or_404(map_id)
    if mm.user_id != current_user.id:
        return jsonify({'success': False}), 403
    data = json.loads(mm.map_data)
    path = data.get('learning_path', [])
    # Build ordered list with labels
    node_map = {n['id']: n['label'] for n in data.get('nodes', [])}
    ordered = [{'id': nid, 'label': node_map.get(nid, nid), 'order': i + 1}
               for i, nid in enumerate(path)]
    return jsonify({'success': True, 'path': ordered})


@mindmap_bp.route('/history')
@login_required
def history():
    maps = MindMap.query.filter_by(user_id=current_user.id).order_by(MindMap.created_at.desc()).all()
    # Enrich with progress stats
    enriched = []
    for m in maps:
        data = json.loads(m.map_data)
        total = len(data.get('nodes', []))
        understood = ConceptStatus.query.filter_by(
            user_id=current_user.id, mindmap_id=m.id, status='understood'
        ).count()
        enriched.append({
            'map': m,
            'total': total,
            'understood': understood,
            'pct': int((understood / total) * 100) if total > 0 else 0
        })
    return render_template('mindmap/history.html', maps=enriched)


@mindmap_bp.route('/delete/<int:map_id>', methods=['POST'])
@login_required
def delete(map_id):
    mm = MindMap.query.get_or_404(map_id)
    if mm.user_id == current_user.id:
        db.session.delete(mm)
        db.session.commit()
        flash('Mind map deleted.', 'success')
    return redirect(url_for('mindmap.history'))


@mindmap_bp.route('/regenerate/<int:map_id>', methods=['POST'])
@login_required
@limiter.limit("10/hour")
def regenerate(map_id):
    mm = MindMap.query.get_or_404(map_id)
    if mm.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('mindmap.index'))

    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    data = _generate_map_data(mm.topic, profile)

    if data is None:
        flash('Could not regenerate map. Try again later.', 'error')
        return redirect(url_for('mindmap.view', map_id=map_id))

    mm.map_data = json.dumps(data)
    # Clear old statuses
    ConceptStatus.query.filter_by(user_id=current_user.id, mindmap_id=map_id).delete()
    db.session.commit()

    flash('Mind map regenerated!', 'success')
    return redirect(url_for('mindmap.view', map_id=map_id))
