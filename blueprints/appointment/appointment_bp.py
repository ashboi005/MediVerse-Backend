from flask import Blueprint, request, jsonify, current_app as app
from flasgger import swag_from
from flask_apscheduler import APScheduler
from config import db
from models import Appointment, User
from blueprints.hospital.models import Hospital # Import Hospital model
from datetime import datetime

appointment_bp = Blueprint('appointment_bp', __name__)

# Route to add an appointment (used by doctor)
@appointment_bp.route('/add-appointment', methods=['POST'])
@swag_from({
    'summary': 'Add a new appointment, to be used by the doctor',
    'tags': ['Appointment'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'doctor_clerkid': {'type': 'string'},
                    'patient_clerkid': {'type': 'string'},
                    'appointment_date': {'type': 'string', 'format': 'date-time'},
                    'text_field': {'type': 'string'},
                    'hospital_id': {'type': 'integer'}  # Added hospital_id
                },
                'required': ['doctor_clerkid', 'patient_clerkid', 'appointment_date']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Appointment added successfully',
            'examples': {'application/json': {'message': 'Appointment added successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'Validation error'}}
        }
    }
})
def add_appointment():
    data = request.json

    doctor_clerkid = data.get('doctor_clerkid')
    patient_clerkid = data.get('patient_clerkid')
    appointment_date = data.get('appointment_date')
    text_field = data.get('text_field')
    hospital_id = data.get('hospital_id')  # Get hospital_id from request

    doctor = User.query.filter_by(clerkid=doctor_clerkid).first()
    patient = User.query.filter_by(clerkid=patient_clerkid).first()

    if not doctor or doctor.role != 'DOCTOR':
        return jsonify({"error": "Doctor not found"}), 400
    if not patient or patient.role != 'PATIENT':
        return jsonify({"error": "Patient not found"}), 400

    appointment = Appointment(
        doctor_clerkid=doctor_clerkid,
        patient_clerkid=patient_clerkid,
        appointment_date=datetime.fromisoformat(appointment_date),
        status='approved',
        text_field=text_field,
        hospital_id=hospital_id  # Include hospital_id in the appointment
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment added successfully"}), 201

# Route to request an appointment (used by patient)
@appointment_bp.route('/request-appointment', methods=['POST'])
@swag_from({
    'summary': 'Request a new appointment',
    'tags': ['Appointment'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'doctor_clerkid': {'type': 'string'},
                    'patient_clerkid': {'type': 'string'},
                    'appointment_date': {'type': 'string', 'format': 'date-time'},
                    'text_field': {'type': 'string'},
                    'hospital_id': {'type': 'integer'}  # Added hospital_id
                },
                'required': ['doctor_clerkid', 'patient_clerkid', 'appointment_date']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Appointment request added successfully',
            'examples': {'application/json': {'message': 'Appointment request added successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'Validation error'}}
        }
    }
})
def request_appointment():
    data = request.json

    doctor_clerkid = data.get('doctor_clerkid')
    patient_clerkid = data.get('patient_clerkid')
    appointment_date = data.get('appointment_date')
    text_field = data.get('text_field')
    hospital_id = data.get('hospital_id')  # Get hospital_id from request

    doctor = User.query.filter_by(clerkid=doctor_clerkid).first()
    patient = User.query.filter_by(clerkid=patient_clerkid).first()

    if not doctor or doctor.role != 'DOCTOR':
        return jsonify({"error": "Doctor not found"}), 400
    if not patient or patient.role != 'PATIENT':
        return jsonify({"error": "Patient not found"}), 400

    appointment = Appointment(
        doctor_clerkid=doctor_clerkid,
        patient_clerkid=patient_clerkid,
        appointment_date=datetime.fromisoformat(appointment_date),
        status='pending',
        text_field=text_field,
        hospital_id=hospital_id  # Include hospital_id in the appointment
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment request added successfully"}), 201

# Route to accept or reject an appointment request (used by doctor)
@appointment_bp.route('/update-appointment-status/<id>', methods=['PATCH'])
@swag_from({
    'summary': 'Update the status of an appointment request',
    'tags': ['Appointment'],
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the appointment'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['approved', 'rejected']},
                    'text_field': {'type': 'string'}
                },
                'required': ['status']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Appointment status updated successfully',
            'examples': {'application/json': {'message': 'Appointment status updated successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'Validation error'}}
        }
    }
})
def update_appointment_status(id):
    data = request.json

    status = data.get('status')
    text_field = data.get('text_field')

    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 400

    appointment.status = status
    if text_field:
        appointment.text_field = text_field

    db.session.commit()

    return jsonify({"message": "Appointment status updated successfully"}), 200

# Route to get all appointments by user clerkid
@appointment_bp.route('/get-appointments/<clerkid>', methods=['GET'])
@swag_from({
    'summary': 'Get all appointments for a user',
    'tags': ['Appointment'],
    'parameters': [
        {
            'name': 'clerkid',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ClerkID of the user (doctor or patient)'
        }
    ],
    'responses': {
        200: {
            'description': 'Appointments fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'doctor_clerkid': '1234',
                        'patient_clerkid': '5678',
                        'appointment_date': '2023-10-01T12:00:00',
                        'status': 'approved',
                        'text_field': 'Follow-up appointment',
                        'hospital_id': 1,  # Added hospital_id
                        'hospital_name': 'General Hospital'  # Added hospital_name
                    }
                ]
            }
        },
        400: {
            'description': 'User not found',
            'examples': {'application/json': {'error': 'User not found'}}
        }
    }
})
def get_appointments(clerkid):
    user = User.query.filter_by(clerkid=clerkid).first()
    if not user:
        return jsonify({"error": "User not found"}), 400

    if user.role == 'DOCTOR':
        appointments = Appointment.query.filter_by(doctor_clerkid=clerkid).all()
    else:
        appointments = Appointment.query.filter_by(patient_clerkid=clerkid).all()

    appointment_list = []
    for appointment in appointments:
        hospital = Hospital.query.get(appointment.hospital_id)  # Fetch hospital details
        appointment_list.append({
            'id': appointment.id,
            'doctor_clerkid': appointment.doctor_clerkid,
            'patient_clerkid': appointment.patient_clerkid,
            'appointment_date': appointment.appointment_date.isoformat(),
            'status': appointment.status,
            'text_field': appointment.text_field,
            'hospital_id': appointment.hospital_id,  # Include hospital_id
            'hospital_name': hospital.name if hospital else None  # Include hospital_name
        })

    return jsonify(appointment_list), 200

# Route to get all pending appointments
@appointment_bp.route('/get-pending-appointments/<doctor_clerkid>', methods=['GET'])
@swag_from({
    'summary': 'Get all pending appointments for a specific doctor',
    'tags': ['Appointment'],
    'parameters': [
        {
            'name': 'doctor_clerkid',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ClerkID of the doctor'
        }
    ],
    'responses': {
        200: {
            'description': 'Pending appointments fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'doctor_clerkid': '1234',
                        'patient_clerkid': '5678',
                        'appointment_date': '2023-10-01T12:00:00',
                        'status': 'pending',
                        'text_field': 'Initial consultation',
                        'hospital_id': 1,
                        'hospital_name': 'General Hospital'
                    }
                ]
            }
        }
    }
})
def get_pending_appointments(doctor_clerkid):
    appointments = Appointment.query.filter_by(status='pending', doctor_clerkid=doctor_clerkid).all()

    appointment_list = []
    for appointment in appointments:
        hospital = Hospital.query.get(appointment.hospital_id)
        appointment_list.append({
            'id': appointment.id,
            'doctor_clerkid': appointment.doctor_clerkid,
            'patient_clerkid': appointment.patient_clerkid,
            'appointment_date': appointment.appointment_date.isoformat(),
            'status': appointment.status,
            'text_field': appointment.text_field,
            'hospital_id': appointment.hospital_id,
            'hospital_name': hospital.name if hospital else None
        })

    return jsonify(appointment_list), 200

