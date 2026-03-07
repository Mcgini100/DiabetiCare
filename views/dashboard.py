from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from models import GlucoseReading, Medication, MedicationLog, Appointment, Exercise, Goal, Badge
from utils import calculate_average, calculate_adherence, get_greeting, glucose_color_code

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # Latest glucose reading
    latest_glucose = GlucoseReading.query.filter_by(user_id=current_user.id)\
        .order_by(GlucoseReading.reading_time.desc()).first()

    # Today's readings
    today_readings = GlucoseReading.query.filter(
        GlucoseReading.user_id == current_user.id,
        GlucoseReading.reading_time >= today_start
    ).order_by(GlucoseReading.reading_time.desc()).all()

    # Last 7 days readings for chart
    week_readings = GlucoseReading.query.filter(
        GlucoseReading.user_id == current_user.id,
        GlucoseReading.reading_time >= week_ago
    ).order_by(GlucoseReading.reading_time.asc()).all()

    # Medication status
    active_meds = Medication.query.filter_by(user_id=current_user.id, active=True).all()
    today_med_logs = MedicationLog.query.filter(
        MedicationLog.user_id == current_user.id,
        MedicationLog.taken_at >= today_start
    ).all()
    taken_med_ids = {log.medication_id for log in today_med_logs if log.taken}

    # Upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.user_id == current_user.id,
        Appointment.date_time >= now,
        Appointment.completed == False
    ).order_by(Appointment.date_time.asc()).limit(3).all()

    # Exercise this week
    week_exercises = Exercise.query.filter(
        Exercise.user_id == current_user.id,
        Exercise.logged_at >= week_ago
    ).all()
    weekly_exercise_mins = sum(e.duration_minutes for e in week_exercises)

    # Averages
    week_avg = calculate_average(week_readings)
    today_avg = calculate_average(today_readings)

    # Adherence
    adherence = calculate_adherence(current_user, days=7)

    # Goals
    active_goals = Goal.query.filter_by(user_id=current_user.id, achieved=False).limit(3).all()

    # Recent badges
    recent_badges = Badge.query.filter_by(user_id=current_user.id)\
        .order_by(Badge.earned_at.desc()).limit(3).all()

    # Chart data for glucose trends
    chart_labels = [r.reading_time.strftime('%d/%m %H:%M') for r in week_readings]
    chart_values = [r.value for r in week_readings]

    return render_template('dashboard/index.html',
        greeting=get_greeting(),
        latest_glucose=latest_glucose,
        today_readings=today_readings,
        today_avg=today_avg,
        week_avg=week_avg,
        active_meds=active_meds,
        taken_med_ids=taken_med_ids,
        upcoming_appointments=upcoming_appointments,
        weekly_exercise_mins=weekly_exercise_mins,
        adherence=adherence,
        active_goals=active_goals,
        recent_badges=recent_badges,
        chart_labels=chart_labels,
        chart_values=chart_values,
        glucose_color_code=glucose_color_code
    )
