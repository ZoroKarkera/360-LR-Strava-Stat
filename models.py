from database import db


class Athlete(db.Model):
    __tablename__ = "athletes"

    athlete_id = db.Column(db.Integer, primary_key=True)

    firstname = db.Column(db.String(100), nullable=False)

    lastname = db.Column(db.String(100), nullable=False)

    access_token = db.Column(db.Text)

    refresh_token = db.Column(db.Text)

    expires_at = db.Column(db.Integer)
