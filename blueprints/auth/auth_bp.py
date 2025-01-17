from flask import Blueprint, request, jsonify
from config import db
from models import User
from flasgger import swag_from

auth_bp = Blueprint('auth_bp', __name__)  # Declare this as a blueprint

# API route to create a user, TO BE USED IN TESTING ONLY, NOT REQUIRED BY THE FRONTEND as when the user is created via clerk it automatically goes in the db we have
@auth_bp.route('/create-user', methods=['POST'])
@swag_from({
    'summary': 'Creates a User, only for testing not needed by the frontend',
    'tags': ['Auth'],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {'application/json': {'message': 'User registered successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'User already exists or validation error'}}
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
                    'id': {'type': 'string'},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'role': {'type': 'string', 'enum': ['PATIENT', 'DOCTOR']},
                    'clerkid': {'type': 'string'}
                },
                'required': ['id', 'first_name', 'email', 'role', 'clerkid']
            }
        }
    ]
})
def create_user():
    data = request.json  # Retrieve JSON data from the request
    id = data.get('id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    role = data.get('role')
    clerkid = data.get('clerkid')

    # Ensure all required fields are present
    if not id or not first_name or not email or not role or not clerkid:
        return jsonify({"error": "ID, first name, email, role, and clerkid are required, and role must be either 'PATIENT' or 'DOCTOR'"}), 400

    # Validate the role
    if role not in ['PATIENT', 'DOCTOR']:
        return jsonify({"error": "Role must be either 'PATIENT' or 'DOCTOR'"}), 400

    # Check if a user with the same email already exists
    existing_email_user = User.query.filter_by(email=email).first()
    if existing_email_user:
        return jsonify({"error": f"User with email '{email}' already exists."}), 400

    # Check if a user with the same ID already exists
    existing_user = User.query.filter_by(id=id).first()
    if existing_user:
        return jsonify({"error": f"User with ID '{id}' already exists."}), 400

    # Create and save the new user
    user = User(id=id, first_name=first_name, last_name=last_name, email=email, role=role, clerkid=clerkid)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500
