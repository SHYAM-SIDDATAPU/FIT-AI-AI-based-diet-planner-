from models.user import db
from datetime import datetime

class Meal(db.Model):
    __tablename__ = 'meals'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    breakfast = db.Column(db.Text, nullable=True)
    lunch     = db.Column(db.Text, nullable=True)
    dinner    = db.Column(db.Text, nullable=True)
    snacks    = db.Column(db.Text, nullable=True)
    calories  = db.Column(db.Integer, nullable=True)
    goal      = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Meal user_id={self.user_id} cal={self.calories}>'