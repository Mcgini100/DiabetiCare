from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
from extensions import db
from models import Appointment
from forms import AppointmentForm

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/')
@login_required
def list_appointments():
    now = datetime.now(timezone.utc)
    upcoming = Appointment.query.filter(
        Appointment.user_id == current_user.id,
        Appointment.date_time >= now, Appointment.completed == False
    ).order_by(Appointment.date_time.asc()).all()
    past = Appointment.query.filter(
        Appointment.user_id == current_user.id,
        (Appointment.date_time < now) | (Appointment.completed == True)
    ).order_by(Appointment.date_time.desc()).limit(20).all()
    return render_template('appointments/list.html', upcoming=upcoming, past=past)


@appointments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        appt = Appointment(user_id=current_user.id, title=form.title.data,
            doctor_name=form.doctor_name.data, appointment_type=form.appointment_type.data,
            date_time=form.date_time.data, location=form.location.data, notes=form.notes.data)
        db.session.add(appt)
        db.session.commit()
        flash('Appointment scheduled!', 'success')
        return redirect(url_for('appointments.list_appointments'))
    return render_template('appointments/add.html', form=form)


@appointments_bp.route('/complete/<int:appt_id>')
@login_required
def complete(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    appt.completed = True
    db.session.commit()
    flash('Appointment marked as completed.', 'success')
    return redirect(url_for('appointments.list_appointments'))


@appointments_bp.route('/delete/<int:appt_id>', methods=['POST'])
@login_required
def delete(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted.', 'info')
    return redirect(url_for('appointments.list_appointments'))
