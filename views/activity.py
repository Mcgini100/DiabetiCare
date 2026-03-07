from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from extensions import db
from models import Exercise
from forms import ExerciseForm

activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_exercise():
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(user_id=current_user.id, activity_type=form.activity_type.data,
            duration_minutes=form.duration_minutes.data, intensity=form.intensity.data,
            calories_burned=form.calories_burned.data, notes=form.notes.data)
        db.session.add(exercise)
        db.session.commit()
        flash(f'Exercise logged! {form.duration_minutes.data} minutes of {form.activity_type.data}.', 'success')
        return redirect(url_for('activity.history'))

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    week_exercises = Exercise.query.filter(
        Exercise.user_id == current_user.id, Exercise.logged_at >= week_ago
    ).all()
    weekly_total = sum(e.duration_minutes for e in week_exercises)
    recent = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.logged_at.desc()).limit(5).all()

    return render_template('activity/log.html', form=form, recent=recent, weekly_total=weekly_total)


@activity_bp.route('/history')
@login_required
def history():
    exercises = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.logged_at.desc()).limit(30).all()

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    week_data = Exercise.query.filter(
        Exercise.user_id == current_user.id, Exercise.logged_at >= week_ago
    ).all()
    weekly_total = sum(e.duration_minutes for e in week_data)
    weekly_calories = sum(e.calories_burned or 0 for e in week_data)

    return render_template('activity/history.html', exercises=exercises,
                         weekly_total=weekly_total, weekly_calories=weekly_calories)


@activity_bp.route('/delete/<int:exercise_id>', methods=['POST'])
@login_required
def delete(exercise_id):
    e = Exercise.query.get_or_404(exercise_id)
    if e.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('activity.history'))
    db.session.delete(e)
    db.session.commit()
    flash('Exercise deleted.', 'info')
    return redirect(url_for('activity.history'))
