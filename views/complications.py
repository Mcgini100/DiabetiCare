from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Complication
from forms import ComplicationForm

complications_bp = Blueprint('complications', __name__)

EMERGENCY_GUIDANCE = {
    'hypoglycemia': {'title': 'Hypoglycemia (Low Blood Sugar)', 'icon': '⚡',
        'steps': ['Eat 15g of fast-acting carbs (3-4 glucose tablets, ½ cup juice, or 1 tbsp honey)',
                  'Wait 15 minutes and recheck blood sugar', 'If still low, repeat step 1',
                  'Once above 4.0 mmol/L, eat a snack or meal', 'If unconscious, call emergency services immediately']},
    'hyperglycemia': {'title': 'Hyperglycemia (High Blood Sugar)', 'icon': '📈',
        'steps': ['Drink plenty of water', 'Check for ketones if blood sugar is above 13.9 mmol/L',
                  'Take medication as prescribed', 'If symptoms worsen (nausea, vomiting, confusion), seek medical help',
                  'Contact your healthcare provider for guidance']},
    'foot_ulcer': {'title': 'Foot Ulcer', 'icon': '🦶',
        'steps': ['Clean the wound gently with mild soap and water', 'Apply a clean bandage',
                  'Do NOT walk barefoot', 'See your doctor as soon as possible',
                  'Watch for signs of infection (redness, warmth, pus, worsening pain)']},
}


@complications_bp.route('/', methods=['GET', 'POST'])
@login_required
def log_complication():
    form = ComplicationForm()
    if form.validate_on_submit():
        comp = Complication(user_id=current_user.id, complication_type=form.complication_type.data,
            severity=form.severity.data, date_time=form.date_time.data, symptoms=form.symptoms.data,
            action_taken=form.action_taken.data, notes=form.notes.data)
        db.session.add(comp)
        db.session.commit()
        flash('Event logged. Please review emergency guidance if needed.', 'warning')
        return redirect(url_for('complications.history'))

    history = Complication.query.filter_by(user_id=current_user.id).order_by(Complication.date_time.desc()).limit(10).all()
    return render_template('complications/log.html', form=form, history=history, guidance=EMERGENCY_GUIDANCE)


@complications_bp.route('/history')
@login_required
def history():
    events = Complication.query.filter_by(user_id=current_user.id).order_by(Complication.date_time.desc()).all()
    return render_template('complications/history.html', events=events, guidance=EMERGENCY_GUIDANCE)
