from flask import Blueprint, request, jsonify
from flasgger import swag_from
from utils.file_upload import handle_file_upload
from utils.gemini import summarize_text, routine_generator
from models import db, TextReport, User


ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/upload', methods=['POST'])
@swag_from({
    'summary': 'Upload a File to extract text and generate Summary',
    'tags': ['Reports'],
    'responses': {
        200: {
            'description': 'Text extracted and summarized successfully',
            'examples': {'application/json': {'extracted_text': 'Sample extracted text', 'summarized_text': 'Summarized result here'}}
        },
        400: {
            'description': 'File upload error or unsupported format',
            'examples': {'application/json': {'error': 'File not supported'}}
        }
    }
})
def upload_and_process():
    file = request.files.get('file')  # Get the uploaded file from form-data
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ['pdf', 'jpg', 'jpeg', 'png']:
        return jsonify({"error": "Unsupported file format. Only PDF, JPG, JPEG, and PNG are allowed."}), 400

    # Save file and extract text
    text = handle_file_upload(file)

    # Summarize or analyze the extracted text using Gemini API
    summarized_text = summarize_text(text)

    # Get clerkid from form-data
    clerkid = request.form.get('clerkid')  # Use request.form for form-data
    if not clerkid:
        return jsonify({"error": "Clerk ID is missing from the request"}), 400

    # Query the User table to find the user based on clerkid
    user = User.query.filter_by(clerkid=clerkid).first()
    if not user:
        return jsonify({"error": "User not found"}), 400

    # Save extracted and summarized text to the database
    text_report = TextReport(
        clerkid=clerkid,
        extracted_text=text,
        summarized_text=summarized_text
    )

    db.session.add(text_report)
    db.session.commit()

    # Return both extracted and summarized text
    return jsonify({"extracted_text": text, "summarized_text": summarized_text}), 200


@ai_bp.route('/get-reports/<clerkid>', methods=['GET'])
@swag_from({
    'summary': 'Fetch all reports for a user by clerkid',
    'tags': ['Reports'],
    'parameters': [
        {
            'name': 'clerkid',
            'in': 'path',
            'required': True,
            'description': 'The unique clerk ID of the user',
            'schema': {'type': 'string'}
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully fetched all reports for the user',
            'content': {
                'application/json': {
                    'example': {
                        'reports': [
                            {
                                'extracted_text': 'This is a sample extracted text',
                                'summarized_text': 'This is a sample summary',
                                'created_at': '2025-01-17T18:30:00'
                            }
                        ]
                    }
                }
            }
        },
        400: {
            'description': 'Validation error',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'User not found'
                    }
                }
            }
        }
    }
})
def get_reports(clerkid):
    # Query the User table to find the user based on clerkid
    user = User.query.filter_by(clerkid=clerkid).first()
    if not user:
        return jsonify({"error": "User not found"}), 400

    # Fetch all reports for the user, sorted by created_at (most recent first)
    reports = TextReport.query.filter_by(clerkid=clerkid).order_by(TextReport.created_at.desc()).all()

    # Format the reports for the response
    response_data = [
        {
            'extracted_text': report.extracted_text,
            'summarized_text': report.summarized_text,
            'created_at': report.created_at.isoformat()
        }
        for report in reports
    ]

    return jsonify({"reports": response_data}), 200


HEALTH_KEYWORDS = [
    "fitness", "exercise", "diet", "wellness", "health", "nutrition",
    "meditation", "yoga", "workout", "self-care", "sleep"
]

@ai_bp.route('/routine', methods=['POST'])
@swag_from({
    'summary': 'Generate a 10-day health-related routine',
    'tags': ['Routine'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'goal': {
                        'type': 'string',
                        'description': 'The health-related goal for the routine generation'
                    }
                },
                'required': ['goal']
            },
            'example': {
                'goal': 'lose weight through healthy eating and exercise'
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Routine generated successfully',
            'content': {
                'application/json': {
                    'example': {
                        'routine': 'Day 1: Morning Yoga for 30 minutes...'
                    }
                }
            }
        },
        400: {
            'description': 'Validation error or unsupported goal',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'Only health-related topics are supported for routine generation.'
                    }
                }
            }
        },
        500: {
            'description': 'Error during routine generation',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'An error occurred during routine generation: <error-message>'
                    }
                }
            }
        }
    }
})
def generate_routine():
    data = request.json  # Get JSON data from the request
    goal = data.get('goal')

    if not goal:
        return jsonify({'error': 'Goal is required'}), 400

    if not any(keyword in goal.lower() for keyword in HEALTH_KEYWORDS):
        return jsonify({'error': 'Only health-related topics are supported for routine generation.'}), 400

    query = f"generate me a 10 days plan for {goal} in md format without any extra description"

    try:
        routine = routine_generator(query)
        return jsonify({'routine': routine}), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred during routine generation: {str(e)}'}), 500
