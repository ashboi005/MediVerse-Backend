from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from models import User, UserDetails
from datetime import datetime

user_bp = Blueprint('user_bp', __name__)  # Declare this as a blueprint

# Function to handle date conversion
def convert_to_date(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")
    return None

# API route to create user details when a new user logs in for the first time
@user_bp.route('/create-details', methods=['POST'])
@swag_from({
    'responses': {
        201: {
            'description': 'User details created successfully',
            'examples': {'application/json': {'message': 'User details created successfully'}}
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
                    'user_id': {'type': 'string'},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'date_of_birth': {'type': 'string', 'format': 'date'},
                    'gender': {'type': 'string'},
                    'age': {'type': 'integer'},
                    'address': {'type': 'string'},
                    'blood_group': {'type': 'string'},
                    'known_allergies': {'type': 'string'},
                    'chronic_conditions': {'type': 'string'},
                    'previous_major_diseases': {'type': 'string'},
                    'previous_major_surgeries': {'type': 'string'},
                    'family_medical_history': {'type': 'string'},
                    'height': {'type': 'number', 'format': 'float'},
                    'weight': {'type': 'number', 'format': 'float'},
                    'bmi': {'type': 'number', 'format': 'float'},
                    'current_medication': {'type': 'string'},
                    'current_health_conditions': {'type': 'string'},
                    'vaccination_history': {'type': 'string'},
                    'emergency_contact_name': {'type': 'string'},
                    'emergency_contact_phone': {'type': 'string'},
                    'emergency_contact_relationship': {'type': 'string'},
                    'smoking_status': {'type': 'string'},
                    'alcohol_consumption': {'type': 'string'},
                    'exercise_frequency': {'type': 'string'},
                    'dietary_preferences': {'type': 'string'},
                    'insurance_provider': {'type': 'string'},
                    'insurance_plan_number': {'type': 'string'},
                    'insurance_validity': {'type': 'string', 'format': 'date'},
                    'mental_health_conditions': {'type': 'string'}
                },
                'required': ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'age', 'address', 'blood_group']
            }
        }
    ]
})
def create_user_details():
    data = request.json  # Get the JSON data sent by the client

    try:
        date_of_birth = convert_to_date(data.get('date_of_birth'))
        insurance_validity = convert_to_date(data.get('insurance_validity'))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    user_id = data.get('user_id')

    # Find the user in the User table using the clerkid
    user = User.query.filter_by(clerkid=user_id).first()  
    if not user:
        return jsonify({"error": "User not found"}), 400

    # Create new user details
    user_details = UserDetails(
        user_id=user_id,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone_number=data.get('phone_number'),
        date_of_birth=date_of_birth,
        gender=data.get('gender'),
        age=data.get('age'),
        address=data.get('address'),
        blood_group=data.get('blood_group'),
        known_allergies=data.get('known_allergies'),
        chronic_conditions=data.get('chronic_conditions'),
        previous_major_diseases=data.get('previous_major_diseases'),
        previous_major_surgeries=data.get('previous_major_surgeries'),
        family_medical_history=data.get('family_medical_history'),
        height=data.get('height'),
        weight=data.get('weight'),
        bmi=data.get('bmi'),
        current_medication=data.get('current_medication'),
        current_health_conditions=data.get('current_health_conditions'),
        vaccination_history=data.get('vaccination_history'),
        emergency_contact_name=data.get('emergency_contact_name'),
        emergency_contact_phone=data.get('emergency_contact_phone'),
        emergency_contact_relationship=data.get('emergency_contact_relationship'),
        smoking_status=data.get('smoking_status'),
        alcohol_consumption=data.get('alcohol_consumption'),
        exercise_frequency=data.get('exercise_frequency'),
        dietary_preferences=data.get('dietary_preferences'),
        insurance_provider=data.get('insurance_provider'),
        insurance_plan_number=data.get('insurance_plan_number'),
        insurance_validity=insurance_validity,
        mental_health_conditions=data.get('mental_health_conditions')
    )

    db.session.add(user_details)
    db.session.commit()

    return jsonify({"message": "User details created successfully"}), 201

# API route to get user details
@user_bp.route('/get-details/<user_id>', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'User details fetched successfully',
            'examples': {
                'application/json': {
                    'user_id': '1234',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                    'phone_number': '9876543210',
                    'age': 30,
                    'address': '123 Main St, Springfield, IL',
                    'blood_group': 'O+'
                }
            }
        },
        400: {
            'description': 'User not found',
            'examples': {'application/json': {'error': 'User not found'}}
        }
    }
})
def get_user_details(user_id):
    user_details = UserDetails.query.filter_by(user_id=user_id).first()

    if not user_details:
        return jsonify({"error": "User not found"}), 400

    return jsonify({
        'user_id': user_details.user_id,
        'first_name': user_details.first_name,
        'last_name': user_details.last_name,
        'email': user_details.email,
        'phone_number': user_details.phone_number,
        'age': user_details.age,
        'address': user_details.address,
        'blood_group': user_details.blood_group,
        'known_allergies': user_details.known_allergies,
        'chronic_conditions': user_details.chronic_conditions,
        'previous_major_diseases': user_details.previous_major_diseases,
        'previous_major_surgeries': user_details.previous_major_surgeries,
        'family_medical_history': user_details.family_medical_history,
        'height': user_details.height,
        'weight': user_details.weight,
        'bmi': user_details.bmi,
        'current_medication': user_details.current_medication,
        'current_health_conditions': user_details.current_health_conditions,
        'vaccination_history': user_details.vaccination_history,
        'emergency_contact_name': user_details.emergency_contact_name,
        'emergency_contact_phone': user_details.emergency_contact_phone,
        'emergency_contact_relationship': user_details.emergency_contact_relationship,
        'smoking_status': user_details.smoking_status,
        'alcohol_consumption': user_details.alcohol_consumption,
        'exercise_frequency': user_details.exercise_frequency,
        'dietary_preferences': user_details.dietary_preferences,
        'insurance_provider': user_details.insurance_provider,
        'insurance_plan_number': user_details.insurance_plan_number,
        'insurance_validity': user_details.insurance_validity,
        'mental_health_conditions': user_details.mental_health_conditions
    }), 200

# API route to update user details
@user_bp.route('/update-details/<user_id>', methods=['PATCH'])
@swag_from({
    'responses': {
        200: {
            'description': 'User details updated successfully',
            'examples': {'application/json': {'message': 'User details updated successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'User not found'}}
        }
    }
})
def update_user_details(user_id):
    data = request.json  # Get the JSON data sent by the client

    # Find the user details by user_id
    user_details = UserDetails.query.filter_by(user_id=user_id).first()
    if not user_details:
        return jsonify({"error": "User not found"}), 400

    # Update fields with provided data (checking for every field in the UserDetails table)
    if 'first_name' in data:
        user_details.first_name = data['first_name']
    if 'last_name' in data:
        user_details.last_name = data['last_name']
    if 'email' in data:
        user_details.email = data['email']
    if 'phone_number' in data:
        user_details.phone_number = data['phone_number']
    if 'date_of_birth' in data:
        try:
            user_details.date_of_birth = convert_to_date(data['date_of_birth'])
        except ValueError as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    if 'gender' in data:
        user_details.gender = data['gender']
    if 'age' in data:
        user_details.age = data['age']
    if 'address' in data:
        user_details.address = data['address']
    if 'blood_group' in data:
        user_details.blood_group = data['blood_group']
    if 'known_allergies' in data:
        user_details.known_allergies = data['known_allergies']
    if 'chronic_conditions' in data:
        user_details.chronic_conditions = data['chronic_conditions']
    if 'previous_major_diseases' in data:
        user_details.previous_major_diseases = data['previous_major_diseases']
    if 'previous_major_surgeries' in data:
        user_details.previous_major_surgeries = data['previous_major_surgeries']
    if 'family_medical_history' in data:
        user_details.family_medical_history = data['family_medical_history']
    if 'height' in data:
        user_details.height = data['height']
    if 'weight' in data:
        user_details.weight = data['weight']
    if 'bmi' in data:
        user_details.bmi = data['bmi']
    if 'current_medication' in data:
        user_details.current_medication = data['current_medication']
    if 'current_health_conditions' in data:
        user_details.current_health_conditions = data['current_health_conditions']
    if 'vaccination_history' in data:
        user_details.vaccination_history = data['vaccination_history']
    if 'emergency_contact_name' in data:
        user_details.emergency_contact_name = data['emergency_contact_name']
    if 'emergency_contact_phone' in data:
        user_details.emergency_contact_phone = data['emergency_contact_phone']
    if 'emergency_contact_relationship' in data:
        user_details.emergency_contact_relationship = data['emergency_contact_relationship']
    if 'smoking_status' in data:
        user_details.smoking_status = data['smoking_status']
    if 'alcohol_consumption' in data:
        user_details.alcohol_consumption = data['alcohol_consumption']
    if 'exercise_frequency' in data:
        user_details.exercise_frequency = data['exercise_frequency']
    if 'dietary_preferences' in data:
        user_details.dietary_preferences = data['dietary_preferences']
    if 'insurance_provider' in data:
        user_details.insurance_provider = data['insurance_provider']
    if 'insurance_plan_number' in data:
        user_details.insurance_plan_number = data['insurance_plan_number']
    if 'insurance_validity' in data:
        try:
            user_details.insurance_validity = convert_to_date(data['insurance_validity'])
        except ValueError as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    if 'mental_health_conditions' in data:
        user_details.mental_health_conditions = data['mental_health_conditions']

    # Commit changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({"message": "User details updated successfully"}), 200
