import os
import requests
import logging
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBridge:
    """
    Bridges the Minds Gateway to Telegram.
    This allows the Gateway to 'shout' missions into the group chat
    and send Direct Messages to individual Mind bots.
    """
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_GROUP_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text: str, target_chat_id: Optional[str] = None):
        """Sends a message to a specific chat or the default group."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": target_chat_id or self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return None

    def announce_mission(self, mission_id: str, sender: str, target: str, task: str):
        """Announces a new mission in the group chat for human visibility."""
        text = (
            f"🚀 *New Mission Dispatched*\n"
            f"🆔 `ID: {mission_id}`\n"
            f"👤 *From:* {sender}\n"
            f"🤖 *Target:* {target}\n"
            f"📝 *Task:* {task}\n"
            f"⏳ *Status:* Waiting for callback..."
        )
        return self.send_message(text)

    def announce_completion(self, mission_id: str, responder: str, result: str):
        """Announces a mission completion for human visibility."""
        text = (
            f"✅ *Mission Completed*\n"
            f"🆔 `ID: {mission_id}`\n"
            f"🤖 *By:* {responder}\n"
            f"📊 *Result:* {result}"
        )
        return self.send_message(text)

# Example usage (standalone)
if __name__ == "__main__":
    # This is just for testing
    bridge = TelegramBridge()
    # bridge.announce_mission("test-123", "Gunner014", "@Radar_Scout", "Scan for NFT trends")
