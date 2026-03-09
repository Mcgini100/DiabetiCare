from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from extensions import db
from models import GlucoseReading
from forms import GlucoseForm
from utils import glucose_color_code, format_meal_context, calculate_average, export_glucose_csv
from ai_service import read_glucometer_image, is_ai_configured

glucose_bp = Blueprint('glucose', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@glucose_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    form = GlucoseForm()
    if form.validate_on_submit():
        reading = GlucoseReading(
            user_id=current_user.id,
            value=form.value.data,
            reading_time=form.reading_time.data or datetime.now(timezone.utc),
            meal_context=form.meal_context.data or None,
            notes=form.notes.data
        )
        db.session.add(reading)
        db.session.commit()

        # Check for alerts
        if reading.value < 3.0:
            flash('⚠️ CRITICAL LOW: Your blood sugar is dangerously low! Eat 15g of fast-acting carbs immediately.', 'danger')
        elif reading.value < 4.0:
            flash('⚠️ Low blood sugar. Consider having a snack.', 'warning')
        elif reading.value > 13.9:
            flash('⚠️ CRITICAL HIGH: Your blood sugar is very high. Contact your doctor.', 'danger')
        elif reading.value > 10.0:
            flash('⚠️ High blood sugar. Monitor closely.', 'warning')
        else:
            flash('✅ Reading saved! Your blood sugar is in a good range.', 'success')

        return redirect(url_for('glucose.trends'))

    # Recent readings
    recent = GlucoseReading.query.filter_by(user_id=current_user.id)\
        .order_by(GlucoseReading.reading_time.desc()).limit(5).all()

    return render_template('glucose/log.html', form=form, recent=recent,
                         glucose_color_code=glucose_color_code, format_meal_context=format_meal_context,
                         ai_enabled=is_ai_configured())


@glucose_bp.route('/scan', methods=['POST'])
@login_required
def scan_glucometer():
    """AI-powered glucometer reading from image."""
    if not is_ai_configured():
        return jsonify({'error': 'AI service not configured.'}), 503

    if 'meter_image' not in request.files:
        return jsonify({'error': 'No image uploaded.'}), 400

    file = request.files['meter_image']
    if not file or not _allowed_file(file.filename):
        return jsonify({'error': 'Invalid file. Use JPG, PNG, or WebP.'}), 400

    image_bytes = file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        return jsonify({'error': 'Image too large. Max 10MB.'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
    mime_type = mime_map.get(ext, 'image/jpeg')

    result = read_glucometer_image(image_bytes, mime_type)
    return jsonify(result)


@glucose_bp.route('/trends')
@login_required
def trends():
    period = request.args.get('period', '7')
    days = int(period) if period.isdigit() else 7
    since = datetime.now(timezone.utc) - timedelta(days=days)

    readings = GlucoseReading.query.filter(
        GlucoseReading.user_id == current_user.id,
        GlucoseReading.reading_time >= since
    ).order_by(GlucoseReading.reading_time.asc()).all()

    avg = calculate_average(readings)
    highest = max((r.value for r in readings), default=0)
    lowest = min((r.value for r in readings), default=0)

    chart_labels = [r.reading_time.strftime('%d/%m %H:%M') for r in readings]
    chart_values = [r.value for r in readings]

    # Sorted desc for table
    readings_desc = sorted(readings, key=lambda r: r.reading_time, reverse=True)

    return render_template('glucose/trends.html',
        readings=readings_desc, avg=avg, highest=highest, lowest=lowest,
        chart_labels=chart_labels, chart_values=chart_values,
        period=period, glucose_color_code=glucose_color_code,
        format_meal_context=format_meal_context)


@glucose_bp.route('/export')
@login_required
def export():
    readings = GlucoseReading.query.filter_by(user_id=current_user.id)\
        .order_by(GlucoseReading.reading_time.desc()).all()
    csv_data = export_glucose_csv(readings)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=glucose_readings.csv'}
    )


@glucose_bp.route('/delete/<int:reading_id>', methods=['POST'])
@login_required
def delete(reading_id):
    reading = GlucoseReading.query.get_or_404(reading_id)
    if reading.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('glucose.trends'))
    db.session.delete(reading)
    db.session.commit()
    flash('Reading deleted.', 'info')
    return redirect(url_for('glucose.trends'))
