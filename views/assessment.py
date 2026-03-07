from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Assessment
import json

assessment_bp = Blueprint('assessment', __name__)

QUESTIONS = [
    {'id': 1, 'text': 'How often do you check your blood sugar?', 'options': ['Never', 'Rarely', 'Sometimes', 'Regularly', 'As recommended']},
    {'id': 2, 'text': 'Do you know your target blood glucose range?', 'options': ['No', 'Not sure', 'Somewhat', 'Yes']},
    {'id': 3, 'text': 'How well do you follow your medication schedule?', 'options': ['Not at all', 'Poorly', 'Sometimes', 'Usually', 'Always']},
    {'id': 4, 'text': 'How often do you exercise each week?', 'options': ['Never', '1-2 times', '3-4 times', '5+ times']},
    {'id': 5, 'text': 'How well do you follow dietary recommendations?', 'options': ['Not at all', 'Poorly', 'Sometimes', 'Usually', 'Always']},
    {'id': 6, 'text': 'Do you inspect your feet daily?', 'options': ['Never', 'Rarely', 'Sometimes', 'Usually', 'Always']},
    {'id': 7, 'text': 'When was your last HbA1c test?', 'options': ['Never/Don\'t know', 'Over a year ago', '6-12 months', 'Within 6 months', 'Within 3 months']},
    {'id': 8, 'text': 'Do you know what to do when your blood sugar is too low?', 'options': ['No', 'Not sure', 'Somewhat', 'Yes']},
    {'id': 9, 'text': 'Have you had an eye exam in the past year?', 'options': ['No', 'Yes']},
    {'id': 10, 'text': 'How confident are you in managing your diabetes?', 'options': ['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely']},
]


@assessment_bp.route('/', methods=['GET', 'POST'])
@login_required
def questionnaire():
    if request.method == 'POST':
        responses = {}
        score = 0
        max_score = 0
        for q in QUESTIONS:
            answer = request.form.get(f'q_{q["id"]}', '')
            responses[str(q['id'])] = answer
            idx = q['options'].index(answer) if answer in q['options'] else 0
            score += idx
            max_score += len(q['options']) - 1

        pct = round(score / max_score * 100) if max_score else 0
        if pct >= 80:
            feedback = "Excellent! You demonstrate strong self-management practices. Keep up the great work!"
        elif pct >= 60:
            feedback = "Good progress! You're on the right track. Consider improving in areas where you scored lower."
        elif pct >= 40:
            feedback = "Fair. There's room for improvement. Focus on regular monitoring, medication adherence, and healthy lifestyle habits."
        else:
            feedback = "It looks like you may benefit from more support. Please consult your healthcare provider and explore our educational resources."

        assessment = Assessment(user_id=current_user.id, assessment_type='self_care',
            responses=json.dumps(responses), score=score, max_score=max_score, feedback=feedback)
        db.session.add(assessment)
        db.session.commit()

        return render_template('assessment/results.html', score=score, max_score=max_score, pct=pct,
                             feedback=feedback, responses=responses, questions=QUESTIONS)

    past = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.completed_at.desc()).limit(5).all()
    return render_template('assessment/questionnaire.html', questions=QUESTIONS, past=past)
