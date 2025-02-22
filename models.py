from config import db

class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.String(36), primary_key=True)  # Keeping id as primary key
    clerkid = db.Column(db.String(36), nullable=False, unique=True)  # Clerk ID remains unique
    email = db.Column(db.String(120), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    createdat = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updatedat = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    role = db.Column(db.String(20), nullable=False, default='PATIENT')

    user_details = db.relationship('UserDetails', back_populates='user', uselist=False, foreign_keys='UserDetails.clerkid')
    text_reports = db.relationship('TextReport', back_populates='user', foreign_keys='TextReport.clerkid')
    doctor_details = db.relationship('DoctorDetails', back_populates='user', uselist=False, foreign_keys='DoctorDetails.clerkid')
    routine = db.relationship('Routine', back_populates='user', uselist=False, foreign_keys='Routine.clerkid')

class UserDetails(db.Model):
    __tablename__ = 'user_details'

    id = db.Column(db.Integer, primary_key=True)
    clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  # Linking to User.clerkid
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)

    # Medical History
    blood_group = db.Column(db.String(10), nullable=False)
    known_allergies = db.Column(db.String(255), nullable=True)
    chronic_conditions = db.Column(db.String(255), nullable=True)
    previous_major_diseases = db.Column(db.String(255), nullable=True)
    previous_major_surgeries = db.Column(db.String(255), nullable=True)
    family_medical_history = db.Column(db.String(255), nullable=True)

    # Current Health Status
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=True)
    current_medication = db.Column(db.String(255), nullable=True)
    current_health_conditions = db.Column(db.String(255), nullable=True)
    vaccination_history = db.Column(db.String(255), nullable=True)

    # Emergency Info
    emergency_contact_name = db.Column(db.String(80), nullable=False)
    emergency_contact_phone = db.Column(db.String(20), nullable=False)
    emergency_contact_relationship = db.Column(db.String(50), nullable=False)

    # Lifestyle
    smoking_status = db.Column(db.String(50), nullable=False)
    alcohol_consumption = db.Column(db.String(50), nullable=False)
    exercise_frequency = db.Column(db.String(50), nullable=True)
    dietary_preferences = db.Column(db.String(100), nullable=True)

    # Insurance and Billing
    insurance_provider = db.Column(db.String(100), nullable=True)
    insurance_plan_number = db.Column(db.String(100), nullable=True)
    insurance_validity = db.Column(db.Date, nullable=True)

    # Mental Health
    mental_health_conditions = db.Column(db.String(255), nullable=True)

    # Relationship
    user = db.relationship('User', back_populates="user_details")


class TextReport(db.Model):
    __tablename__ = 'text_reports'

    id = db.Column(db.Integer, primary_key=True)
    clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  # Linking to User.clerkid
    file_url = db.Column(db.String(255), nullable=False)  # URL of the uploaded file
    summarized_text = db.Column(db.Text, nullable=False)  # Summarized text (AI processed)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates="text_reports")  # Relationship with User model

class DoctorDetails(db.Model):
    __tablename__ = 'doctor_details'

    id = db.Column(db.Integer, primary_key=True)
    clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    specialization = db.Column(db.String(100), nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100), nullable=True)
    clinic_address = db.Column(db.String(255), nullable=True)
    consultation_fee = db.Column(db.Float, nullable=False)
    available_days = db.Column(db.String(50), nullable=False)
    available_time = db.Column(db.String(50), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)

    user = db.relationship('User', back_populates='doctor_details')
    hospital = db.relationship('Hospital', back_populates='doctors')

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    doctor_clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  # Linking to Doctor's clerkid
    patient_clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  # Linking to Patient's clerkid
    prescription_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    prescription_text = db.Column(db.Text, nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)

    doctor = db.relationship('User', foreign_keys=[doctor_clerkid])
    patient = db.relationship('User', foreign_keys=[patient_clerkid])
    
class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    doctor_clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  
    patient_clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(15), nullable=False)
    text_field = db.Column(db.Text, nullable=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)

class Routine (db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(100), nullable=False)
    clerkid = db.Column(db.String(36), db.ForeignKey('User.clerkid'), nullable=False)  # Linking to User's clerkid
    routine = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='routine')  # Relationship with User model