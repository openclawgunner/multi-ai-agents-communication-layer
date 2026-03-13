import os
import uuid
import time
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from app.bridge import TelegramBridge

# Create logs directory
LOG_DIR = os.path.join(os.getcwd(), "logs", "missions")
os.makedirs(LOG_DIR, exist_ok=True)

def log_mission_event(mission_id: str, event_type: str, content: str):
    """Saves a human-readable markdown log of the mission conversation."""
    filename = f"MISSION_{mission_id}.md"
    filepath = os.path.join(LOG_DIR, filename)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filepath, "a") as f:
        if event_type == "dispatch":
            f.write(f"# Mission Log: {mission_id}\n\n")
            f.write(f"### [ {timestamp} ] DISPATCHED\n")
        else:
            f.write(f"\n### [ {timestamp} ] {event_type.upper()}\n")
        f.write(f"{content}\n---\n")

# Firestore integration
try:
    from google.cloud import firestore
    # Initialize Firestore Client pointing to the dedicated database
    db = firestore.Client(database="agents-comms")
    missions_ref = db.collection("minds_missions")
    HAS_FIRESTORE = True
except Exception as e:
    print(f"Firestore (agents-comms) not configured, falling back to mock: {e}")
    HAS_FIRESTORE = False
    active_missions = {}

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
    
    if HAS_FIRESTORE:
        missions_ref.document(mission.id).set(mission.model_dump())
    else:
        active_missions[mission.id] = mission
    
    # Log the mission narrative locally
    dispatch_msg = f"**Sender:** {mission.sender}\n**Target:** {mission.target}\n**Task:** {mission.task}"
    log_mission_event(mission.id, "dispatch", dispatch_msg)
    
    # Announce the mission in the group for human visibility
    tg_bridge.announce_mission(mission.id, mission.sender, mission.target, mission.task)
    
    return mission

@app.post("/missions/callback")
async def mission_callback(response: MissionResponse, auth: str = Depends(verify_api_key)):
    """A Mind reports its results back to the Gateway."""
    
    if HAS_FIRESTORE:
        doc_ref = missions_ref.document(response.mission_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Mission ID not found")
        doc_ref.update({"status": "completed", "result": response.result})
    else:
        if response.mission_id not in active_missions:
            raise HTTPException(status_code=404, detail="Mission ID not found")
        mission = active_missions[response.mission_id]
        mission.status = "completed"
    
    # Log the result narrative locally
    callback_msg = f"**Responder:** {response.responder}\n**Result:** {response.result}"
    log_mission_event(response.mission_id, "callback", callback_msg)
    
    # Announce the completion in the group for human visibility
    tg_bridge.announce_completion(response.mission_id, response.responder, response.result)
    
    return {"status": "success", "message": f"Result received for mission {response.mission_id}"}

@app.get("/missions/status/{mission_id}")
async def get_mission_status(mission_id: str):
    """Check the progress of a delegated task."""
    if HAS_FIRESTORE:
        doc = missions_ref.document(mission_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Mission ID not found")
        return doc.to_dict()
    else:
        if mission_id not in active_missions:
            raise HTTPException(status_code=404, detail="Mission ID not found")
        return active_missions[mission_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
