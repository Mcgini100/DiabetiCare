from flask import Blueprint, render_template, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from extensions import db
from models import GlucoseReading, Medication, Feedback
from forms import SettingsForm, FeedbackForm, GoalForm
from models import Goal
from utils import export_glucose_csv, generate_pdf_report

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SettingsForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.language = form.language.data
        current_user.font_size = form.font_size.data
        current_user.high_contrast = form.high_contrast.data
        current_user.reminder_medication = form.reminder_medication.data
        current_user.reminder_glucose = form.reminder_glucose.data
        current_user.reminder_appointments = form.reminder_appointments.data
        current_user.receive_tips = form.receive_tips.data
        db.session.commit()
        flash('Settings saved!', 'success')
        return redirect(url_for('settings.index'))
    # Pre-fill
    form.name.data = current_user.name
    form.language.data = current_user.language
    form.font_size.data = current_user.font_size
    form.high_contrast.data = current_user.high_contrast
    form.reminder_medication.data = current_user.reminder_medication
    form.reminder_glucose.data = current_user.reminder_glucose
    form.reminder_appointments.data = current_user.reminder_appointments
    form.receive_tips.data = current_user.receive_tips
    return render_template('settings/index.html', form=form)


@settings_bp.route('/export')
@login_required
def export():
    return render_template('settings/export.html')


@settings_bp.route('/export/csv')
@login_required
def export_csv():
    readings = GlucoseReading.query.filter_by(user_id=current_user.id)\
        .order_by(GlucoseReading.reading_time.desc()).all()
    csv_data = export_glucose_csv(readings)
    return Response(csv_data, mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=diabeticare_export.csv'})


@settings_bp.route('/export/pdf')
@login_required
def export_pdf():
    since = datetime.now(timezone.utc) - timedelta(days=30)
    readings = GlucoseReading.query.filter(
        GlucoseReading.user_id == current_user.id,
        GlucoseReading.reading_time >= since
    ).order_by(GlucoseReading.reading_time.desc()).all()
    medications = Medication.query.filter_by(user_id=current_user.id, active=True).all()
    pdf_bytes = generate_pdf_report(current_user, readings, medications)
    if pdf_bytes is None:
        flash('PDF generation failed. Please ensure ReportLab is installed.', 'warning')
        return redirect(url_for('settings.export'))
    return Response(pdf_bytes, mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=diabeticare_report.pdf'})


@settings_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        fb = Feedback(user_id=current_user.id, subject=form.subject.data,
                     message=form.message.data, feedback_type=form.feedback_type.data)
        db.session.add(fb)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('settings.index'))
    return render_template('settings/feedback.html', form=form)


@settings_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(user_id=current_user.id, goal_type=form.goal_type.data,
                   title=form.title.data, target_value=form.target_value.data,
                   unit=form.unit.data, deadline=form.deadline.data)
        db.session.add(goal)
        db.session.commit()
        flash('Goal set!', 'success')
        return redirect(url_for('settings.goals'))
    active_goals = Goal.query.filter_by(user_id=current_user.id, achieved=False).all()
    achieved_goals = Goal.query.filter_by(user_id=current_user.id, achieved=True).order_by(Goal.created_at.desc()).limit(10).all()
    return render_template('settings/goals.html', form=form, active_goals=active_goals, achieved_goals=achieved_goals)


@settings_bp.route('/goals/achieve/<int:goal_id>')
@login_required
def achieve_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('settings.goals'))
    goal.achieved = True
    goal.current_value = goal.target_value
    db.session.commit()
    flash(f'🎉 Goal "{goal.title}" achieved! Well done!', 'success')
    return redirect(url_for('settings.goals'))
