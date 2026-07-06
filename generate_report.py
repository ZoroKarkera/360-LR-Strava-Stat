from flask import Flask

from config import Config
from database import db
from dashboard import generate_dashboard
from excel_report import generate_excel


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    generate_excel()
    generate_dashboard()
