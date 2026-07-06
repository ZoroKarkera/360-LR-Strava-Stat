from database import db


class Athlete(db.Model):
    __tablename__ = "athletes"

    athlete_id = db.Column(db.Integer, primary_key=True)

    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)

    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)

    expires_at = db.Column(db.Integer)


class Activity(db.Model):
    __tablename__ = "activities"

    activity_id = db.Column(db.BigInteger, primary_key=True)

    athlete_id = db.Column(
        db.Integer,
        db.ForeignKey("athletes.athlete_id"),
        nullable=False,
    )

    name = db.Column(db.String(255))
    activity_type = db.Column(db.String(30))

    start_date = db.Column(db.DateTime)
    timezone = db.Column(db.String(100))

    distance = db.Column(db.Float)

    moving_time = db.Column(db.Integer)
    elapsed_time = db.Column(db.Integer)

    total_elevation_gain = db.Column(db.Float)

    average_speed = db.Column(db.Float)
    max_speed = db.Column(db.Float)

    average_heartrate = db.Column(db.Float)
    max_heartrate = db.Column(db.Float)

    average_cadence = db.Column(db.Float)

    average_watts = db.Column(db.Float)
    max_watts = db.Column(db.Float)

    kilojoules = db.Column(db.Float)

    trainer = db.Column(db.Boolean)
    commute = db.Column(db.Boolean)
