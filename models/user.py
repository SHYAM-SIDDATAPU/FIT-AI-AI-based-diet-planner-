from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age           = db.Column(db.Integer, nullable=True)
    gender        = db.Column(db.String(10), nullable=True)
    height        = db.Column(db.Float, nullable=True)   # cm
    weight        = db.Column(db.Float, nullable=True)   # kg
    activity_level = db.Column(db.String(30), nullable=True)
    goal          = db.Column(db.String(30), nullable=True)
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    meals    = db.relationship('Meal',     backref='user', lazy=True, cascade='all, delete-orphan')
    workouts = db.relationship('Workout',  backref='user', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def bmi(self):
        if self.height and self.weight and self.height > 0:
            h_m = self.height / 100
            return round(self.weight / (h_m * h_m), 1)
        return None

    @property
    def bmi_category(self):
        b = self.bmi
        if b is None:
            return 'N/A'
        if b < 18.5:
            return 'Underweight'
        elif b < 25:
            return 'Normal'
        elif b < 30:
            return 'Overweight'
        else:
            return 'Obese'

    @property
    def daily_calories(self):
        """Harris-Benedict BMR + activity multiplier."""
        if not all([self.weight, self.height, self.age, self.gender]):
            return None
        if self.gender == 'Male':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)

        multipliers = {
            'sedentary': 1.2,
            'light':     1.375,
            'moderate':  1.55,
            'active':    1.725,
            'very_active': 1.9,
        }
        mult = multipliers.get(self.activity_level, 1.2)
        base = bmr * mult

        # Adjust by goal
        if self.goal == 'weight_loss':
            return int(base - 500)
        elif self.goal in ('weight_gain', 'muscle_gain'):
            return int(base + 500)
        else:
            return int(base)

    def profile_complete(self):
        return all([self.age, self.gender, self.height, self.weight, self.activity_level, self.goal])

    def __repr__(self):
        return f'<User {self.email}>'