from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
from extensions import db
from models import Medication, MedicationLog
from forms import MedicationForm
from utils import format_frequency

medication_bp = Blueprint('medication', __name__)


@medication_bp.route('/')
@login_required
def list_medications():
    active_meds = Medication.query.filter_by(user_id=current_user.id, active=True).all()
    inactive_meds = Medication.query.filter_by(user_id=current_user.id, active=False).all()
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = MedicationLog.query.filter(
        MedicationLog.user_id == current_user.id,
        MedicationLog.taken_at >= today_start
    ).all()
    taken_ids = {log.medication_id for log in today_logs if log.taken}
    return render_template('medication/list.html', active_meds=active_meds,
                         inactive_meds=inactive_meds, taken_ids=taken_ids,
                         format_frequency=format_frequency)


@medication_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_medication():
    form = MedicationForm()
    if form.validate_on_submit():
        med = Medication(
            user_id=current_user.id,
            name=form.name.data,
            dosage=form.dosage.data,
            frequency=form.frequency.data,
            time_of_day=form.time_of_day.data,
            side_effects=form.side_effects.data,
            adverse_effects=form.adverse_effects.data,
            instructions=form.instructions.data
        )
        db.session.add(med)
        db.session.commit()
        flash(f'Medication "{med.name}" added!', 'success')
        return redirect(url_for('medication.list_medications'))
    return render_template('medication/add.html', form=form, editing=False)


@medication_bp.route('/edit/<int:med_id>', methods=['GET', 'POST'])
@login_required
def edit_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    if med.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('medication.list_medications'))
    form = MedicationForm(obj=med)
    if form.validate_on_submit():
        med.name = form.name.data
        med.dosage = form.dosage.data
        med.frequency = form.frequency.data
        med.time_of_day = form.time_of_day.data
        med.side_effects = form.side_effects.data
        med.adverse_effects = form.adverse_effects.data
        med.instructions = form.instructions.data
        db.session.commit()
        flash('Medication updated!', 'success')
        return redirect(url_for('medication.list_medications'))
    return render_template('medication/add.html', form=form, editing=True, med=med)


@medication_bp.route('/take/<int:medication_id>')
@login_required
def take_medication(medication_id):
    med = Medication.query.get_or_404(medication_id)
    if med.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('medication.list_medications'))
    log = MedicationLog(user_id=current_user.id, medication_id=medication_id, taken=True)
    db.session.add(log)
    db.session.commit()
    flash(f'✅ {med.name} marked as taken!', 'success')
    return redirect(url_for('medication.list_medications'))


@medication_bp.route('/toggle/<int:med_id>')
@login_required
def toggle_medication(med_id):
    med = Medication.query.get_or_404(med_id)
    if med.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('medication.list_medications'))
    med.active = not med.active
    db.session.commit()
    status = 'activated' if med.active else 'deactivated'
    flash(f'{med.name} {status}.', 'info')
    return redirect(url_for('medication.list_medications'))


@medication_bp.route('/history')
@login_required
def history():
    logs = MedicationLog.query.filter_by(user_id=current_user.id)\
        .order_by(MedicationLog.taken_at.desc()).limit(50).all()
    return render_template('medication/history.html', logs=logs)
