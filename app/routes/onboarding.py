from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import LearningProfile

onboarding = Blueprint('onboarding', __name__)

QUIZ_QUESTIONS = [
  {
    "id": 1,
    "question": "When learning something new, you prefer to:",
    "options": {
      "A": "Watch a diagram, chart or video explanation",
      "B": "Listen to a lecture or podcast about it",
      "C": "Read a detailed textbook or article",
      "D": "Try it out hands-on immediately"
    }
  },
  {
    "id": 2,
    "question": "When you forget how to do something, you:",
    "options": {
      "A": "Look for a diagram or visual example",
      "B": "Ask someone to explain it to you verbally",
      "C": "Search for written notes or documentation",
      "D": "Just try doing it again until it works"
    }
  },
  {
    "id": 3,
    "question": "During a lecture, you learn best when the teacher:",
    "options": {
      "A": "Uses lots of diagrams, slides and charts",
      "B": "Explains concepts clearly through talking",
      "C": "Provides detailed handouts or notes",
      "D": "Gives live demos and practical examples"
    }
  },
  {
    "id": 4,
    "question": "To remember a new concept, you usually:",
    "options": {
      "A": "Draw a mind map or sketch it out",
      "B": "Repeat it out loud or discuss with friends",
      "C": "Write detailed notes and re-read them",
      "D": "Build something or apply it to a project"
    }
  },
  {
    "id": 5,
    "question": "When solving a complex problem, you prefer to:",
    "options": {
      "A": "Visualize the problem with a flowchart",
      "B": "Talk through the steps out loud",
      "C": "Write out all the steps on paper",
      "D": "Jump in and experiment with solutions"
    }
  },
  {
    "id": 6,
    "question": "Your ideal study resource is:",
    "options": {
      "A": "YouTube tutorials with visual animations",
      "B": "Audio lectures or study group discussions",
      "C": "Textbooks, PDFs and written guides",
      "D": "Coding exercises, labs or practice problems"
    }
  },
  {
    "id": 7,
    "question": "You find it easiest to understand a new formula when:",
    "options": {
      "A": "It is shown with a graph or visual",
      "B": "Someone walks you through it verbally",
      "C": "You read the derivation step by step",
      "D": "You apply it to solve an actual problem"
    }
  },
  {
    "id": 8,
    "question": "During exams, you remember things best from:",
    "options": {
      "A": "Diagrams and visual summaries you studied",
      "B": "Things you discussed or heard in class",
      "C": "Detailed notes you wrote and reviewed",
      "D": "Practice problems and labs you worked on"
    }
  },
  {
    "id": 9,
    "question": "How do you prefer to learn new topics?",
    "options": {
      "A": "I need lots of time, examples and repetition",
      "B": "I take moderate time with some examples",
      "C": "I grasp quickly and prefer challenges",
      "D": "It depends on the topic"
    },
    "pace_map": {"A": "slow", "B": "medium", "C": "fast", "D": "medium"}
  },
  {
    "id": 10,
    "question": "When stuck on a problem, you usually:",
    "options": {
      "A": "Re-read everything carefully from the beginning",
      "B": "Review key parts and try again",
      "C": "Search quickly online and move forward",
      "D": "Ask a friend or teacher immediately"
    },
    "pace_map": {"A": "slow", "B": "medium", "C": "fast", "D": "medium"}
  }
]

@onboarding.route('/onboarding')
@login_required
def quiz():
    if current_user.learning_profile and current_user.learning_profile.onboarding_done:
        flash("You have already completed onboarding!", "success")
        return redirect(url_for('dashboard.dashboard_route'))
    
    return render_template('onboarding/quiz.html', questions=QUIZ_QUESTIONS, user=current_user)

@onboarding.route('/onboarding/submit', methods=['POST'])
@login_required
def submit():
    # Validate
    answers = {}
    for i in range(1, 11):
        ans = request.form.get(f'q{i}')
        if not ans:
            flash("Please answer all 10 questions.", "error")
            return redirect(url_for('onboarding.quiz'))
        answers[i] = ans
        
    subject_focus = request.form.get('subject_focus')
    if not subject_focus:
        flash("Please select a subject focus.", "error")
        return redirect(url_for('onboarding.quiz'))

    # VARK SCORING (Q1-Q8)
    style_scores = {"visual": 0, "auditory": 0, "reading": 0, "kinesthetic": 0}
    style_map = {"A": "visual", "B": "auditory", "C": "reading", "D": "kinesthetic"}
    
    for i in range(1, 9):
        ans = answers[i]
        style = style_map.get(ans)
        if style:
            style_scores[style] += 1
            
    # Find max score style, tie-breaker: kinesthetic > visual > auditory > reading
    best_style = 'reading'
    max_score = -1
    priority = {'kinesthetic': 4, 'visual': 3, 'auditory': 2, 'reading': 1}
    
    for style, score in style_scores.items():
        if score > max_score:
            max_score = score
            best_style = style
        elif score == max_score:
            if priority[style] > priority[best_style]:
                best_style = style

    # PACE SCORING (Q9-Q10)
    q9_map = {"A": "slow", "B": "medium", "C": "fast", "D": "medium"}
    q10_map = {"A": "slow", "B": "medium", "C": "fast", "D": "medium"}
    
    pace_votes = []
    pace_votes.append(q9_map.get(answers[9], "medium"))
    pace_votes.append(q10_map.get(answers[10], "medium"))
    
    if pace_votes[0] == pace_votes[1]:
        final_pace = pace_votes[0]
    elif ("slow" in pace_votes and "fast" in pace_votes):
        final_pace = "medium"
    else:
        # if no consensus, default medium or pick one? requirement:
        # "final_pace = most common in pace_votes. If slow+fast tie -> medium"
        # If they pick slow and medium, most common? It's a tie between slow and medium.
        # Let's just average or default to medium if tie, or pick one. 
        # Actually rule says: "most common in pace_votes. If one slow + one fast -> medium"
        # For a 2-vote system, a tie means they are different. If slow & medium -> medium? Fast & medium -> medium?
        if "medium" in pace_votes:
            final_pace = "medium"
        else:
            final_pace = "medium" # slow+fast tie -> medium. so any tie -> medium mostly.

    profile = current_user.learning_profile
    if not profile:
        profile = LearningProfile(user_id=current_user.id)
        db.session.add(profile)
        
    profile.learning_style = best_style
    profile.learning_pace = final_pace
    profile.subject_focus = subject_focus
    profile.onboarding_done = True
    
    db.session.commit()
    
    flash(f"✅ Profile saved! Your learning style is {best_style}, pace is {final_pace}.", "success")
    return redirect(url_for('dashboard.index'))

@onboarding.route('/onboarding/result')
@login_required
def result():
    if not current_user.learning_profile or not current_user.learning_profile.onboarding_done:
        return redirect(url_for('onboarding.quiz'))
        
    return render_template('onboarding/result.html', profile=current_user.learning_profile)

@onboarding.route('/onboarding/reset')
@login_required
def reset():
    profile = current_user.learning_profile
    if profile:
        profile.onboarding_done = False
        profile.learning_style = 'reading'
        profile.learning_pace = 'medium'
        db.session.commit()
        flash("Quiz reset! Please retake to update your profile.", "success")
    return redirect(url_for('onboarding.quiz'))
