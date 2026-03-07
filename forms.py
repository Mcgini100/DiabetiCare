from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
                     IntegerField, FloatField, SelectField, TextAreaField,
                     DateTimeLocalField, DateField, TimeField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


# ─── Auth Forms ──────────────────────────────────────────
class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    age = IntegerField('Age', validators=[Optional(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
    ], validators=[Optional()])
    diagnosis_year = IntegerField('Year of Diagnosis', validators=[Optional(), NumberRange(min=1950, max=2030)])
    diabetes_type = SelectField('Diabetes Type', choices=[
        ('Type 2', 'Type 2 Diabetes'), ('Type 1', 'Type 1 Diabetes'),
        ('Gestational', 'Gestational Diabetes'), ('Other', 'Other')
    ], validators=[Optional()])
    language = SelectField('Preferred Language', choices=[
        ('en', 'English'), ('sn', 'Shona'), ('nd', 'Ndebele')
    ], validators=[Optional()])
    submit = SubmitField('Save Profile')


class PreferencesForm(FlaskForm):
    reminder_medication = BooleanField('Medication Reminders')
    reminder_glucose = BooleanField('Blood Glucose Check Reminders')
    reminder_appointments = BooleanField('Appointment Reminders')
    receive_tips = BooleanField('Receive Tips & Education')
    submit = SubmitField('Save Preferences')


# ─── Glucose Form ────────────────────────────────────────
class GlucoseForm(FlaskForm):
    value = FloatField('Blood Glucose (mmol/L)', validators=[DataRequired(), NumberRange(min=0.5, max=40.0)])
    reading_time = DateTimeLocalField('Time of Reading', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    meal_context = SelectField('Meal Context', choices=[
        ('', 'Select Context'), ('before_breakfast', 'Before Breakfast'),
        ('after_breakfast', 'After Breakfast'), ('before_lunch', 'Before Lunch'),
        ('after_lunch', 'After Lunch'), ('before_dinner', 'Before Dinner'),
        ('after_dinner', 'After Dinner'), ('bedtime', 'Bedtime'),
        ('fasting', 'Fasting'), ('other', 'Other')
    ], validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Reading')


# ─── Medication Forms ────────────────────────────────────
class MedicationForm(FlaskForm):
    name = StringField('Medication Name', validators=[DataRequired(), Length(max=100)])
    dosage = StringField('Dosage (e.g. 500mg)', validators=[DataRequired(), Length(max=50)])
    frequency = SelectField('Frequency', choices=[
        ('once_daily', 'Once Daily'), ('twice_daily', 'Twice Daily'),
        ('three_daily', 'Three Times Daily'), ('as_needed', 'As Needed'),
        ('weekly', 'Weekly')
    ], validators=[DataRequired()])
    time_of_day = SelectField('Time of Day', choices=[
        ('morning', 'Morning'), ('afternoon', 'Afternoon'),
        ('evening', 'Evening'), ('night', 'Night')
    ], validators=[Optional()])
    side_effects = TextAreaField('Known Side Effects', validators=[Optional(), Length(max=500)])
    adverse_effects = TextAreaField('Adverse Effects', validators=[Optional(), Length(max=500)])
    instructions = TextAreaField('Special Instructions', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Medication')


# ─── Appointment Form ────────────────────────────────────
class AppointmentForm(FlaskForm):
    title = StringField('Appointment Title', validators=[DataRequired(), Length(max=100)])
    doctor_name = StringField('Doctor / Specialist Name', validators=[Optional(), Length(max=100)])
    appointment_type = SelectField('Type', choices=[
        ('checkup', 'Regular Checkup'), ('eye_exam', 'Eye Exam'),
        ('foot_exam', 'Foot Exam'), ('lab_test', 'Lab Test (HbA1c)'),
        ('dental', 'Dental'), ('specialist', 'Specialist Visit'),
        ('other', 'Other')
    ], validators=[Optional()])
    date_time = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Appointment')


# ─── Diet Form ───────────────────────────────────────────
class MealForm(FlaskForm):
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'), ('lunch', 'Lunch'),
        ('dinner', 'Dinner'), ('snack', 'Snack')
    ], validators=[DataRequired()])
    food_items = TextAreaField('Food Items', validators=[DataRequired(), Length(max=500)])
    carbs_grams = FloatField('Carbohydrates (g)', validators=[Optional(), NumberRange(min=0, max=500)])
    portion_size = SelectField('Portion Size', choices=[
        ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')
    ], validators=[Optional()])
    calories = IntegerField('Calories (approx)', validators=[Optional(), NumberRange(min=0, max=5000)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Meal')


# ─── Exercise Form ───────────────────────────────────────
class ExerciseForm(FlaskForm):
    activity_type = SelectField('Activity Type', choices=[
        ('walking', 'Walking'), ('jogging', 'Jogging'), ('running', 'Running'),
        ('cycling', 'Cycling'), ('swimming', 'Swimming'), ('yoga', 'Yoga'),
        ('strength', 'Strength Training'), ('dancing', 'Dancing'),
        ('gardening', 'Gardening'), ('other', 'Other')
    ], validators=[DataRequired()])
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1, max=600)])
    intensity = SelectField('Intensity', choices=[
        ('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')
    ], validators=[DataRequired()])
    calories_burned = IntegerField('Calories Burned (approx)', validators=[Optional(), NumberRange(min=0, max=5000)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Activity')


# ─── Complication Form ───────────────────────────────────
class ComplicationForm(FlaskForm):
    complication_type = SelectField('Type', choices=[
        ('hypoglycemia', 'Hypoglycemia (Low Blood Sugar)'),
        ('hyperglycemia', 'Hyperglycemia (High Blood Sugar)'),
        ('foot_ulcer', 'Foot Ulcer'), ('eye_issue', 'Eye/Vision Issue'),
        ('neuropathy', 'Neuropathy (Nerve Damage)'),
        ('kidney_issue', 'Kidney Issue'),
        ('hospitalization', 'Hospitalization'),
        ('infection', 'Infection'), ('other', 'Other')
    ], validators=[DataRequired()])
    severity = SelectField('Severity', choices=[
        ('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')
    ], validators=[DataRequired()])
    date_time = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    symptoms = TextAreaField('Symptoms', validators=[Optional(), Length(max=500)])
    action_taken = TextAreaField('Action Taken', validators=[Optional(), Length(max=500)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Event')


# ─── Community Forms ─────────────────────────────────────
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    body = TextAreaField('Content', validators=[DataRequired(), Length(max=5000)])
    category = SelectField('Category', choices=[
        ('general', 'General'), ('motivation', 'Motivation'),
        ('recipes', 'Recipes & Diet'), ('tips', 'Tips & Tricks'),
        ('questions', 'Questions'), ('success', 'Success Stories')
    ], validators=[Optional()])
    submit = SubmitField('Post')


class ReplyForm(FlaskForm):
    body = TextAreaField('Reply', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Reply')


# ─── Messaging Form ─────────────────────────────────────
class MessageForm(FlaskForm):
    recipient_email = StringField('To (Email)', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    body = TextAreaField('Message', validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField('Send')


# ─── Feedback Form ───────────────────────────────────────
class FeedbackForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Your Feedback', validators=[DataRequired(), Length(max=2000)])
    feedback_type = SelectField('Type', choices=[
        ('suggestion', 'Suggestion'), ('bug', 'Bug Report'), ('compliment', 'Compliment')
    ], validators=[Optional()])
    submit = SubmitField('Submit Feedback')


# ─── Goal Form ───────────────────────────────────────────
class GoalForm(FlaskForm):
    goal_type = SelectField('Goal Type', choices=[
        ('glucose', 'Blood Glucose'), ('exercise', 'Exercise'),
        ('weight', 'Weight'), ('medication', 'Medication Adherence'),
        ('diet', 'Healthy Eating')
    ], validators=[DataRequired()])
    title = StringField('Goal Title', validators=[DataRequired(), Length(max=120)])
    target_value = FloatField('Target Value', validators=[Optional()])
    unit = StringField('Unit (e.g. mmol/L, minutes, kg)', validators=[Optional(), Length(max=20)])
    deadline = DateField('Target Date', validators=[Optional()])
    submit = SubmitField('Set Goal')


# ─── Settings Form ──────────────────────────────────────
class SettingsForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    language = SelectField('Language', choices=[
        ('en', 'English'), ('sn', 'Shona'), ('nd', 'Ndebele')
    ], validators=[Optional()])
    font_size = SelectField('Font Size', choices=[
        ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')
    ], validators=[Optional()])
    high_contrast = BooleanField('High Contrast Mode')
    reminder_medication = BooleanField('Medication Reminders')
    reminder_glucose = BooleanField('Glucose Check Reminders')
    reminder_appointments = BooleanField('Appointment Reminders')
    receive_tips = BooleanField('Receive Tips')
    submit = SubmitField('Save Settings')
