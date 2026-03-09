from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
import base64
import json
from extensions import db
from models import GlucoseReading
from forms import GlucoseForm
from utils import glucose_color_code, format_meal_context, calculate_average, export_glucose_csv
from google import genai
from google.genai import types

glucose_bp = Blueprint('glucose', __name__)


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
                         glucose_color_code=glucose_color_code, format_meal_context=format_meal_context)


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


@glucose_bp.route('/api/read-glucometer', methods=['POST'])
@login_required
def read_glucometer():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400

        header, image_data = data['image'].split(',', 1)
        mime_type = header.split(';')[0].split(':')[1]
        decoded_image = base64.b64decode(image_data)
        
        client = genai.Client(api_key=current_app.config['GEMINI_API_KEY'])
        
        prompt = """
        Analyze this image of a glucometer screen. Extract the blood glucose reading shown.
        Return a JSON object (and only the JSON object, absolutely no markdown formatting) with the following structure:
        {
            "glucose_value": float (the reading extracted, e.g. 5.6 or 105),
            "unit": "string" (either "mmol/L" or "mg/dL" if visible, otherwise null)
        }
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, types.Part.from_bytes(data=decoded_image, mime_type=mime_type)]
        )
        
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
            
        result = json.loads(text)
        
        # If the reading is in mg/dL, convert to mmol/L for the app
        if result.get('unit') == 'mg/dL' and result.get('glucose_value'):
            result['glucose_value'] = round(result['glucose_value'] / 18.0, 1)
            result['unit'] = 'mmol/L'
            
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
