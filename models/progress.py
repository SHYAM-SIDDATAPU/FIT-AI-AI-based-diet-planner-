from models.user import db
from datetime import datetime, date

class Progress(db.Model):
    __tablename__ = 'progress'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight           = db.Column(db.Float, nullable=True)
    water            = db.Column(db.Float, nullable=True)   # litres
    workout_done     = db.Column(db.Boolean, default=False)
    calories_consumed = db.Column(db.Integer, nullable=True)
    date             = db.Column(db.Date, default=date.today)
    notes            = db.Column(db.Text, nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def bmi_at_date(self):
        user = self.user
        if user and user.height and self.weight and user.height > 0:
            h_m = user.height / 100
            return round(self.weight / (h_m * h_m), 1)
        return None

    def __repr__(self):
        return f'<Progress user_id={self.user_id} date={self.date}>'