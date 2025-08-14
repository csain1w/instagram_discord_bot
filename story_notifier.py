import instaloader
import requests
import time
import os
from datetime import datetime

# --- CONFIG ---
USERNAME = os.environ.get("IG_USERNAME")  # Instagram login (set in Render)
PASSWORD = os.environ.get("IG_PASSWORD")  # Instagram password (set in Render)
TARGET_USER = "nba"  # Account to monitor
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")  # Set in Render
CHECK_INTERVAL = 60  # seconds between checks
# --------------

# Initialize Instaloader
L = instaloader.Instaloader()
L.login(USERNAME, PASSWORD)

seen_story_ids = set()

def send_discord_message(content):
    data = {"content": content}
    requests.post(WEBHOOK_URL, json=data)

def check_stories():
    global seen_story_ids

    try:
        profile = instaloader.Profile.from_username(L.context, TARGET_USER)
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                if item.mediaid not in seen_story_ids:
                    seen_story_ids.add(item.mediaid)
                    story_time = item.date_local.strftime("%Y-%m-%d %H:%M:%S")
                    story_url = f"https://www.instagram.com/stories/{TARGET_USER}/{item.mediaid}/"
                    message = f"📢 **{TARGET_USER}** posted a new story at {story_time}!\n{story_url}"
                    send_discord_message(message)
                    print(f"[{datetime.now()}] New story found and sent to Discord.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    print(f"Monitoring @{TARGET_USER} for new stories...")
    while True:
        check_stories()
        time.sleep(CHECK_INTERVAL)
