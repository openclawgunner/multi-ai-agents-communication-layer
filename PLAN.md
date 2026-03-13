# Minds Gateway (AI Agent Communication Layer)

## 🎯 Goal
Establish a dedicated, standalone communication layer between Victor (V), Gunner014, and the **Integrated Minds** (@Radar_Scout, @Librarian, @Assistant). This serves as the "Orchestrator" for inter-agent task delegation and multi-agent reasoning.

## 🏗️ Architecture (Phase 1)
- **Framework:** FastAPI (Independent from NetSuite repo).
- **Communication Protocol:** 
  - **Inbound:** Webhook listeners for the Minds (Telegram/Minds Platform).
  - **Outbound:** Secure Proxy to dispatch tasks to the Minds via API/Telegram.
- **State Management:** Redis or Firestore to track active "Missions" and their statuses.
- **Security:** `X-API-KEY` authentication for all agent-to-agent calls.

## 🛠️ Core Endpoints (Proposed)
1. `POST /missions/dispatch`: Gunner014 or V assigns a task to a specific Mind.
2. `POST /missions/callback`: A Mind reports its results back to the Gateway.
3. `GET /missions/status/{id}`: Check the progress of a delegated task.
4. `POST /broadcast`: Issue instructions to all Minds simultaneously (e.g., "Enter Silent Standby").

## 📂 Project Structure
- `projects/minds-gateway/`
  - `app/main.py` (FastAPI Entry)
  - `app/routes/missions.py` (Dispatch/Callback logic)
  - `app/auth.py` (Security)
  - `Dockerfile` (Container for Cloud Run)
  - `requirements.txt`

## 📅 Immediate Next Steps
1. [ ] Finalize the API Schema for the "Mission" object.
2. [ ] Set up the FastAPI scaffolding.
3. [ ] Configure a secure tunnel (or Cloud Run) to expose the Gateway to the Minds.
