from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from models import DoctorDetails
from blueprints.hospital.models import Hospital

hospital_bp = Blueprint('hospital_bp', __name__)

# Route to add a new hospital
@hospital_bp.route('/add-hospital', methods=['POST'])
@swag_from({
    'summary': 'Add a new hospital',
    'tags': ['Hospital'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'address': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'email': {'type': 'string'},
                    'website': {'type': 'string'}
                },
                'required': ['name', 'address', 'phone_number', 'email']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Hospital added successfully',
            'examples': {'application/json': {'message': 'Hospital added successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'Validation error'}}
        }
    }
})
def add_hospital():
    data = request.json

    hospital = Hospital(
        name=data.get('name'),
        address=data.get('address'),
        phone_number=data.get('phone_number'),
        email=data.get('email'),
        website=data.get('website')
    )

    db.session.add(hospital)
    db.session.commit()

    return jsonify({"message": "Hospital added successfully"}), 201

# Route to get all hospitals
@hospital_bp.route('/get-hospitals', methods=['GET'])
@swag_from({
    'summary': 'Get all hospitals',
    'tags': ['Hospital'],
    'responses': {
        200: {
            'description': 'Hospitals fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'name': 'General Hospital',
                        'address': '123 Main St, Springfield, IL',
                        'phone_number': '123-456-7890',
                        'email': 'info@generalhospital.com',
                        'website': 'https://generalhospital.com'
                    }
                ]
            }
        }
    }
})
def get_hospitals():
    hospitals = Hospital.query.all()
    hospital_list = [
        {
            'id': hospital.id,
            'name': hospital.name,
            'address': hospital.address,
            'phone_number': hospital.phone_number,
            'email': hospital.email,
            'website': hospital.website
        }
        for hospital in hospitals
    ]

    return jsonify(hospital_list), 200

@hospital_bp.route('/get-doctors-by-hospital/<hospital_id>', methods=['GET'])
@swag_from({
    'summary': 'Get doctors by hospital',
    'tags': ['Hospital'],
    'parameters': [
        {
            'name': 'hospital_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the hospital'
        }
    ],
    'responses': {
        200: {
            'description': 'Doctors fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'specialization': 'Cardiology',
                        'email': 'john.doe@example.com',
                        'phone_number': '123-456-7890'
                    }
                ]
            }
        },
        400: {
            'description': 'Hospital not found',
            'examples': {'application/json': {'error': 'Hospital not found'}}
        },
        404: {
            'description': 'No doctors found for the specified hospital',
            'examples': {'application/json': {'message': 'No doctors found for this hospital'}}
        }
    }
})
def get_doctors_by_hospital(hospital_id):
    hospital = Hospital.query.get(hospital_id)
    if not hospital:
        return jsonify({"error": "Hospital not found"}), 400

    doctors = DoctorDetails.query.filter_by(hospital_id=hospital.id).all()
    
    if not doctors:
        return jsonify({"message": "No doctors found for this hospital"}), 404

    doctor_list = [
        {
            'id': doctor.id,
            'first_name': doctor.first_name,
            'last_name': doctor.last_name,
            'specialization': doctor.specialization,
            'email': doctor.email,
            'phone_number': doctor.phone_number
        }
        for doctor in doctors
    ]

    return jsonify(doctor_list), 200