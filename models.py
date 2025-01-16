from config import db

class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.String(36), primary_key=True)
    clerkid = db.Column(db.String(36), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    createdat = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Changed to createdat
    updatedat = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # Changed to updatedat
    role = db.Column(db.Enum('PATIENT', 'DOCTOR', name='role_enum'), nullable=False, default='PATIENT')

    user_details = db.relationship('UserDetails', back_populates='user', uselist=False)

class UserDetails(db.Model):
    __tablename__ = 'user_details'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('User.id'), nullable=False)  # Correct ForeignKey to reference 'User.id'
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
