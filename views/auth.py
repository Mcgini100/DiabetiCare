from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User
from forms import RegistrationForm, LoginForm, ProfileForm, PreferencesForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        if current_user.onboarding_complete:
            return redirect(url_for('dashboard.index'))
        elif not current_user.profile_complete:
            return redirect(url_for('auth.profile_setup'))
    return render_template('onboarding/welcome.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash('Email already registered. Please sign in.', 'warning')
            return redirect(url_for('auth.login'))
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            password_hash=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Let\'s set up your profile.', 'success')
        return redirect(url_for('auth.profile_setup'))
    return render_template('onboarding/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not user.onboarding_complete:
                return redirect(url_for('auth.profile_setup'))
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('onboarding/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('auth.welcome'))


@auth_bp.route('/profile-setup', methods=['GET', 'POST'])
@login_required
def profile_setup():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.diagnosis_year = form.diagnosis_year.data
        current_user.diabetes_type = form.diabetes_type.data
        current_user.language = form.language.data
        current_user.profile_complete = True
        db.session.commit()
        flash('Profile saved!', 'success')
        return redirect(url_for('auth.preferences'))
    # Pre-fill form
    form.age.data = current_user.age
    form.gender.data = current_user.gender
    form.diagnosis_year.data = current_user.diagnosis_year
    form.diabetes_type.data = current_user.diabetes_type
    form.language.data = current_user.language
    return render_template('onboarding/profile_setup.html', form=form)


@auth_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    form = PreferencesForm()
    if form.validate_on_submit():
        current_user.reminder_medication = form.reminder_medication.data
        current_user.reminder_glucose = form.reminder_glucose.data
        current_user.reminder_appointments = form.reminder_appointments.data
        current_user.receive_tips = form.receive_tips.data
        db.session.commit()
        flash('Preferences saved!', 'success')
        return redirect(url_for('auth.tour'))
    form.reminder_medication.data = current_user.reminder_medication
    form.reminder_glucose.data = current_user.reminder_glucose
    form.reminder_appointments.data = current_user.reminder_appointments
    form.receive_tips.data = current_user.receive_tips
    return render_template('onboarding/preferences.html', form=form)


@auth_bp.route('/tour')
@login_required
def tour():
    return render_template('onboarding/tour.html')


@auth_bp.route('/complete-onboarding')
@login_required
def complete_onboarding():
    current_user.onboarding_complete = True
    db.session.commit()
    flash('Welcome to DiabetiCare! 🎉 Your journey starts here.', 'success')
    return redirect(url_for('dashboard.index'))
