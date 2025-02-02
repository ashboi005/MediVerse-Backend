from flask import Blueprint, request, jsonify, make_response, g
from config import db
from blueprints.management.models import (
    ParkingLot, Sensor, Garbage, 
    EmergencyReport, EnergyUsage, WaterUsage
)
from datetime import datetime, timedelta, timezone
import uuid
import calendar
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flasgger import swag_from

# Initialize blueprints
parking_bp = Blueprint('parking_bp', __name__)
garbage_sensor_bp = Blueprint('garbage_sensor_bp', __name__)
fire_sensor_bp = Blueprint('fire_sensor_bp', __name__)
energy_usage_bp = Blueprint('energy_usage_bp', __name__)
water_usage_bp = Blueprint('water_usage_bp', __name__)
sensor_bp = Blueprint('sensor_bp', __name__)

# Define IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Twilio Helper Function
def send_sms(to_number, message_text):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            to=to_number,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            body=message_text,
        )
        return message.sid
    except TwilioRestException as e:
        print(f"Error sending SMS: {str(e)}")
        return None

# Garbage Alert Helper Function
def trigger_garbage_response(location):
    emergency_contact_number= os.getenv("EMERGENCY_CONTACT_NUMBER")
    if emergency_contact_number:
        message_text = f"Garbage overflow detected at {location}. Immediate cleanup required."
        send_sms(emergency_contact_number, message_text)
    else:
        print("EMERGENCY_CONTACT_NUMBER environment variable not set.")

# Shared Helper Function for Water Usage Data
def get_water_usage_data(year, month):
    session = db.session
    try:
        start_date = datetime(year, month, 1, tzinfo=IST)
        end_date = start_date + timedelta(days=calendar.monthrange(year, month)[1])
        
        records = session.query(WaterUsage).filter(
            WaterUsage.timestamp >= start_date.astimezone(timezone.utc),
            WaterUsage.timestamp < end_date.astimezone(timezone.utc)
        ).all()

        return {
            "total_usage_liters": sum(r.usage_liters for r in records),
            "usage_records": [{
                "date": r.timestamp.astimezone(IST).strftime("%Y-%m-%d"),
                "usage_liters": r.usage_liters
            } for r in records]
        }
    except Exception as e:
        raise e
    finally:
        session.close()

# ==================== Sensor Routes ====================
@sensor_bp.route('/add_sensor', methods=['POST'])
@swag_from({
    'tags': ['Sensors'],
    'summary': 'Add a new sensor',
    'description': 'This endpoint adds a new sensor to the database.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'sensor_name': {'type': 'string', 'example': 'P005'},
                    'type': {'type': 'string', 'example': 'parking'},
                    'location': {'type': 'string', 'example': 'Building C'}
                },
                'required': ['sensor_name', 'type', 'location']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Sensor added successfully!',
            'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}
        },
        '400': {
            'description': 'Bad request, invalid input'
        }
    }
})
def add_sensor():
    """ Add a new sensor """
    data = request.json
    try:
        new_sensor = Sensor(
            sensor_name=data['sensor_name'],
            type=data['type'],
            location=data['location']
        )
        db.session.add(new_sensor)
        db.session.commit()
        return jsonify({'message': 'Sensor added successfully!'}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================== Parking Routes ====================
@parking_bp.route('/update-status/<sensor_id>', methods=['POST'])
@swag_from({
    'tags': ['Parking'],
    'description': 'Update parking lot status based on sensor data',
    'parameters': [
        {
            'name': 'sensor_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the parking sensor'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'boolean',
                        'description': 'True if parking lot is empty, False if occupied'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Parking status updated successfully'},
        400: {'description': 'Invalid data provided'},
        404: {'description': 'Parking lot not found'},
        500: {'description': 'Internal server error'}
    }
})
def update_parking_status(sensor_id):
    data = request.json
    status = data.get('status', True)  # Default to True (empty) if status is missing

    session = db.session
    try:
        parking_lot = session.query(ParkingLot).filter_by(sensor_id=sensor_id).first()
        if not parking_lot:
            return jsonify({"error": "Parking lot not found"}), 404

        parking_lot.status = status
        parking_lot.last_updated = datetime.utcnow()
        session.commit()

        # Corrected response messages
        return jsonify({"message": "Car parked" if not status else "Car unparked"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@parking_bp.route('/status', methods=['GET'])
@swag_from({
    'tags': ['Parking'],
    'description': 'Get the status of all parking lots',
    'responses': {
        200: {'description': 'List of parking lot statuses'},
        500: {'description': 'Internal server error'}
    }
})
def get_parking_lots_status():
    session = db.session
    try:
        parking_lots = session.query(ParkingLot).all()
        lots_data = [{
            "sensor_id": lot.sensor_id,
            "location": lot.sensor.location,
            "status": "Empty" if lot.status else "Occupied",
            "last_updated": lot.last_updated.isoformat(),
        } for lot in parking_lots]
        return jsonify(lots_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# ==================== Garbage Routes ====================
@garbage_sensor_bp.route('/garbage-overflow', methods=['POST'])
@swag_from({
    'tags': ['Garbage'],
    'description': 'Handle garbage overflow alerts from sensors',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'sensor_name': {'type': 'string', 'description': 'Name of the sensor'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Alert logged successfully'},
        400: {'description': 'No data provided'},
        404: {'description': 'Sensor not found'},
        500: {'description': 'Internal server error'}
    }
})
def receive_garbage_alert():
    data = request.json
    sensor_name = data.get('sensor_name')

    session = db.session
    try:
        sensor = session.query(Sensor).filter_by(sensor_name=sensor_name).first()
        if not sensor:
            return jsonify({"error": "Sensor not found"}), 404

        new_record = Garbage(
            location=sensor.location,
            sensor_id=sensor_name
        )
        session.add(new_record)
        session.commit()
        trigger_garbage_response(sensor.location)  # Now defined
        return make_response(jsonify({"message": "Alert logged."}), 201)
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# ==================== Fire Routes ====================
@fire_sensor_bp.route('/fire-detected', methods=['POST'])
@swag_from({
    'tags': ['Fire'],
    'description': 'Handle fire detection alerts from sensors',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'sensor_name': {'type': 'string', 'description': 'Name of the sensor'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Fire alert handled successfully'},
        400: {'description': 'No data provided'},
        404: {'description': 'Sensor not found'},
        500: {'description': 'Internal server error'}
    }
})
def receive_fire_alert():
    data = request.json
    sensor_name = data.get('sensor_name')

    session = db.session
    try:
        sensor = session.query(Sensor).filter_by(sensor_name=sensor_name).first()
        if not sensor:
            return jsonify({"error": "Sensor not found"}), 404

        new_emergency = EmergencyReport(
            location=sensor.location,
            emergency_type='fire',
            sensor_id=sensor.sensor_name
        )
        session.add(new_emergency)
        
        emergency_contact_number = os.getenv("EMERGENCY_CONTACT_NUMBER")
        if emergency_contact_number:
            message_text = f"Fire emergency detected at {sensor.location}!"
            send_sms(emergency_contact_number, message_text)
        
        session.commit()
        return make_response(jsonify({"message": "Fire alert handled."}), 201)
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# ==================== Water Usage Routes ====================
@water_usage_bp.route("/record-usage", methods=["POST"])
@swag_from({
    'tags': ['Water'],
    'description': 'Record hospital-wide water usage',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'sensor_name': {'type': 'string'},
                'usage_liters': {'type': 'number'}
            },
            'required': ['sensor_name', 'usage_liters']
        }
    }],
    'responses': {
        201: {'description': 'Water usage recorded'},
        500: {'description': 'Server error'}
    }
})
def record_water_usage():
    data = request.json
    session = db.session
    try:
        sensor = session.query(Sensor).filter_by(sensor_name=data['sensor_name']).first()
        new_usage = WaterUsage(
            location=sensor.location,
            sensor_id=data['sensor_name'],
            usage_liters=data['usage_liters']
        )
        session.add(new_usage)
        
        # Use naive UTC datetime for cutoff
        cutoff_date = datetime.utcnow() - timedelta(days=730)
        session.query(WaterUsage).filter(WaterUsage.timestamp < cutoff_date).delete()
        
        session.commit()
        return jsonify({"message": "Water usage recorded"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

def get_water_usage_data(year, month):
    session = db.session
    try:
        # Create aware IST datetime for start of month
        start_date_ist = datetime(year, month, 1, tzinfo=IST)
        # Convert to naive UTC datetime
        start_date_utc = start_date_ist.astimezone(timezone.utc).replace(tzinfo=None)
        
        # Calculate last day of the month in IST
        last_day = calendar.monthrange(year, month)[1]
        end_date_ist = datetime(year, month, last_day, 23, 59, 59, tzinfo=IST)
        # Convert to naive UTC datetime
        end_date_utc = end_date_ist.astimezone(timezone.utc).replace(tzinfo=None)

        # Query using naive UTC datetimes
        records = session.query(WaterUsage).filter(
            WaterUsage.timestamp >= start_date_utc,
            WaterUsage.timestamp <= end_date_utc
        ).all()

        return {
            "total_usage_liters": sum(r.usage_liters for r in records),
            "usage_records": [{
                "date": r.timestamp.strftime("%Y-%m-%d"),  # Already naive UTC
                "usage_liters": r.usage_liters
            } for r in records]
        }
    except Exception as e:
        raise e
    finally:
        session.close()



@water_usage_bp.route("/usage/<int:year>/<int:month>", methods=["GET"])
@swag_from({
    'tags': ['Water'],
    'description': 'Get monthly water usage for entire hospital',
    'parameters': [
        {'name': 'year', 'in': 'path', 'type': 'integer'},
        {'name': 'month', 'in': 'path', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Hospital water usage'},
        500: {'description': 'Server error'}
    }
})
def get_monthly_water_usage(year, month):
    try:
        data = get_water_usage_data(year, month)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@water_usage_bp.route("/bill/<int:year>/<int:month>", methods=["GET"])
@swag_from({
    'tags': ['Water'],
    'description': 'Get monthly water bill for hospital',
    'parameters': [
        {'name': 'year', 'in': 'path', 'type': 'integer'},
        {'name': 'month', 'in': 'path', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Water bill details'},
        500: {'description': 'Server error'}
    }
})
def get_water_bill(year, month):
    try:
        data = get_water_usage_data(year, month)
        total_usage = data['total_usage_liters']
        return jsonify({
            "total_usage_liters": total_usage,
            "total_bill": total_usage * 0.5,
            "rate_per_liter": 0.5,
            "currency": "INR"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Energy Usage Routes ====================
@energy_usage_bp.route("/record-usage", methods=["POST"])
@swag_from({
    'tags': ['Energy'],
    'description': 'Record hospital-wide energy usage',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'sensor_name': {'type': 'string'},
                'usage_kwh': {'type': 'number'}
            },
            'required': ['sensor_name', 'usage_kwh']
        }
    }],
    'responses': {
        201: {'description': 'Energy usage recorded'},
        500: {'description': 'Server error'}
    }
})
def record_energy_usage():
    data = request.json
    session = db.session
    try:
        sensor = session.query(Sensor).filter_by(sensor_name=data['sensor_name']).first()
        new_usage = EnergyUsage(
            location=sensor.location,
            sensor_id=data['sensor_name'],
            usage_kwh=data['usage_kwh']
        )
        session.add(new_usage)
        
        # Cleanup old data (2 years)
        cutoff_date = datetime.utcnow() - timedelta(days=730)
        session.query(EnergyUsage).filter(EnergyUsage.timestamp < cutoff_date).delete()
        
        session.commit()
        return jsonify({"message": "Energy usage recorded"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@energy_usage_bp.route("/usage/<int:year>/<int:month>", methods=["GET"])
@swag_from({
    'tags': ['Energy'],
    'description': 'Get monthly energy usage for entire hospital',
    'parameters': [
        {'name': 'year', 'in': 'path', 'type': 'integer'},
        {'name': 'month', 'in': 'path', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Hospital energy usage'},
        500: {'description': 'Server error'}
    }
})
def get_monthly_energy_usage(year, month):
    try:
        # Shared logic with water usage (define a helper if repeating)
        start_date_ist = datetime(year, month, 1, tzinfo=IST)
        start_date_utc = start_date_ist.astimezone(timezone.utc).replace(tzinfo=None)
        
        last_day = calendar.monthrange(year, month)[1]
        end_date_ist = datetime(year, month, last_day, 23, 59, 59, tzinfo=IST)
        end_date_utc = end_date_ist.astimezone(timezone.utc).replace(tzinfo=None)

        session = db.session
        records = session.query(EnergyUsage).filter(
            EnergyUsage.timestamp >= start_date_utc,
            EnergyUsage.timestamp <= end_date_utc
        ).all()

        return jsonify({
            "total_usage_kwh": sum(r.usage_kwh for r in records),
            "usage_records": [{
                "date": r.timestamp.strftime("%Y-%m-%d"),
                "usage_kwh": r.usage_kwh
            } for r in records]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@energy_usage_bp.route("/bill/<int:year>/<int:month>", methods=["GET"])
@swag_from({
    'tags': ['Energy'],
    'description': 'Get monthly energy bill for hospital',
    'parameters': [
        {'name': 'year', 'in': 'path', 'type': 'integer'},
        {'name': 'month', 'in': 'path', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Energy bill details'},
        500: {'description': 'Server error'}
    }
})
def get_energy_bill(year, month):
    try:
        session = db.session
        records = session.query(EnergyUsage).filter(
            EnergyUsage.timestamp >= datetime(year, month, 1),
            EnergyUsage.timestamp < datetime(year, month + 1, 1)
        ).all()

        total_usage = sum(r.usage_kwh for r in records)
        return jsonify({
            "total_usage_kwh": total_usage,
            "total_bill": total_usage * 8.5,  # Example rate: ₹8.5 per kWh
            "rate_per_kwh": 8.5,
            "currency": "INR"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500