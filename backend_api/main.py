from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import numpy as np
import os

app = FastAPI(
    title="Saarthi Lead Qualification API",
    description="Production-ready backend for hyper-personalised customer onboarding.",
    version="1.0.0"
)

# Define the local path where your model file should sit
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'saarthi_xgb_model.json')

# Request validation schema
class ChatTelemetry(BaseModel):
    session_id: str
    user_message: str
    features: list[float]  # Expects the 2,538 feature array

@app.get("/health")
async def health_check():
    """Verifies the backend server is up and the model file is detected."""
    model_exists = os.path.exists(MODEL_PATH)
    return {
        "status": "operational",
        "model_detected": model_exists,
        "environment": "development"
    }

@app.post("/api/v1/chat/message")
async def process_message(payload: ChatTelemetry):
    """Processes conversational telemetry and executes real-time lead scoring."""
    # 1. Validate feature length
    if len(payload.features) != 2538:
        raise HTTPException(
            status_code=400, 
            detail=f"Expected exactly 2538 features, received {len(payload.features)}"
        )

    # 2. Check for model and execute inference
    if os.path.exists(MODEL_PATH):
        try:
            # Load the model dynamically per request or on startup
            booster = xgb.Booster()
            booster.load_model(MODEL_PATH)
            
            # Formulate DMatrix for XGBoost
            data_matrix = xgb.DMatrix(np.array([payload.features]))
            conversion_prob = float(booster.predict(data_matrix)[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model execution failed: {str(e)}")
    else:
        # Fallback score if your teammate hits the API before you drop the json file in
        conversion_prob = 0.50

    # 3. Formulate Next Best Action response logic
    if conversion_prob < 0.60:
        action = "TRIGGER_AUTOCORRECT_AGENT"
        response_text = "It looks like there's an issue verifying your documents. Let's fix that right now."
    else:
        action = "PROCEED_TO_EKYC"
        response_text = "Perfect! Your profile looks great. Let's move forward with secure Aadhaar verification."

    return {
        "session_id": payload.session_id,
        "conversion_probability": round(conversion_prob, 4),
        "next_best_action": action,
        "agent_response": response_text
    }