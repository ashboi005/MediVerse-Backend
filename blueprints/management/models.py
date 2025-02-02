from datetime import datetime
import uuid
from config import db

# ==================== Base Models ====================

class Sensor(db.Model):
    """
    Represents a sensor in the hospital management system.
    """
    __tablename__ = 'sensor'
    sensor_name = db.Column(db.String, primary_key=True)  # Unique identifier for the sensor
    location = db.Column(db.String, nullable=False)      # Location of the sensor in the hospital
    type = db.Column(db.String, nullable=False)          # Type of sensor (e.g., parking, garbage, fire, energy, water)
    parking_lot = db.relationship("ParkingLot", back_populates="sensor", uselist=False)

# ==================== Parking Management ====================

class ParkingLot(db.Model):
    """
    Represents a parking lot managed by a sensor.
    """
    __tablename__ = 'parking_lot'
    sensor_id = db.Column(db.String, db.ForeignKey('sensor.sensor_name'), primary_key=True)
    status = db.Column(db.Boolean, default=True)  # True = empty, False = occupied
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    sensor = db.relationship("Sensor", back_populates="parking_lot")

# ==================== Garbage Management ====================

class Garbage(db.Model):
    """
    Represents garbage overflow alerts from sensors.
    """
    __tablename__ = 'garbage'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    location = db.Column(db.String, nullable=False)  # Location of the garbage bin
    sensor_id = db.Column(db.String, db.ForeignKey('sensor.sensor_name'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== Emergency Management ====================

class EmergencyReport(db.Model):
    """
    Represents emergency reports (e.g., fire alerts).
    """
    __tablename__ = 'emergency_report'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    location = db.Column(db.String, nullable=False)  # Location of the emergency
    emergency_type = db.Column(db.String, nullable=False)  # Type of emergency (e.g., fire)
    sensor_id = db.Column(db.String, db.ForeignKey('sensor.sensor_name'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== Energy Management ====================

class EnergyUsage(db.Model):
    """
    Represents energy usage data from sensors.
    """
    __tablename__ = 'energy_usage'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    location = db.Column(db.String, nullable=False)  # Location of the energy sensor
    sensor_id = db.Column(db.String, db.ForeignKey('sensor.sensor_name'))
    usage_kwh = db.Column(db.Float, nullable=False)  # Energy usage in kWh
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== Water Management ====================

class WaterUsage(db.Model):
    """
    Represents water usage data from sensors.
    """
    __tablename__ = 'water_usage'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    location = db.Column(db.String, nullable=False)  # Location of the water sensor
    sensor_id = db.Column(db.String, db.ForeignKey('sensor.sensor_name'))
    usage_liters = db.Column(db.Float, nullable=False)  # Water usage in liters
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


