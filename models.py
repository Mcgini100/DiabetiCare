from datetime import datetime, timezone
from extensions import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── User ───────────────────────────────────────────────
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    diagnosis_year = db.Column(db.Integer)
    diabetes_type = db.Column(db.String(30), default='Type 2')
    language = db.Column(db.String(5), default='en')
    font_size = db.Column(db.String(10), default='medium')
    high_contrast = db.Column(db.Boolean, default=False)
    reminder_medication = db.Column(db.Boolean, default=True)
    reminder_glucose = db.Column(db.Boolean, default=True)
    reminder_appointments = db.Column(db.Boolean, default=False)
    receive_tips = db.Column(db.Boolean, default=True)
    profile_complete = db.Column(db.Boolean, default=False)
    onboarding_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    glucose_readings = db.relationship('GlucoseReading', backref='user', lazy='dynamic')
    medications = db.relationship('Medication', backref='user', lazy='dynamic')
    medication_logs = db.relationship('MedicationLog', backref='user', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='user', lazy='dynamic')
    meals = db.relationship('Meal', backref='user', lazy='dynamic')
    exercises = db.relationship('Exercise', backref='user', lazy='dynamic')
    quiz_results = db.relationship('QuizResult', backref='user', lazy='dynamic')
    assessments = db.relationship('Assessment', backref='user', lazy='dynamic')
    complications = db.relationship('Complication', backref='user', lazy='dynamic')
    forum_posts = db.relationship('ForumPost', backref='author', lazy='dynamic')
    forum_replies = db.relationship('ForumReply', backref='author', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    goals = db.relationship('Goal', backref='user', lazy='dynamic')
    badges = db.relationship('Badge', backref='user', lazy='dynamic')
    feedbacks = db.relationship('Feedback', backref='user', lazy='dynamic')


# ─── Blood Glucose ──────────────────────────────────────
class GlucoseReading(db.Model):
    __tablename__ = 'glucose_readings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)  # mmol/L
    reading_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    meal_context = db.Column(db.String(30))  # before_breakfast, after_lunch, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def status(self):
        if self.value < 3.0:
            return 'critical-low'
        elif self.value < 4.0:
            return 'low'
        elif self.value <= 7.0:
            return 'normal'
        elif self.value <= 10.0:
            return 'high'
        elif self.value <= 13.9:
            return 'very-high'
        else:
            return 'critical-high'

    def status_label(self):
        labels = {
            'critical-low': 'Critical Low',
            'low': 'Low',
            'normal': 'Normal',
            'high': 'High',
            'very-high': 'Very High',
            'critical-high': 'Critical High'
        }
        return labels.get(self.status(), 'Unknown')

    def status_color(self):
        colors = {
            'critical-low': '#dc2626',
            'low': '#f59e0b',
            'normal': '#10b981',
            'high': '#f59e0b',
            'very-high': '#ef4444',
            'critical-high': '#dc2626'
        }
        return colors.get(self.status(), '#6b7280')


# ─── Medication ─────────────────────────────────────────
class Medication(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # morning, evening, twice_daily, etc.
    time_of_day = db.Column(db.String(20))  # morning, afternoon, evening, night
    side_effects = db.Column(db.Text)
    adverse_effects = db.Column(db.Text)
    instructions = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    logs = db.relationship('MedicationLog', backref='medication', lazy='dynamic')


class MedicationLog(db.Model):
    __tablename__ = 'medication_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    taken = db.Column(db.Boolean, default=True)
    taken_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text)


# ─── Appointments ───────────────────────────────────────
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100))
    appointment_type = db.Column(db.String(50))  # checkup, eye_exam, foot_exam, lab_test, etc.
    date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Diet / Nutrition ───────────────────────────────────
class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    food_items = db.Column(db.Text, nullable=False)
    carbs_grams = db.Column(db.Float)
    portion_size = db.Column(db.String(30))  # small, medium, large
    calories = db.Column(db.Integer)
    notes = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Physical Activity ─────────────────────────────────
class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # walking, jogging, cycling, etc.
    duration_minutes = db.Column(db.Integer, nullable=False)
    intensity = db.Column(db.String(20), nullable=False)  # low, moderate, high
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Education ──────────────────────────────────────────
class EducationModule(db.Model):
    __tablename__ = 'education_modules'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # basics, diet, exercise, complications, foot_care
    summary = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), default='en')
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    quizzes = db.relationship('Quiz', backref='module', lazy='dynamic')


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1), nullable=False)  # a, b, c, d
    explanation = db.Column(db.Text)


class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Self-Assessment ────────────────────────────────────
class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # knowledge, self_care, risk
    responses = db.Column(db.Text)  # JSON string of question-answer pairs
    score = db.Column(db.Integer)
    max_score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Complications ──────────────────────────────────────
class Complication(db.Model):
    __tablename__ = 'complications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complication_type = db.Column(db.String(50), nullable=False)  # hypoglycemia, foot_ulcer, eye_issue, etc.
    severity = db.Column(db.String(20), nullable=False)  # mild, moderate, severe
    date_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    symptoms = db.Column(db.Text)
    action_taken = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Community / Forums ─────────────────────────────────
class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # motivation, recipes, tips, questions
    pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    replies = db.relationship('ForumReply', backref='post', lazy='dynamic', cascade='all, delete-orphan')


class ForumReply(db.Model):
    __tablename__ = 'forum_replies'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Secure Messaging ───────────────────────────────────
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200))
    body = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    attachment_type = db.Column(db.String(30))  # glucose_log, medication_log, symptom, photo
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Goals & Badges ─────────────────────────────────────
class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # glucose, exercise, weight, medication
    title = db.Column(db.String(120), nullable=False)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))
    deadline = db.Column(db.DateTime)
    achieved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))  # emoji or icon name
    earned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─── Feedback ────────────────────────────────────────────
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    feedback_type = db.Column(db.String(30))  # bug, suggestion, compliment
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
