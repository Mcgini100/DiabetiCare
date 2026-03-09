from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
import base64
import json
from extensions import db
from models import Meal
from forms import MealForm
from google import genai
from google.genai import types

diet_bp = Blueprint('diet', __name__)


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
    return render_template('diet/log.html', form=form, recent=recent)


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


@diet_bp.route('/api/analyze-food', methods=['POST'])
@login_required
def analyze_food():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400

        header, image_data = data['image'].split(',', 1)
        mime_type = header.split(';')[0].split(':')[1]
        decoded_image = base64.b64decode(image_data)
        
        client = genai.Client(api_key=current_app.config['GEMINI_API_KEY'])
        
        prompt = """
        Analyze this image of food. Return a JSON object (and only the JSON object, absolutely no markdown formatting) with the following structure:
        {
            "food_items": "Brief but descriptive name of the food visible (e.g. Sadza with beef stew and spinach)",
            "carbs_grams": integer (estimated total carbohydrates in grams),
            "calories": integer (estimated total calories),
            "portion_size": "medium" (choose exact string from: small, medium, large, extra-large)
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
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
