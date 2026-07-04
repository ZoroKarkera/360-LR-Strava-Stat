from flask import Flask
from database import db
from config import Config
import models

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database created successfully!")
