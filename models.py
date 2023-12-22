from datetime import datetime

#from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

#bcrypt = Bcrypt()
db = SQLAlchemy()

class Patient(db.Model):
    """Model for patients"""

    __tablename__ = "patients"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    name = db.Column(
        db.Text, 
        nullable=False,
    )
    address = db.Column(
        db.Text,
        nullable=False
    )
    city = db.Column(
        db.Text,
        nullable=False
    )
    frequency = db.Column(
        db.Integer,
        nullable=False
    )
    timeframe_start = db.Column(
        db.Text,
        nullable=False
    )
    timeframe_end = db.Column(
        db.Text, 
        nullable=False
    )
    preferred_days = db.Column(
        db.Text,
    )
    preferred_times = db.Column(
        db.Text,
    )


def connect_db(app):
    """Connect this database to Flask app.
    """

    db.app = app
    db.init_app(app)

