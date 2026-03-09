from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Meal
from forms import MealForm
from ai_service import analyze_food_image, is_ai_configured

diet_bp = Blueprint('diet', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@diet_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_meal():
    form = MealForm()
    if form.validate_on_submit():
        meal = Meal(user_id=current_user.id, meal_type=form.meal_type.data,
            food_items=form.food_items.data, carbs_grams=form.carbs_grams.data,
            portion_size=form.portion_size.data, calories=form.calories.data, notes=form.notes.data)
        db.session.add(meal)
        db.session.commit()
        flash('Meal logged!', 'success')
        return redirect(url_for('diet.history'))
    recent = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.logged_at.desc()).limit(5).all()
    return render_template('diet/log.html', form=form, recent=recent, ai_enabled=is_ai_configured())


@diet_bp.route('/scan', methods=['POST'])
@login_required
def scan_food():
    """AI-powered food image analysis endpoint."""
    if not is_ai_configured():
        return jsonify({'error': 'AI service not configured.'}), 503

    if 'food_image' not in request.files:
        return jsonify({'error': 'No image uploaded.'}), 400

    file = request.files['food_image']
    if not file or not _allowed_file(file.filename):
        return jsonify({'error': 'Invalid file. Use JPG, PNG, or WebP.'}), 400

    image_bytes = file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        return jsonify({'error': 'Image too large. Max 10MB.'}), 400

    # Determine MIME type
    ext = file.filename.rsplit('.', 1)[1].lower()
    mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
    mime_type = mime_map.get(ext, 'image/jpeg')

    result = analyze_food_image(image_bytes, mime_type)
    return jsonify(result)


@diet_bp.route('/log-from-scan', methods=['POST'])
@login_required
def log_from_scan():
    """Save a meal entry from AI analysis results."""
    data = request.form
    meal = Meal(
        user_id=current_user.id,
        meal_type=data.get('meal_type', 'snack'),
        food_items=data.get('food_items', ''),
        carbs_grams=float(data.get('carbs_grams', 0)) if data.get('carbs_grams') else None,
        protein_grams=float(data.get('protein_grams', 0)) if data.get('protein_grams') else None,
        fat_grams=float(data.get('fat_grams', 0)) if data.get('fat_grams') else None,
        fiber_grams=float(data.get('fiber_grams', 0)) if data.get('fiber_grams') else None,
        calories=int(data.get('calories', 0)) if data.get('calories') else None,
        portion_size=data.get('portion_size', 'medium'),
        notes=data.get('health_notes', ''),
        ai_analyzed=True
    )
    db.session.add(meal)
    db.session.commit()
    flash('🤖 AI-analyzed meal saved!', 'success')
    return redirect(url_for('diet.history'))


@diet_bp.route('/history')
@login_required
def history():
    meals = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.logged_at.desc()).limit(30).all()
    return render_template('diet/history.html', meals=meals)


@diet_bp.route('/delete/<int:meal_id>', methods=['POST'])
@login_required
def delete(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    if meal.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('diet.history'))
    db.session.delete(meal)
    db.session.commit()
    flash('Meal deleted.', 'info')
    return redirect(url_for('diet.history'))
