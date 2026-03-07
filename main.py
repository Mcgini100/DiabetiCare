import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager, bcrypt, babel, migrate, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register Blueprints
    from views.auth import auth_bp
    from views.dashboard import dashboard_bp
    from views.glucose import glucose_bp
    from views.medication import medication_bp
    from views.appointments import appointments_bp
    from views.diet import diet_bp
    from views.activity import activity_bp
    from views.education import education_bp
    from views.assessment import assessment_bp
    from views.complications import complications_bp
    from views.community import community_bp
    from views.messaging import messaging_bp
    from views.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(glucose_bp, url_prefix='/glucose')
    app.register_blueprint(medication_bp, url_prefix='/medication')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(diet_bp, url_prefix='/diet')
    app.register_blueprint(activity_bp, url_prefix='/activity')
    app.register_blueprint(education_bp, url_prefix='/education')
    app.register_blueprint(assessment_bp, url_prefix='/assessment')
    app.register_blueprint(complications_bp, url_prefix='/complications')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(messaging_bp, url_prefix='/messaging')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('auth.welcome'))

    # Create database tables
    with app.app_context():
        import models  # noqa: F401
        db.create_all()
        seed_education_content()

    return app


def seed_education_content():
    """Seed initial education modules if none exist."""
    from models import EducationModule, Quiz
    if EducationModule.query.first() is not None:
        return

    modules = [
        {
            'title': 'Understanding Diabetes',
            'category': 'basics',
            'summary': 'Learn the fundamentals of diabetes, including types, causes, and how it affects your body.',
            'content': '''<h3>What is Diabetes?</h3>
<p>Diabetes is a chronic condition that affects how your body turns food into energy. When you eat, your body breaks down food into glucose (sugar) and releases it into your bloodstream.</p>

<h3>Types of Diabetes</h3>
<ul>
<li><strong>Type 1 Diabetes:</strong> Your body doesn't make insulin. This is usually diagnosed in children and young adults.</li>
<li><strong>Type 2 Diabetes:</strong> Your body doesn't use insulin well and can't keep blood sugar at normal levels. This is the most common type.</li>
<li><strong>Gestational Diabetes:</strong> Develops during pregnancy and usually goes away after the baby is born.</li>
</ul>

<h3>Why Blood Sugar Matters</h3>
<p>High blood sugar over time can lead to serious health problems including heart disease, vision loss, and kidney disease. Managing your blood sugar is the key to living well with diabetes.</p>

<h3>Key Numbers to Know</h3>
<ul>
<li>Normal fasting blood sugar: 4.0–5.5 mmol/L</li>
<li>Before meals: 4.0–7.0 mmol/L</li>
<li>2 hours after meals: less than 10.0 mmol/L</li>
<li>HbA1c target: below 7% (53 mmol/mol)</li>
</ul>''',
            'language': 'en',
            'order': 1,
            'quizzes': [
                {'question': 'What is the most common type of diabetes?', 'option_a': 'Type 1', 'option_b': 'Type 2', 'option_c': 'Gestational', 'option_d': 'Type 3', 'correct_answer': 'b', 'explanation': 'Type 2 diabetes is the most common form, accounting for about 90% of all diabetes cases.'},
                {'question': 'What is a normal fasting blood sugar range?', 'option_a': '2.0–3.0 mmol/L', 'option_b': '4.0–5.5 mmol/L', 'option_c': '8.0–10.0 mmol/L', 'option_d': '15.0–20.0 mmol/L', 'correct_answer': 'b', 'explanation': 'A normal fasting blood sugar level is between 4.0 and 5.5 mmol/L.'},
            ]
        },
        {
            'title': 'Healthy Eating with Diabetes',
            'category': 'diet',
            'summary': 'Practical guidance on meal planning, carbohydrate counting, and making healthy food choices.',
            'content': '''<h3>Eating Well with Diabetes</h3>
<p>Healthy eating is one of the most important tools for managing diabetes. It helps control blood sugar, blood pressure, and cholesterol levels.</p>

<h3>The Plate Method</h3>
<p>An easy way to plan meals:</p>
<ul>
<li><strong>Half your plate:</strong> Non-starchy vegetables (broccoli, spinach, tomatoes)</li>
<li><strong>Quarter of your plate:</strong> Lean protein (chicken, fish, beans)</li>
<li><strong>Quarter of your plate:</strong> Carbohydrate foods (brown rice, sadza, sweet potato)</li>
</ul>

<h3>Carbohydrate Counting</h3>
<p>Carbohydrates (carbs) have the biggest effect on blood sugar. Learning to count carbs helps you manage your glucose levels.</p>
<ul>
<li>1 serving of carbs ≈ 15g of carbohydrates</li>
<li>Most adults need 3–5 servings per meal</li>
<li>Choose whole grains over refined carbs</li>
</ul>

<h3>Local Food Tips</h3>
<ul>
<li><strong>Sadza:</strong> Choose small portions, pair with vegetables</li>
<li><strong>Fruits:</strong> Bananas, mangoes, oranges — eat in moderation</li>
<li><strong>Vegetables:</strong> Spinach (muriwo), pumpkin leaves, okra are excellent choices</li>
<li><strong>Proteins:</strong> Beans, lentils, kapenta, chicken — great options</li>
</ul>''',
            'language': 'en',
            'order': 2,
            'quizzes': [
                {'question': 'What should fill half your plate at meals?', 'option_a': 'Rice or sadza', 'option_b': 'Non-starchy vegetables', 'option_c': 'Meat', 'option_d': 'Fruit', 'correct_answer': 'b', 'explanation': 'The plate method recommends filling half your plate with non-starchy vegetables like broccoli, spinach, and tomatoes.'},
                {'question': 'How many grams of carbohydrates are in one serving?', 'option_a': '5 grams', 'option_b': '15 grams', 'option_c': '30 grams', 'option_d': '50 grams', 'correct_answer': 'b', 'explanation': 'One serving of carbohydrates equals approximately 15 grams.'},
            ]
        },
        {
            'title': 'Exercise and Diabetes',
            'category': 'exercise',
            'summary': 'How physical activity helps manage blood sugar and tips for getting started safely.',
            'content': '''<h3>Why Exercise Matters</h3>
<p>Regular physical activity helps your body use insulin better, lowers blood sugar, and improves overall health. Aim for at least 150 minutes of moderate activity per week.</p>

<h3>Benefits of Exercise</h3>
<ul>
<li>Lowers blood sugar levels</li>
<li>Helps with weight management</li>
<li>Reduces risk of heart disease</li>
<li>Improves mood and energy</li>
<li>Helps you sleep better</li>
</ul>

<h3>Safe Exercise Tips</h3>
<ul>
<li>Check blood sugar before and after exercise</li>
<li>Carry a fast-acting sugar source (glucose tablets, juice) in case of low blood sugar</li>
<li>Start slowly and gradually increase intensity</li>
<li>Stay hydrated — drink water before, during, and after exercise</li>
<li>Wear comfortable, supportive shoes to protect your feet</li>
</ul>

<h3>Suggested Activities</h3>
<ul>
<li><strong>Walking:</strong> 30 minutes daily — the easiest way to start</li>
<li><strong>Gardening / Yard Work:</strong> Great moderate activity</li>
<li><strong>Dancing:</strong> Fun and effective</li>
<li><strong>Swimming:</strong> Easy on joints</li>
<li><strong>Cycling:</strong> Excellent cardio exercise</li>
</ul>''',
            'language': 'en',
            'order': 3,
            'quizzes': [
                {'question': 'How many minutes of exercise per week is recommended?', 'option_a': '30 minutes', 'option_b': '60 minutes', 'option_c': '150 minutes', 'option_d': '300 minutes', 'correct_answer': 'c', 'explanation': 'The recommended amount is at least 150 minutes of moderate physical activity per week.'},
            ]
        },
        {
            'title': 'Foot Care for Diabetes',
            'category': 'foot_care',
            'summary': 'Essential foot care practices to prevent complications commonly associated with diabetes.',
            'content': '''<h3>Why Foot Care is Important</h3>
<p>Diabetes can reduce blood flow and cause nerve damage in your feet. This means you may not feel cuts, blisters, or sores. Without proper care, small problems can become serious infections.</p>

<h3>Daily Foot Care Routine</h3>
<ul>
<li><strong>Inspect your feet daily:</strong> Look for cuts, blisters, redness, swelling, or nail problems</li>
<li><strong>Wash your feet:</strong> Use warm (not hot) water and mild soap. Dry thoroughly, especially between toes</li>
<li><strong>Moisturize:</strong> Apply lotion to prevent cracking, but NOT between your toes</li>
<li><strong>Trim nails carefully:</strong> Cut straight across, file sharp edges</li>
<li><strong>Wear proper shoes:</strong> Supportive, well-fitting shoes. Never walk barefoot</li>
</ul>

<h3>Warning Signs — See Your Doctor If:</h3>
<ul>
<li>A cut or sore doesn't heal within a few days</li>
<li>You notice redness, warmth, or swelling</li>
<li>You see pus or drainage</li>
<li>You feel numbness, tingling, or burning</li>
<li>Your foot changes color or shape</li>
</ul>''',
            'language': 'en',
            'order': 4,
            'quizzes': [
                {'question': 'Where should you NOT apply moisturizer on your feet?', 'option_a': 'On the heels', 'option_b': 'Between the toes', 'option_c': 'On the soles', 'option_d': 'On the top of the foot', 'correct_answer': 'b', 'explanation': 'Moisture between the toes can promote fungal infections. Apply moisturizer everywhere else to prevent cracking.'},
            ]
        },
        {
            'title': 'Understanding Complications',
            'category': 'complications',
            'summary': 'Learn about potential diabetes complications and how to prevent or manage them.',
            'content': '''<h3>Diabetes Complications</h3>
<p>Over time, poorly managed diabetes can lead to various complications. The good news is that many can be prevented or delayed with proper management.</p>

<h3>Common Complications</h3>
<ul>
<li><strong>Hypoglycemia (Low Blood Sugar):</strong> Symptoms include shakiness, sweating, confusion, dizziness. Treat with fast-acting sugar immediately.</li>
<li><strong>Hyperglycemia (High Blood Sugar):</strong> Symptoms include excessive thirst, frequent urination, fatigue, blurred vision.</li>
<li><strong>Eye Problems (Retinopathy):</strong> Diabetes can damage blood vessels in the eyes. Get annual eye exams.</li>
<li><strong>Kidney Disease (Nephropathy):</strong> High blood sugar can damage kidneys over time. Regular lab tests can detect early signs.</li>
<li><strong>Nerve Damage (Neuropathy):</strong> Can cause tingling, numbness, or pain, especially in feet and hands.</li>
<li><strong>Heart Disease:</strong> People with diabetes are at higher risk. Manage blood pressure and cholesterol.</li>
</ul>

<h3>Emergency: What to Do for Hypoglycemia</h3>
<ol>
<li>Eat or drink 15g of fast-acting carbohydrate (3-4 glucose tablets, half a cup of juice, or 1 tablespoon of honey)</li>
<li>Wait 15 minutes and recheck blood sugar</li>
<li>If still low, repeat step 1</li>
<li>Once blood sugar is above 4.0 mmol/L, eat a snack or meal</li>
<li>If unconscious, call emergency services immediately</li>
</ol>''',
            'language': 'en',
            'order': 5,
            'quizzes': [
                {'question': 'What is the first step when experiencing hypoglycemia?', 'option_a': 'Take insulin', 'option_b': 'Eat 15g of fast-acting carbohydrate', 'option_c': 'Go to sleep', 'option_d': 'Exercise', 'correct_answer': 'b', 'explanation': 'The "15-15 rule": eat 15g of fast-acting carbs, wait 15 minutes, and recheck your blood sugar.'},
            ]
        },
    ]

    for mod_data in modules:
        quizzes_data = mod_data.pop('quizzes', [])
        module = EducationModule(**mod_data)
        db.session.add(module)
        db.session.flush()

        for q_data in quizzes_data:
            quiz = Quiz(module_id=module.id, **q_data)
            db.session.add(quiz)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
