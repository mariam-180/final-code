
import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from enum import Enum, auto
import threading

# ====================== **Enums & Constants** ======================
class SensorType(Enum):
    TEMPERATURE = auto()
    SOIL_MOISTURE = auto()
    LIGHT_INTENSITY = auto()
    CO2_LEVEL = auto()
    HUMIDITY = auto()

class ActuatorType(Enum):
    IRRIGATION = auto()
    COOLING = auto()
    VENTILATION = auto()
    FERTILIZER_DOSER = auto()

# Sensor ranges
SENSORS = {
    SensorType.TEMPERATURE: {"min": 20, "max": 30, "unit": "°C"},
    SensorType.SOIL_MOISTURE: {"min": 30, "max": 70, "unit": "%"},
    SensorType.LIGHT_INTENSITY: {"min": 0, "max": 100, "unit": "lux"},
    SensorType.CO2_LEVEL: {"min": 300, "max": 1000, "unit": "ppm"},
    SensorType.HUMIDITY: {"min": 40, "max": 80, "unit": "%"}
}

# MQTT Setup
client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)
threading.Thread(target=client.loop_forever, daemon=True).start()

# Global state for actuators
actuators = {actuator: False for actuator in ActuatorType}
history = []
local_db = []
cloud_sync_interval = 5

# ====================== **Core Functions** ======================

def read_sensors():
    """Layer 1: Perception - Simulate sensor readings."""
    timestamp = datetime.now().isoformat()
    return [{
        "sensor_type": sensor.name,
        "value": round(random.uniform(params["min"], params["max"]), 1),
        "unit": params["unit"],
        "timestamp": timestamp
    } for sensor, params in SENSORS.items()]

def send_mqtt(data):
    """Layer 2: Transport - Publish to MQTT with LoRaWAN simulation."""
    payload = json.dumps(data)
    client.publish("iot/agriculture/data", payload)
    print(f"[LoRaWAN Sim] Sent long-range packet (Size: {len(payload)} bytes)")

def analyze_data(data):
    """Layer 3: Processing - Edge AI logic."""
    temp = next(d["value"] for d in data if d["sensor_type"] == SensorType.TEMPERATURE.name)
    humidity = next(d["value"] for d in data if d["sensor_type"] == SensorType.HUMIDITY.name)
    moisture = next(d["value"] for d in data if d["sensor_type"] == SensorType.SOIL_MOISTURE.name)

    dew_point = round(temp - ((100 - humidity) / 5), 1)
    heat_index = round(temp + humidity * 0.1, 1)
    crop_stress = random.uniform(0, 1)

    return {
        "raw_data": data,
        "metrics": {"dew_point": dew_point, "heat_index": heat_index},
        "predictions": {
            "crop_stress_risk": crop_stress,
            "irrigation_needed": crop_stress > 0.7,
            "optimal_watering": "ASAP" if crop_stress > 0.7 else "6h"
        }
    }

def control_actuators(processed_data):
    """Layer 4: Application - Trigger actuators."""
    global actuators
    if processed_data["predictions"]["irrigation_needed"]:
        actuators[ActuatorType.IRRIGATION] = True
    if processed_data["metrics"]["heat_index"] > 30:
        actuators[ActuatorType.COOLING] = True
    if processed_data["metrics"]["dew_point"] > 25:
        actuators[ActuatorType.VENTILATION] = True
    if next(d["value"] for d in processed_data["raw_data"] if d["sensor_type"] == SensorType.CO2_LEVEL.name) < 400:
        actuators[ActuatorType.FERTILIZER_DOSER] = True

    print("Actuators:", {a.name: "ON" if s else "OFF" for a, s in actuators.items()})

def business_report(processed_data):
    """Layer 5: Business Intelligence - Historical analysis."""
    history.append(processed_data)
    if len(history) % 5 == 0:
        print("\n=== Business Report ===")
        print(f"Total Data Points: {len(history)}")
        print("Recent Stress Levels:", [d["predictions"]["crop_stress_risk"] for d in history[-3:]])
        print("Recommended Actions: Check irrigation valves\n")

def cloud_sync(data):
    """Storage - Simulate cloud sync every 5 cycles."""
    local_db.append(data)
    if len(local_db) % cloud_sync_interval == 0:
        print(f"📤 Cloud Sync: Uploaded {cloud_sync_interval} records")

# ====================== **Main Loop** ======================
print("🌱 Initializing IoT Smart Farm System...")
cycle = 0

try:
    while True:
        print("\n" + "="*40)
        print(f"Cycle @ {datetime.now().strftime('%H:%M:%S')}")

        # 1. Perception Layer
        sensor_data = read_sensors()
        print("📡 Sensor Data:", [f"{d['sensor_type']}: {d['value']}{d['unit']}" for d in sensor_data])

        # 2. Transport Layer
        send_mqtt(sensor_data)

        # 3. Processing Layer
        processed_data = analyze_data(sensor_data)
        print("🧠 Edge AI Output:", processed_data["predictions"])

        # 4. Application Layer
        control_actuators(processed_data)

        # 5. Business Layer
        business_report(processed_data)

        # 6. Storage
        cloud_sync(processed_data)

        cycle += 1
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 System shutdown")