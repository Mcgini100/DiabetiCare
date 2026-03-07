from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import EducationModule, Quiz, QuizResult
import json

education_bp = Blueprint('education', __name__)


@education_bp.route('/')
@login_required
def index():
    modules = EducationModule.query.filter_by(language='en').order_by(EducationModule.order).all()
    categories = {}
    for m in modules:
        categories.setdefault(m.category, []).append(m)
    return render_template('education/index.html', categories=categories)


@education_bp.route('/module/<int:module_id>')
@login_required
def module(module_id):
    mod = EducationModule.query.get_or_404(module_id)
    return render_template('education/module.html', module=mod)


@education_bp.route('/quiz/<int:module_id>', methods=['GET', 'POST'])
@login_required
def quiz(module_id):
    mod = EducationModule.query.get_or_404(module_id)
    questions = Quiz.query.filter_by(module_id=module_id).all()

    if request.method == 'POST':
        score = 0
        total = len(questions)
        results = []
        for q in questions:
            answer = request.form.get(f'q_{q.id}', '')
            correct = answer.lower() == q.correct_answer.lower()
            if correct:
                score += 1
            results.append({'question': q.question, 'user_answer': answer,
                          'correct_answer': q.correct_answer, 'correct': correct,
                          'explanation': q.explanation})

        quiz_result = QuizResult(user_id=current_user.id, module_id=module_id,
                                score=score, total=total)
        db.session.add(quiz_result)
        db.session.commit()

        pct = round(score / total * 100) if total > 0 else 0
        if pct >= 80:
            flash(f'🎉 Great job! You scored {score}/{total} ({pct}%)!', 'success')
        elif pct >= 50:
            flash(f'Good attempt! You scored {score}/{total} ({pct}%). Review the module for improvement.', 'warning')
        else:
            flash(f'You scored {score}/{total} ({pct}%). Please review the module and try again.', 'info')

        return render_template('education/quiz_results.html', module=mod,
                             results=results, score=score, total=total, pct=pct)

    return render_template('education/quiz.html', module=mod, questions=questions)
