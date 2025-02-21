from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from models import User, UserDetails, DoctorDetails
from blueprints.hospital.models import Hospital # Import Hospital model
from datetime import datetime

doctor_bp = Blueprint('doctor_bp', __name__)

# Function to handle date conversion
def convert_to_date(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")
    return None

# Route to change the role of an existing user to DOCTOR
@doctor_bp.route('/create-doctor/<clerkid>', methods=['PATCH'])
@swag_from({
    'summary': 'Change the role of an existing user to DOCTOR, only for admin control not needed by the frontend',
    'tags': ['Doctor'],
    'responses': {
        200: {
            'description': 'User role updated to DOCTOR successfully',
            'examples': {'application/json': {'message': 'User role updated to DOCTOR successfully'}}
        },
        400: {
            'description': 'User not found',
            'examples': {'application/json': {'error': 'User not found'}}
        }
    }
})
def create_doctor(clerkid):
    user = User.query.filter_by(clerkid=clerkid).first()
    if not user:
        return jsonify({"error": "User not found"}), 400

    user.role = 'DOCTOR'
    db.session.commit()

    return jsonify({"message": "User role updated to DOCTOR successfully"}), 200

# Route for doctor to post their details
@doctor_bp.route('/post-details', methods=['POST'])
@swag_from({
    'summary': 'Allows a doctor to enter their details',
    'tags': ['Doctor Details'],
    'responses': {
        201: {
            'description': 'Doctor details created successfully',
            'examples': {'application/json': {'message': 'Doctor details created successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'User not found'}}
        }
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'clerkid': {'type': 'string'},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'address': {'type': 'string'},
                    'years_of_experience': {'type': 'integer'},
                    'specialization': {'type': 'string'},
                    'department': {'type': 'string'},
                    'clinic_address': {'type': 'string'},
                    'consultation_fee': {'type': 'number'},
                    'available_days': {'type': 'string'},
                    'available_time': {'type': 'string'},
                    'hospital_id': {'type': 'integer'}  
                },
                'required': [
                    'clerkid', 'first_name', 'last_name', 'email', 'phone_number', 'address',
                    'years_of_experience', 'specialization', 'department', 'consultation_fee',
                    'available_days', 'available_time'
                ]
            }
        }
    ]
})
def post_doctor_details():
    data = request.json

    clerkid = data.get('clerkid')
    user = User.query.filter_by(clerkid=clerkid).first()
    if not user or user.role != 'DOCTOR':
        return jsonify({"error": "User not found or not a doctor"}), 400

    doctor_details = DoctorDetails(
        clerkid=user.clerkid,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        address=data.get('address'),
        years_of_experience=data.get('years_of_experience'),
        specialization=data.get('specialization'),
        department=data.get('department'),
        clinic_address=data.get('clinic_address'),
        consultation_fee=data.get('consultation_fee'),
        available_days=data.get('available_days'),
        available_time=data.get('available_time'),
        hospital_id=data.get('hospital_id')  # Include hospital_id
    )

    db.session.add(doctor_details)
    db.session.commit()

    return jsonify({"message": "Doctor details created successfully"}), 201

# Route to get doctor details by clerkid
@doctor_bp.route('/get-details/<clerkid>', methods=['GET'])
@swag_from({
    'summary': 'Fetches the Doctor Details by ClerkID',
    'tags': ['Doctor Details'],
    'parameters': [
        {
            'name': 'clerkid',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ClerkID of the doctor'
        }
    ],
    'responses': {
        200: {
            'description': 'Doctor details fetched successfully',
            'examples': {
                'application/json': {
                    'clerkid': '1234',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone_number': '9876543210',
                    'email': 'john.doe@example.com',
                    'address': '123 Main St, Springfield, IL',
                    'years_of_experience': 10,
                    'specialization': 'Cardiology',
                    'department': 'Cardiology',
                    'clinic_address': '456 Clinic St, Springfield, IL',
                    'consultation_fee': 100,
                    'available_days': 'Mon-Fri',
                    'available_time': '09:00-17:00',
                    'hospital_id': 1,  # Added hospital_id
                    'hospital_name': 'General Hospital'  # Added hospital_name
                }
            }
        },
        400: {
            'description': 'Doctor not found',
            'examples': {'application/json': {'error': 'Doctor not found'}}
        }
    }
})
def get_doctor_details(clerkid):
    user = User.query.filter_by(clerkid=clerkid).first()
    if not user or user.role != 'DOCTOR':
        return jsonify({"error": "Doctor not found"}), 400

    # Join DoctorDetails and Hospital tables to fetch hospital name
    doctor_details = (
        db.session.query(DoctorDetails, Hospital.name)
        .join(Hospital, DoctorDetails.hospital_id == Hospital.id, isouter=True)
        .filter(DoctorDetails.clerkid == user.clerkid)
        .first()
    )

    if not doctor_details:
        return jsonify({"error": "Doctor details not found"}), 400

    # Unpack the result
    doctor, hospital_name = doctor_details

    return jsonify({
        'clerkid': user.clerkid,
        'first_name': doctor.first_name,
        'last_name': doctor.last_name,
        'phone_number': doctor.phone_number,
        'email': doctor.email,
        'address': doctor.address,
        'years_of_experience': doctor.years_of_experience,
        'specialization': doctor.specialization,
        'department': doctor.department,
        'clinic_address': doctor.clinic_address,
        'consultation_fee': doctor.consultation_fee,
        'available_days': doctor.available_days,
        'available_time': doctor.available_time,
        'hospital_id': doctor.hospital_id,  # Include hospital_id
        'hospital_name': hospital_name  # Include hospital_name
    }), 200

    
# Route to update doctor details
@doctor_bp.route('/update-details/<clerkid>', methods=['PATCH'])
@swag_from({
    'summary': 'Updates the Doctor Details by ClerkID',
    'tags': ['Doctor Details'],
    'parameters': [
        {
            'name': 'clerkid',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ClerkID of the doctor'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'address': {'type': 'string'},
                    'years_of_experience': {'type': 'integer'},
                    'specialization': {'type': 'string'},
                    'department': {'type': 'string'},
                    'clinic_address': {'type': 'string'},
                    'consultation_fee': {'type': 'number'},
                    'available_days': {'type': 'string'},
                    'available_time': {'type': 'string'},
                    'hospital_id': {'type': 'integer'}  # Added hospital_id
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Doctor details updated successfully',
            'examples': {'application/json': {'message': 'Doctor details updated successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'Doctor not found'}}
        }
    }
})
def update_doctor_details(clerkid):
    data = request.json

    user = User.query.filter_by(clerkid=clerkid).first()
    if not user or user.role != 'DOCTOR':
        return jsonify({"error": "Doctor not found"}), 400

    doctor_details = DoctorDetails.query.filter_by(clerkid=user.clerkid).first()
    if not doctor_details:
        return jsonify({"error": "Doctor details not found"}), 400

    if 'first_name' in data:
        doctor_details.first_name = data['first_name']
    if 'last_name' in data:
        doctor_details.last_name = data['last_name']
    if 'phone_number' in data:
        doctor_details.phone_number = data['phone_number']
    if 'address' in data:
        doctor_details.address = data['address']
    if 'email' in data:
        doctor_details.email = data['email']
    if 'years_of_experience' in data:
        doctor_details.years_of_experience = data['years_of_experience']
    if 'specialization' in data:
        doctor_details.specialization = data['specialization']
    if 'department' in data:
        doctor_details.department = data['department']
    if 'clinic_address' in data:
        doctor_details.clinic_address = data['clinic_address']
    if 'consultation_fee' in data:
        doctor_details.consultation_fee = data['consultation_fee']
    if 'available_days' in data:
        doctor_details.available_days = data['available_days']
    if 'available_time' in data:
        doctor_details.available_time = data['available_time']
    if 'hospital_id' in data:
        doctor_details.hospital_id = data['hospital_id']  # Update hospital_id

    db.session.commit()

    return jsonify({"message": "Doctor details updated successfully"}), 200

# Route to get all users for the doctor's dashboard
@doctor_bp.route('/get-all-users', methods=['GET'])
@swag_from({
    'summary': 'Fetches all users for the doctor\'s dashboard',
    'tags': ['Doctor Dashboard'],
    'responses': {
        200: {
            'description': 'Users fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'clerkid': '1234',
                        'name': 'John Doe',
                        'phone_number': '9876543210',
                        'email': 'john.doe@example.com'
                    },
                    {
                        'clerkid': '5678',
                        'name': 'Jane Smith',
                        'phone_number': '1234567890',
                        'email': 'jane.smith@example.com'
                    }
                ]
            }
        }
    }
})
def get_all_users():
    user_details_list = UserDetails.query.all()
    users = []
    for user_details in user_details_list:
        user = User.query.filter_by(clerkid=user_details.clerkid).first()
        if user:
            users.append({
                'clerkid': user.clerkid,
                'name': f"{user_details.first_name} {user_details.last_name}",
                'phone_number': user_details.phone_number,
                'email': user_details.email
            })
    return jsonify(users), 200

# Route to get all doctors
@doctor_bp.route('/get-all-doctors', methods=['GET'])
@swag_from({
    'summary': 'Fetches all doctors',
    'tags': ['Doctor'],
    'responses': {
        200: {
            'description': 'Doctors fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'clerkid': '1234',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'specialization': 'Cardiology',
                        'hospital_id': 1,  # Added hospital_id
                        'hospital_name': 'General Hospital'  # Added hospital_name
                    }
                ]
            }
        }
    }
})
def get_all_doctors():
    doctor_details_list = DoctorDetails.query.all()
    doctors = []
    for doctor_details in doctor_details_list:
        user = User.query.filter_by(clerkid=doctor_details.clerkid, role='DOCTOR').first()
        if user:
            hospital = Hospital.query.get(doctor_details.hospital_id)  # Fetch hospital details
            doctors.append({
                'clerkid': doctor_details.clerkid,
                'first_name': doctor_details.first_name,
                'last_name': doctor_details.last_name,
                'specialization': doctor_details.specialization,
                'hospital_id': doctor_details.hospital_id,  # Include hospital_id
                'hospital_name': hospital.name if hospital else None  # Include hospital_name
            })
    return jsonify(doctors), 200