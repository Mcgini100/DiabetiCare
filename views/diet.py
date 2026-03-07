from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Meal
from forms import MealForm

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
