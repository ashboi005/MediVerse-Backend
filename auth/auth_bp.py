from flask import Blueprint, request, jsonify
from config import db
from models import User
from flasgger import swag_from

auth_bp = Blueprint('auth_bp', __name__)  # Declare this as a blueprint

# API route to create a user
@auth_bp.route('/create-user', methods=['POST'])
@swag_from({
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {'application/json': {'message': 'User registered successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'ID, first name, email, and role are required, and role must be either "patient" or "doctor"'}}
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
                    'clerkid': {'type': 'string'}  # Add clerkid here
                },
                'required': ['id', 'first_name', 'email', 'role', 'clerkid']  # clerkid is now required
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
    clerkid = data.get('clerkid')  # Get clerkid from the request

    # Just an error if API Endpoint is hit incorrectly with missing data
    if not id or not first_name or not email or not role or not clerkid:
        return jsonify({"error": "ID, first name, email, role, and clerkid are required, and role must be either 'PATIENT' or 'DOCTOR'"}), 400

    # Validate the role
    if role not in ['PATIENT', 'DOCTOR']:
        return jsonify({"error": "Role must be either 'PATIENT' or 'DOCTOR'"}), 400

    # Checks if user already exists, because we only want to save newly created users
    existing_user = User.query.filter_by(id=id).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Create new user
    user = User(id=id, first_name=first_name, last_name=last_name, email=email, role=role, clerkid=clerkid)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201
