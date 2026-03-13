import os
import uuid
import time
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from app.bridge import TelegramBridge

app = FastAPI(title="Minds Gateway - AI Agent Communication Layer")

# Initialize Telegram Bridge
# We'll need these env vars set: TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_CHAT_ID
tg_bridge = TelegramBridge()

# --- Schemas ---
class Mission(BaseModel):
    id: str = str(uuid.uuid4())
    sender: str  # Gunner014, Victor, or a Mind
    target: str  # @Radar_Scout, @Librarian, etc.
    task: str
    priority: int = 1
    timestamp: float = time.time()
    status: str = "dispatched" # dispatched, processing, completed, failed

class MissionResponse(BaseModel):
    mission_id: str
    responder: str
    result: str
    metadata: Optional[dict] = None

# --- Mock Database (Replace with Firestore/Redis later) ---
active_missions = {}

# --- Security (Simple Key for Phase 1) ---
API_KEY = "v-minds-secure-key-2026" # To be moved to env vars

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

# --- Endpoints ---

@app.get("/")
async def root():
    return {"status": "Minds Gateway Active", "active_missions_count": len(active_missions)}

@app.post("/missions/dispatch", response_model=Mission)
async def dispatch_mission(mission: Mission, auth: str = Depends(verify_api_key)):
    """Gunner014 or Victor assigns a task to a Mind."""
    active_missions[mission.id] = mission
    
    # Announce the mission in the group for human visibility
    tg_bridge.announce_mission(mission.id, mission.sender, mission.target, mission.task)
    
    # TODO: In Phase 2, we can also send a direct notification to the Mind via its specific endpoint
    return mission

@app.post("/missions/callback")
async def mission_callback(response: MissionResponse, auth: str = Depends(verify_api_key)):
    """A Mind reports its results back to the Gateway."""
    if response.mission_id not in active_missions:
        raise HTTPException(status_code=404, detail="Mission ID not found")
    
    # Update mission status
    mission = active_missions[response.mission_id]
    mission.status = "completed"
    
    # Announce the completion in the group for human visibility
    tg_bridge.announce_completion(response.mission_id, response.responder, response.result)
    
    return {"status": "success", "message": f"Result received for mission {response.mission_id}"}

@app.get("/missions/status/{mission_id}")
async def get_mission_status(mission_id: str):
    """Check the progress of a delegated task."""
    if mission_id not in active_missions:
        raise HTTPException(status_code=404, detail="Mission ID not found")
    return active_missions[mission_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
