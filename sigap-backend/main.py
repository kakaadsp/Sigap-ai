from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
import joblib
import random
import time
from datetime import datetime

app = FastAPI(title="SIGAP.AI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading AI Model and Scaler...")
try:
    model = tf.keras.models.load_model('sigap_model.h5', compile=False)
    scaler = joblib.load('sigap_scaler.save')
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")

# ==========================================
# 🧠 SIMULATION STATE
# ==========================================
class SimState:
    def __init__(self):
        self.base_volume = 300
        self.cooldown_until = 0

sim = SimState()

class ActionRequest(BaseModel):
    action: str

# ==========================================
# 🚦 MAIN ENDPOINTS
# ==========================================
@app.get("/")
def read_root():
    return {"message": "SIGAP.AI API is Running."}

@app.get("/api/traffic/live")
def get_live_traffic_prediction():
    current_time = time.time()

    # 1. SIMULATION LOGIC: congested vs free-flow
    if current_time < sim.cooldown_until:
        current_volume = random.randint(150, 250)
        sim.base_volume = current_volume
    else:
        sim.base_volume += random.randint(5, 20)
        if sim.base_volume > 580:
            sim.base_volume = 580
        current_volume = sim.base_volume

    current_speed = max(10.0, 60.0 - (current_volume / 10))

    # 2. AI PREDICTION
    dummy_sequence = []
    for _ in range(6):
        dummy_sequence.append([
            current_volume + random.randint(-10, 10),
            current_speed + random.uniform(-2, 2),
            0, 0
        ])

    scaled_sequence = scaler.transform(np.array(dummy_sequence))
    X_input = scaled_sequence.reshape(1, 6, 4)
    predicted_scaled = model.predict(X_input)

    dummy_inverse = np.zeros((1, 4))
    dummy_inverse[0, 0] = predicted_scaled[0][0]
    predicted_volume = int(scaler.inverse_transform(dummy_inverse)[0, 0])

    # 3. AI RECOMMENDATION LOGIC
    risk_percentage = min(int((predicted_volume / 600) * 100), 100)

    action = "Safe (No action needed)"
    status = "NORMAL"
    recommended_green = 45
    current_green = 45

    if predicted_volume > 450:
        action = "Extend Green Light Duration +20s"
        status = "DANGER"
        recommended_green = 65
    elif predicted_volume > 350:
        action = "Extend Green Light Duration +10s"
        status = "WARNING"
        recommended_green = 55

    # 4. DERIVED METRICS for dashboard
    queue_length = max(10, int(current_volume / 8) + random.randint(-3, 5))
    wait_time_mins = max(2, int(current_volume / 40) + random.randint(-1, 2))
    avg_speed = round(current_speed + random.uniform(-2, 2), 1)
    system_confidence = max(85, min(99, 100 - int(risk_percentage / 10)))

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "status": status,
        "current_conditions": {
            "volume": int(current_volume),
            "speed_kmh": round(current_speed, 1)
        },
        "prediction_15_mins": {
            "predicted_volume": predicted_volume,
            "risk_level": risk_percentage,
            "recommended_action": action
        },
        "queue_length": queue_length,
        "wait_time_mins": wait_time_mins,
        "weather": {
            "temp": 30,
            "condition": "Sunny, Clear visibility"
        },
        "avg_speed_kmh": avg_speed,
        "accidents": 0,
        "system_confidence": system_confidence,
        "peak_forecast": "17:45",
        "current_green_duration": current_green,
        "recommended_green_duration": recommended_green
    }

# ==========================================
# 🚨 ACTION ENDPOINT
# ==========================================
@app.post("/api/action/apply")
def apply_action(req: ActionRequest):
    sim.cooldown_until = time.time() + 60
    sim.base_volume = 200
    return {
        "status": "success",
        "message": f"Action '{req.action}' applied successfully! AI has modified traffic signal timing. Vehicle volume is expected to decrease shortly."
    }