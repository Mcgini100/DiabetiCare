from datetime import datetime, timedelta, timezone
from io import BytesIO
import csv
import io


def glucose_color_code(value):
    """Return CSS class based on glucose value (mmol/L)."""
    if value < 3.0:
        return 'glucose-critical-low'
    elif value < 4.0:
        return 'glucose-low'
    elif value <= 7.0:
        return 'glucose-normal'
    elif value <= 10.0:
        return 'glucose-high'
    elif value <= 13.9:
        return 'glucose-very-high'
    else:
        return 'glucose-critical-high'


def glucose_status_text(value):
    """Return human-readable status for glucose value."""
    if value < 3.0:
        return 'Critical Low — Seek help immediately!'
    elif value < 4.0:
        return 'Low — Have a sugary snack'
    elif value <= 7.0:
        return 'Normal — Well done!'
    elif value <= 10.0:
        return 'High — Monitor closely'
    elif value <= 13.9:
        return 'Very High — Contact your doctor'
    else:
        return 'Critical High — Seek emergency help!'


def calculate_average(readings):
    """Calculate average from a list of GlucoseReading objects."""
    if not readings:
        return 0.0
    return round(sum(r.value for r in readings) / len(readings), 1)


def calculate_adherence(user, days=7):
    """Calculate medication adherence percentage for last N days."""
    from models import MedicationLog, Medication
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    active_meds = Medication.query.filter_by(user_id=user.id, active=True).count()
    if active_meds == 0:
        return 100
    expected = active_meds * days
    taken = MedicationLog.query.filter(
        MedicationLog.user_id == user.id,
        MedicationLog.taken == True,
        MedicationLog.taken_at >= start
    ).count()
    return min(round((taken / expected) * 100), 100) if expected > 0 else 100


def format_meal_context(context):
    """Convert meal_context slug to readable string."""
    mapping = {
        'before_breakfast': 'Before Breakfast',
        'after_breakfast': 'After Breakfast',
        'before_lunch': 'Before Lunch',
        'after_lunch': 'After Lunch',
        'before_dinner': 'Before Dinner',
        'after_dinner': 'After Dinner',
        'bedtime': 'Bedtime',
        'fasting': 'Fasting',
        'other': 'Other'
    }
    return mapping.get(context, context or '')


def format_frequency(frequency):
    """Convert frequency slug to readable string."""
    mapping = {
        'once_daily': 'Once Daily',
        'twice_daily': 'Twice Daily',
        'three_daily': 'Three Times Daily',
        'as_needed': 'As Needed',
        'weekly': 'Weekly'
    }
    return mapping.get(frequency, frequency or '')


def get_greeting():
    """Return greeting based on time of day."""
    hour = datetime.now().hour
    if hour < 12:
        return 'Good Morning'
    elif hour < 17:
        return 'Good Afternoon'
    else:
        return 'Good Evening'


def export_glucose_csv(readings):
    """Generate CSV string from glucose readings."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Time', 'Value (mmol/L)', 'Status', 'Meal Context', 'Notes'])
    for r in readings:
        writer.writerow([
            r.reading_time.strftime('%Y-%m-%d'),
            r.reading_time.strftime('%H:%M'),
            r.value,
            r.status_label(),
            format_meal_context(r.meal_context),
            r.notes or ''
        ])
    return output.getvalue()


def generate_pdf_report(user, readings, medications, period_label='Last 30 Days'):
    """Generate a PDF health report as bytes using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"DiabetiCare Health Report", styles['Title']))
    elements.append(Paragraph(f"Patient: {user.name}", styles['Normal']))
    elements.append(Paragraph(f"Period: {period_label}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Glucose summary
    if readings:
        avg = calculate_average(readings)
        high = max(r.value for r in readings)
        low = min(r.value for r in readings)
        elements.append(Paragraph("Blood Glucose Summary", styles['Heading2']))
        elements.append(Paragraph(f"Average: {avg} mmol/L  |  Highest: {high}  |  Lowest: {low}", styles['Normal']))
        elements.append(Spacer(1, 10))

        # Table of readings
        data = [['Date', 'Time', 'Value', 'Status', 'Context']]
        for r in readings[:50]:
            data.append([
                r.reading_time.strftime('%d/%m/%Y'),
                r.reading_time.strftime('%H:%M'),
                f"{r.value} mmol/L",
                r.status_label(),
                format_meal_context(r.meal_context)
            ])
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d9488')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    # Medications
    if medications:
        elements.append(Paragraph("Current Medications", styles['Heading2']))
        for m in medications:
            elements.append(Paragraph(f"• {m.name} — {m.dosage} ({format_frequency(m.frequency)})", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
