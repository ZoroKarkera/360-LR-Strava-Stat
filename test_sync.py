from flask import Flask

from config import Config
from database import db

from models import Athlete
from activity_sync import sync_recent_activities

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():

    athlete = Athlete.query.first()

    if athlete is None:
        print("No athlete found.")
        exit()

    sync_recent_activities(athlete)
