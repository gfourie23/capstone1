import json
import os
import requests
import psycopg2

from flask import Flask, redirect, render_template, session, url_for, request, flash, abort, jsonify
#from flask_wtf import FlaskForm
#from flask_debugtoolbar import DebugToolbarExtension
#from flask_oauthlib.client import OAuth
#from werkzeug.utils import url_quote
from urllib.parse import quote
import openai
from authlib.integrations.flask_client import OAuth
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
from openai import OpenAI

from models import db, connect_db, Patient
from forms import NewPatientForm, PatientEditForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///schedule_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.app_context().push()

client = OpenAI()
login_manager = LoginManager()
login_manager.init_app(app)

connect_db(app)

db.create_all()

app.config.from_pyfile('config.py')
GOOGLE_CLIENT_ID = app.config['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = app.config['GOOGLE_CLIENT_SECRET']
OAUTH2_META_URL = ("https://accounts.google.com/.well-known/openid-configuration")
SECRET_KEY = app.config['SECRET_KEY']


openai.api_key = app.config['OPENAI_API_KEY']

oauth = OAuth(app)

oauth.register("Scheduler", 
               client_id=app.config["GOOGLE_CLIENT_ID"],
               client_secret=app.config["GOOGLE_CLIENT_SECRET"],
               server_metadata_url=OAUTH2_META_URL,
               authorize_url='https://accounts.google.com/o/oauth2/auth',
               redirect_uri='http://127.0.0.1:5000/calendar',
               client_kwargs={
                   "scope": "openid profile email https://www.googleapis.com/auth/calendar.events"
               })


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()



@app.route("/")
def home():
    return render_template('signin.html', session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4))
                           

@app.route("/google-login")
def googleLogin():
    """User login."""
    return oauth.Scheduler.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True))

@app.route("/signin-google")
def googleCallback():
    token = oauth.Scheduler.authorize_access_token()
    session["user"] = token
    return redirect ('/calendar')

@app.route("/logout")
def logout():
    """User logout."""
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route('/calendar', methods=["GET"])
def show_cal():
    """Show calendar."""
    return render_template('homepage.html')



@app.route('/pt-list', methods=["GET"])
def show_pt_list():
    #Show the list of patients
    patients = Patient.query.all()
    return render_template('pt-list.html', patients=patients)

@app.route('/add-pt', methods=["GET", "POST"])
def add_pt_form():
    """Add new patient information to database."""
    form = NewPatientForm()

    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        city = form.city.data
        frequency = form.frequency.data
        timeframe_start = form.timeframe_start.data
        timeframe_end = form.timeframe_end.data

        new_patient = Patient(name=name, address=address, city=city, frequency=frequency, timeframe_start=timeframe_start, timeframe_end=timeframe_end)

        db.session.add(new_patient)
        db.session.commit()

        #flash(f"Added {name} to patient list.")
        return redirect("/pt-list")

    else:
        return render_template("add-pt.html", form=form)
    

@app.route('/edit-pt/<int:patient_id>', methods=["GET", "POST"])
def edit_pt_form(patient_id):
    """Edit existing patient information."""
    
    patient = Patient.query.get(patient_id)
    form = PatientEditForm(obj=patient)

    if not patient:
        abort(404)
    
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.address = form.address.data
        patient.city = form.city.data
        patient.frequency = form.frequency.data
        patient.timeframe_start = form.timeframe_start.data
        patient.timeframe_end = form.timeframe_end.data
        patient.preferred_days = form.preferred_days.data
        patient.preferred_times = form.preferred_times.data
      
        db.session.add(patient)
        db.session.commit()

        flash(f"{patient.name} has been updated.")
        return redirect("/pt-list")

    return render_template("edit-pt.html", form=form, patient=patient)
    

@app.route('/pt-list/<int:patient_id>/delete', methods=["POST"])
def delete_pt(patient_id):
    """Delete a patient from patient list."""

    patient = Patient.query.get(patient_id)
    print(patient)

    if not patient:
        abort(404)

    try: 
        db.session.delete(patient)
        db.session.commit()
        flash(f"{patient.name} has been deleted successfully.")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting patient: {str(e)}, 'error")

    return redirect(url_for("show_pt_list"))



if __name__ == '__main__':
        app.run(debug=True)