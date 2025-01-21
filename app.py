from flask import Flask
from flask_cors import CORS
from flask_apscheduler import APScheduler
from config import configure_app, db
from blueprints.auth.auth_bp import auth_bp
from blueprints.user.user_bp import user_bp
from blueprints.ai.ai_bp import ai_bp
from blueprints.meeting.meeting_bp import meeting_bp
from blueprints.doctor.doctor_bp import doctor_bp
from blueprints.prescription.prescription_bp import prescription_bp
from blueprints.appointment.appointment_bp import appointment_bp
from models import Appointment
from datetime import datetime

app = Flask(__name__)
configure_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(meeting_bp, url_prefix='/meeting')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(prescription_bp, url_prefix='/prescription')
app.register_blueprint(appointment_bp, url_prefix='/appointment')

# APScheduler setup
scheduler = APScheduler()

def update_expired_appointments():
    now = datetime.now()
    expired_appointments = Appointment.query.filter(Appointment.appointment_date < now, Appointment.status != 'completed', Appointment.status != 'expired').all()
    for appointment in expired_appointments:
        appointment.status = 'expired'
    db.session.commit()

with app.app_context():
    db.create_all()
    scheduler.add_job(id='update_expired_appointments', func=update_expired_appointments, trigger='interval', minutes=45)
    scheduler.init_app(app)
    scheduler.start()

# Default Route
@app.route('/')
def hello():
    return "Hello World! Let's Get Started With This Then, Shall We?"

if __name__ == "__main__":
    app.run(debug=True)
