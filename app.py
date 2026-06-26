from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from models.user import db, User
from models.meal import Meal
from models.workout import Workout
from models.progress import Progress
from datetime import date, datetime
import os

# ─────────────────────────────────────────────
#  App factory
# ─────────────────────────────────────────────
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ─── create tables & seed admin ───────────────
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@fitai.com').first():
            admin = User(name='Admin', email='admin@fitai.com', is_admin=True)
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()

    # ═══════════════════════════════════════
    #  HELPER – AI Rule-based Recommendations
    # ═══════════════════════════════════════
    def get_recommendations(user):
        recs = []
        bmi = user.bmi
        goal = user.goal or ''

        if bmi is None:
            return ['Complete your profile to get AI recommendations.']

        if bmi < 18.5:
            recs.append('Your BMI indicates you are <strong>Underweight</strong>. Consider a high-calorie diet.')
            recs.append('Focus on <strong>Strength Training</strong> to build muscle mass.')
        elif bmi < 25:
            recs.append('Your BMI is in the <strong>Normal</strong> range. Keep maintaining your healthy lifestyle!')
        elif bmi < 30:
            recs.append('Your BMI indicates you are <strong>Overweight</strong>. A calorie-deficit diet is recommended.')
            recs.append('Include <strong>Cardio workouts</strong> like running and cycling in your routine.')
        else:
            recs.append('Your BMI indicates <strong>Obesity</strong>. Consult a doctor and adopt a structured diet plan.')
            recs.append('Start with <strong>low-impact cardio</strong> such as walking and swimming.')

        if goal == 'muscle_gain':
            recs.append('Your goal is <strong>Muscle Gain</strong>. Ensure high protein intake (1.6–2.2 g/kg body weight).')
            recs.append('Follow a <strong>progressive overload</strong> strength training programme.')
        elif goal == 'weight_loss':
            recs.append('Maintain a calorie deficit of ~500 kcal/day for safe weight loss of 0.5 kg/week.')
        elif goal == 'weight_gain':
            recs.append('Eat in a calorie surplus with nutritious whole foods and limit junk food.')

        return recs

    # ═══════════════════════════════════════
    #  MEAL PLAN GENERATOR
    # ═══════════════════════════════════════
    MEAL_PLANS = {
        'weight_loss': {
            'breakfast': 'Oats with skimmed milk, 2 Boiled Eggs, 1 Apple, Green Tea',
            'lunch':     'Brown Rice (1 cup), Grilled Chicken Breast (150g), Mixed Salad, Lemon Water',
            'dinner':    'Vegetable Soup, Steamed Broccoli & Carrots, 1 small Multigrain Roti',
            'snacks':    'Handful of Almonds, 1 Orange, Buttermilk',
            'calories':  1600,
        },
        'weight_gain': {
            'breakfast': 'Whole-grain Toast (3 slices), Peanut Butter, Banana Smoothie (2 bananas + milk), Boiled Eggs (3)',
            'lunch':     'White Rice (2 cups), Chicken Curry, Paneer, Dal, Salad',
            'dinner':    'Pasta with Chicken, Garlic Bread, Mixed Vegetables, Curd',
            'snacks':    'Protein Shake, Cashews & Dates, Cheese Sandwich',
            'calories':  2800,
        },
        'muscle_gain': {
            'breakfast': 'Scrambled Eggs (4), Oats with Whey Protein, Whole-grain Toast, Banana',
            'lunch':     'Brown Rice (1.5 cups), Grilled Chicken (200g), Black Beans, Broccoli, Olive Oil Dressing',
            'dinner':    'Baked Salmon / Paneer Steak, Sweet Potato, Spinach Salad, Cottage Cheese',
            'snacks':    'Protein Bar, Greek Yoghurt with Berries, Hard-boiled Eggs',
            'calories':  2600,
        },
        'maintain': {
            'breakfast': 'Whole-grain Cereal with Milk, Mixed Fruit Bowl, 1 Boiled Egg, Black Coffee',
            'lunch':     'Chapati (2), Mixed Dal, Sabzi, Curd, Salad',
            'dinner':    'Grilled Fish / Tofu, Brown Rice (1 cup), Stir-fried Vegetables',
            'snacks':    'Fruit Salad, Roasted Chana, Herbal Tea',
            'calories':  2100,
        },
    }

    # ═══════════════════════════════════════
    #  WORKOUT PLAN GENERATOR
    # ═══════════════════════════════════════
    WORKOUT_PLANS = {
        'weight_loss': [
            {'exercise': 'Brisk Walking',     'sets': 1, 'reps': None, 'duration': 30},
            {'exercise': 'Running / Jogging', 'sets': 1, 'reps': None, 'duration': 20},
            {'exercise': 'Cycling',           'sets': 1, 'reps': None, 'duration': 20},
            {'exercise': 'Jump Rope (HIIT)',  'sets': 4, 'reps': None, 'duration': 5},
            {'exercise': 'Burpees',           'sets': 3, 'reps': 15,   'duration': None},
            {'exercise': 'Mountain Climbers', 'sets': 3, 'reps': 20,   'duration': None},
        ],
        'weight_gain': [
            {'exercise': 'Bench Press',       'sets': 4, 'reps': 10, 'duration': None},
            {'exercise': 'Deadlifts',         'sets': 4, 'reps': 8,  'duration': None},
            {'exercise': 'Squats',            'sets': 4, 'reps': 10, 'duration': None},
            {'exercise': 'Overhead Press',    'sets': 3, 'reps': 10, 'duration': None},
            {'exercise': 'Pull-Ups',          'sets': 3, 'reps': 8,  'duration': None},
            {'exercise': 'Dumbbell Rows',     'sets': 3, 'reps': 12, 'duration': None},
        ],
        'muscle_gain': [
            {'exercise': 'Push-Ups',          'sets': 4, 'reps': 15, 'duration': None},
            {'exercise': 'Pull-Ups',          'sets': 4, 'reps': 10, 'duration': None},
            {'exercise': 'Barbell Squats',    'sets': 4, 'reps': 10, 'duration': None},
            {'exercise': 'Bench Press',       'sets': 4, 'reps': 10, 'duration': None},
            {'exercise': 'Bicep Curls',       'sets': 3, 'reps': 12, 'duration': None},
            {'exercise': 'Tricep Dips',       'sets': 3, 'reps': 12, 'duration': None},
            {'exercise': 'Plank',             'sets': 3, 'reps': None,'duration': 1},
        ],
        'maintain': [
            {'exercise': 'Light Jog',         'sets': 1, 'reps': None, 'duration': 20},
            {'exercise': 'Yoga / Stretching', 'sets': 1, 'reps': None, 'duration': 20},
            {'exercise': 'Bodyweight Squats', 'sets': 3, 'reps': 15,   'duration': None},
            {'exercise': 'Push-Ups',          'sets': 3, 'reps': 12,   'duration': None},
            {'exercise': 'Swimming / Cycling','sets': 1, 'reps': None, 'duration': 25},
        ],
    }

    # ═══════════════════════════════════════
    #  ROUTES
    # ═══════════════════════════════════════
    @app.route('/')
    def home():
        return redirect(url_for('login'))
    # ── Landing ──────────────────────────────
    

    # ── Register ─────────────────────────────
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            name     = request.form.get('name', '').strip()
            email    = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm  = request.form.get('confirm_password', '')

            errors = []
            if not name:
                errors.append('Name is required.')
            if not email or '@' not in email:
                errors.append('Valid email is required.')
            if len(password) < 6:
                errors.append('Password must be at least 6 characters.')
            if password != confirm:
                errors.append('Passwords do not match.')
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered.')

            if errors:
                for e in errors:
                    flash(e, 'danger')
                return render_template('auth/register.html', name=name, email=email)

            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('auth/register.html')

    # ── Login ────────────────────────────────
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            email    = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = request.form.get('remember') == 'on'

            if not email or not password:
                flash('Email and password are required.', 'danger')
                return render_template('auth/login.html', email=email)

            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.name}!', 'success')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')

        return render_template('auth/login.html')

    # ── Logout ───────────────────────────────
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    # ── Dashboard ────────────────────────────
    @app.route('/dashboard')
    @login_required
    def dashboard():
        recs        = get_recommendations(current_user)
        today_prog  = Progress.query.filter_by(
            user_id=current_user.id, date=date.today()).first()
        meal_plan   = Meal.query.filter_by(
            user_id=current_user.id).order_by(Meal.created_at.desc()).first()
        workouts    = Workout.query.filter_by(
            user_id=current_user.id).order_by(Workout.created_at.desc()).limit(5).all()
        return render_template('dashboard/dashboard.html',
                               recs=recs,
                               today_prog=today_prog,
                               meal_plan=meal_plan,
                               workouts=workouts)

    # ── Profile ──────────────────────────────
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            errors = []
            name           = request.form.get('name', '').strip()
            age_raw        = request.form.get('age', '').strip()
            gender         = request.form.get('gender', '').strip()
            height_raw     = request.form.get('height', '').strip()
            weight_raw     = request.form.get('weight', '').strip()
            activity_level = request.form.get('activity_level', '').strip()
            goal           = request.form.get('goal', '').strip()

            if not name:            errors.append('Name is required.')
            if not age_raw:         errors.append('Age is required.')
            if not gender:          errors.append('Gender is required.')
            if not height_raw:      errors.append('Height is required.')
            if not weight_raw:      errors.append('Weight is required.')
            if not activity_level:  errors.append('Activity level is required.')
            if not goal:            errors.append('Goal is required.')

            try:
                age = int(age_raw)
                if not (10 <= age <= 120):
                    errors.append('Age must be between 10 and 120.')
            except (ValueError, TypeError):
                errors.append('Age must be a valid number.')
                age = None

            try:
                height = float(height_raw)
                if not (50 <= height <= 250):
                    errors.append('Height must be between 50 and 250 cm.')
            except (ValueError, TypeError):
                errors.append('Height must be a valid number.')
                height = None

            try:
                weight = float(weight_raw)
                if not (20 <= weight <= 300):
                    errors.append('Weight must be between 20 and 300 kg.')
            except (ValueError, TypeError):
                errors.append('Weight must be a valid number.')
                weight = None

            if errors:
                for e in errors:
                    flash(e, 'danger')
                return render_template('profile/profile.html')

            current_user.name           = name
            current_user.age            = age
            current_user.gender         = gender
            current_user.height         = height
            current_user.weight         = weight
            current_user.activity_level = activity_level
            current_user.goal           = goal
            db.session.commit()

            # Auto-generate plans if they don't exist
            _ensure_meal_plan(current_user, goal)
            _ensure_workout_plan(current_user, goal)

            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('profile/profile.html')

    # ── Diet Plan ────────────────────────────
    @app.route('/diet', methods=['GET', 'POST'])
    @login_required
    def diet_plan():
        if request.method == 'POST':
            goal = request.form.get('goal') or current_user.goal or 'maintain'
            plan_data = MEAL_PLANS.get(goal, MEAL_PLANS['maintain'])

            # Remove old plan and create new
            Meal.query.filter_by(user_id=current_user.id).delete()
            meal = Meal(
                user_id   = current_user.id,
                breakfast = plan_data['breakfast'],
                lunch     = plan_data['lunch'],
                dinner    = plan_data['dinner'],
                snacks    = plan_data['snacks'],
                calories  = plan_data['calories'],
                goal      = goal,
            )
            db.session.add(meal)
            db.session.commit()
            flash('Diet plan generated!', 'success')
            return redirect(url_for('diet_plan'))

        meal_plan = Meal.query.filter_by(
            user_id=current_user.id).order_by(Meal.created_at.desc()).first()
        return render_template('meals/diet_plan.html', meal_plan=meal_plan,
                               meal_plans=MEAL_PLANS)

    # ── Workout Plan ─────────────────────────
    @app.route('/workout', methods=['GET', 'POST'])
    @login_required
    def workout_plan():
        if request.method == 'POST':
            goal = request.form.get('goal') or current_user.goal or 'maintain'
            exercises = WORKOUT_PLANS.get(goal, WORKOUT_PLANS['maintain'])

            Workout.query.filter_by(user_id=current_user.id).delete()
            for ex in exercises:
                w = Workout(
                    user_id  = current_user.id,
                    exercise = ex['exercise'],
                    sets     = ex['sets'],
                    reps     = ex['reps'],
                    duration = ex['duration'],
                    goal     = goal,
                )
                db.session.add(w)
            db.session.commit()
            flash('Workout plan generated!', 'success')
            return redirect(url_for('workout_plan'))

        workouts = Workout.query.filter_by(
            user_id=current_user.id).order_by(Workout.id).all()
        return render_template('workouts/workout_plan.html',
                               workouts=workouts, workout_plans=WORKOUT_PLANS)

    # ── Progress ─────────────────────────────
    @app.route('/progress', methods=['GET', 'POST'])
    @login_required
    def progress():
        if request.method == 'POST':
            errors = []
            weight_raw = request.form.get('weight', '').strip()
            water_raw  = request.form.get('water', '').strip()
            workout_done = request.form.get('workout_done') == 'on'
            calories_raw = request.form.get('calories_consumed', '').strip()
            notes = request.form.get('notes', '').strip()
            date_raw = request.form.get('date', str(date.today())).strip()

            try:
                weight_val = float(weight_raw) if weight_raw else None
                if weight_val and not (20 <= weight_val <= 300):
                    errors.append('Weight must be between 20 and 300 kg.')
            except ValueError:
                errors.append('Weight must be a valid number.')
                weight_val = None

            try:
                water_val = float(water_raw) if water_raw else None
            except ValueError:
                errors.append('Water intake must be a valid number.')
                water_val = None

            try:
                cal_val = int(calories_raw) if calories_raw else None
            except ValueError:
                cal_val = None

            try:
                log_date = datetime.strptime(date_raw, '%Y-%m-%d').date()
            except ValueError:
                log_date = date.today()

            if errors:
                for e in errors:
                    flash(e, 'danger')
            else:
                existing = Progress.query.filter_by(
                    user_id=current_user.id, date=log_date).first()
                if existing:
                    existing.weight           = weight_val
                    existing.water            = water_val
                    existing.workout_done     = workout_done
                    existing.calories_consumed = cal_val
                    existing.notes            = notes
                else:
                    prog = Progress(
                        user_id          = current_user.id,
                        weight           = weight_val,
                        water            = water_val,
                        workout_done     = workout_done,
                        calories_consumed = cal_val,
                        notes            = notes,
                        date             = log_date,
                    )
                    db.session.add(prog)
                db.session.commit()
                flash('Progress logged successfully!', 'success')
                return redirect(url_for('progress'))

        history = Progress.query.filter_by(
            user_id=current_user.id).order_by(Progress.date.desc()).all()

        # Chart data
        chart_dates    = [str(p.date) for p in reversed(history)]
        chart_weights  = [p.weight  for p in reversed(history)]
        chart_bmis     = [p.bmi_at_date for p in reversed(history)]
        chart_calories = [p.calories_consumed for p in reversed(history)]

        return render_template('progress/progress.html',
                               history=history,
                               chart_dates=chart_dates,
                               chart_weights=chart_weights,
                               chart_bmis=chart_bmis,
                               chart_calories=chart_calories,
                               today=str(date.today()))

    # ── Admin ────────────────────────────────
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        users    = User.query.order_by(User.created_at.desc()).all()
        meals    = Meal.query.order_by(Meal.created_at.desc()).limit(20).all()
        workouts = Workout.query.order_by(Workout.created_at.desc()).limit(20).all()
        total_users = User.query.count()
        total_meals = Meal.query.count()
        total_workouts = Workout.query.count()
        return render_template('admin/admin_dashboard.html',
                               users=users, meals=meals, workouts=workouts,
                               total_users=total_users,
                               total_meals=total_meals,
                               total_workouts=total_workouts)

    @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    def admin_delete_user(user_id):
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            flash('Cannot delete admin account.', 'danger')
            return redirect(url_for('admin_dashboard'))
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.email} deleted.', 'success')
        return redirect(url_for('admin_dashboard'))

    # ── API: BMI calculator ───────────────────
    @app.route('/api/bmi')
    @login_required
    def api_bmi():
        try:
            h = float(request.args.get('height', 0))
            w = float(request.args.get('weight', 0))
            if h <= 0 or w <= 0:
                return jsonify({'error': 'Invalid values'}), 400
            h_m = h / 100
            bmi = round(w / (h_m * h_m), 1)
            if bmi < 18.5:   cat = 'Underweight'
            elif bmi < 25:   cat = 'Normal'
            elif bmi < 30:   cat = 'Overweight'
            else:             cat = 'Obese'
            return jsonify({'bmi': bmi, 'category': cat})
        except (ValueError, ZeroDivisionError):
            return jsonify({'error': 'Invalid values'}), 400

    # ─── helpers ─────────────────────────────
    def _ensure_meal_plan(user, goal):
        if not Meal.query.filter_by(user_id=user.id).first():
            plan_data = MEAL_PLANS.get(goal, MEAL_PLANS['maintain'])
            meal = Meal(user_id=user.id, goal=goal, **plan_data)
            db.session.add(meal)
            db.session.commit()

    def _ensure_workout_plan(user, goal):
        if not Workout.query.filter_by(user_id=user.id).first():
            for ex in WORKOUT_PLANS.get(goal, WORKOUT_PLANS['maintain']):
                w = Workout(user_id=user.id, goal=goal, **ex)
                db.session.add(w)
            db.session.commit()

    return app


# ─────────────────────────────────────────────
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)