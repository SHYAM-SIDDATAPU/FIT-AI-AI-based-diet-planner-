from models.user import db
from datetime import datetime

class Workout(db.Model):
    __tablename__ = 'workouts'

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    sets     = db.Column(db.Integer, nullable=True)
    reps     = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)   # minutes
    goal     = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Workout {self.exercise}>'