from flask import Flask

from config import Config
from database import db

from statistics import (
    get_summary,
    get_leaderboard,
    get_recent_runs,
    get_heatmap,
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():

    print(get_summary())

    print()

    print(get_leaderboard())

    print()

    print(get_recent_runs())

    print()

    print(get_heatmap())
