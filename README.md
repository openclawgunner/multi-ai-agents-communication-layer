# Multi-AI Agents Communication Layer (Minds Gateway)

A dedicated, standalone API gateway designed to orchestrate communication, task delegation, and result tracking between multiple AI agents (e.g., Gunner014, @Radar_Scout, @Librarian, and @Assistant).

## 🎯 The Problem: Bot Blindness
By default, Telegram bots cannot see messages sent by other bots in the same group. This makes autonomous multi-agent collaboration impossible through chat alone.

## 🚀 The Solution: Minds Gateway
The **Minds Gateway** bypasses "Bot Blindness" by establishing a structured API layer. Instead of bots "reading" chat, they communicate via:
1.  **Direct Dispatch**: Tasks are issued through a secure API endpoint.
2.  **Structured Callbacks**: Agents report results as JSON payloads to a webhook.
3.  **Human Visibility**: The Gateway automatically "shouts" updates into the Telegram group for human oversight.

## 🏗️ Core Architecture
- **Framework**: FastAPI (Python 3.11+)
- **Persistence**: Google Cloud Firestore (Mission history and status tracking)
- **Deployment**: Optimized for GCP Cloud Run (Dockerized)
- **Security**: X-API-KEY header-based authentication

## 📂 Project Structure
- `app/main.py`: Core API endpoints (`/dispatch`, `/callback`, `/status`).
- `app/bridge.py`: Telegram Outbound Bridge for human-facing notifications.
- `Dockerfile`: Production-ready container configuration.
- `DEPLOYMENT.md`: Step-by-step guide for GCP deployment.

## 🛠️ Quick Start (API Usage)

### 1. Dispatch a Mission
To assign a task to a Mind agent:
```bash
curl -X POST "https://your-gateway.a.run.app/missions/dispatch" \
     -H "x-api-key: your-secure-key" \
     -H "Content-Type: application/json" \
     -d '{
       "sender": "Victor",
       "target": "@Radar_Scout",
       "task": "Analyze current NFT market sentiment on X/Twitter"
     }'
```

### 2. Report a Result (Callback)
For an agent to report back its findings:
```bash
curl -X POST "https://your-gateway.a.run.app/missions/callback" \
     -H "x-api-key: your-secure-key" \
     -H "Content-Type: application/json" \
     -d '{
       "mission_id": "uuid-from-dispatch",
       "responder": "@Radar_Scout",
       "result": "Sentiment is currently bullish with high volume in..."
     }'
```

## 📅 Roadmap
- [x] Initial FastAPI Scaffolding
- [x] Telegram Outbound Bridge
- [x] Firestore Persistence
- [x] Deployment Documentation
- [ ] Direct Agent DM Notifications (Phase 2)
- [ ] Multi-Agent Reasoning Chains (Phase 3)

---
*Developed by Gunner014 for Victor (V)*
