from flask import Blueprint, request, jsonify
from flasgger import swag_from
from config import db
from models import Prescription, User, DoctorDetails

prescription_bp = Blueprint('prescription_bp', __name__)

# Route to add a prescription (used by doctor)
@prescription_bp.route('/add-prescription', methods=['POST'])
@swag_from({
    'summary': 'Add a new prescription',
    'tags': ['Prescription'],
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
                    'prescription_text': {'type': 'string'}
                },
                'required': ['doctor_clerkid', 'patient_clerkid', 'prescription_text']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Prescription added successfully',
            'examples': {'application/json': {'message': 'Prescription added successfully'}}
        },
        400: {
            'description': 'Validation error',
            'examples': {'application/json': {'error': 'Validation error'}}
        }
    }
})
def add_prescription():
    data = request.json

    doctor_clerkid = data.get('doctor_clerkid')
    patient_clerkid = data.get('patient_clerkid')
    prescription_text = data.get('prescription_text')

    doctor = User.query.filter_by(clerkid=doctor_clerkid).first()
    patient = User.query.filter_by(clerkid=patient_clerkid).first()

    if not doctor or doctor.role != 'DOCTOR':
        return jsonify({"error": "Doctor not found"}), 400
    if not patient or patient.role != 'PATIENT':
        return jsonify({"error": "Patient not found"}), 400

    prescription = Prescription(
        doctor_clerkid=doctor_clerkid,
        patient_clerkid=patient_clerkid,
        prescription_text=prescription_text
    )

    db.session.add(prescription)
    db.session.commit()

    return jsonify({"message": "Prescription added successfully"}), 201

# Route to get all prescriptions for a patient
@prescription_bp.route('/get-prescriptions/<patient_clerkid>', methods=['GET'])
@swag_from({
    'summary': 'Get all prescriptions for a patient',
    'tags': ['Prescription'],
    'parameters': [
        {
            'name': 'patient_clerkid',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ClerkID of the patient'
        }
    ],
    'responses': {
        200: {
            'description': 'Prescriptions fetched successfully',
            'examples': {
                'application/json': [
                    {
                        'doctor_clerkid': '1234',
                        'doctor_name': 'John Doe',
                        'patient_clerkid': '5678',
                        'prescription_date': '2023-10-01T12:00:00',
                        'prescription_text': 'Take two tablets daily'
                    }
                ]
            }
        },
        400: {
            'description': 'Patient not found',
            'examples': {'application/json': {'error': 'Patient not found'}}
        }
    }
})
def get_prescriptions(patient_clerkid):
    patient = User.query.filter_by(clerkid=patient_clerkid).first()
    if not patient or patient.role != 'PATIENT':
        return jsonify({"error": "Patient not found"}), 400

    prescriptions = Prescription.query.filter_by(patient_clerkid=patient_clerkid).all()

    prescription_list = []
    for prescription in prescriptions:
        doctor = DoctorDetails.query.filter_by(clerkid=prescription.doctor_clerkid).first()
        doctor_name = f"{doctor.first_name} {doctor.last_name}" if doctor else "Unknown"
        prescription_list.append({
            'doctor_clerkid': prescription.doctor_clerkid,
            'doctor_name': doctor_name,
            'patient_clerkid': prescription.patient_clerkid,
            'prescription_date': prescription.prescription_date.isoformat(),
            'prescription_text': prescription.prescription_text
        })

    return jsonify(prescription_list), 200
