import feedparser
import requests
import time
import json
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Use environment variable for bot token
TELEGRAM_CHANNEL = "@alghurabaa01"  # Replace with your channel username
CHECK_INTERVAL = 10800  # 3 hours (in seconds)
LAST_VIDEO_FILE = "last_videos.json"

# Add YouTube Channel IDs here (find via https://commentpicker.com/youtube-channel-id.php)
YOUTUBE_CHANNEL_IDS = [
    "UC1YzRrrvxo5TJn_37RsR_8g",  # Example: "UCBa659QWEk1AI4Tg--mqJtQ" for Tom Scott
    "UCv_iCmNshOGpxHLgKNHB8Dw",
    "UCv3Hpjo6BuzfPvhebhmIwdg",
    "UCkcoIaXFhaHHJJEi9W8V_IA",
    "UC3-tHO0xzWGvYqUBxxAUh7g",
    "UCfS0Uy0CmrBxQHoyHfWM08w",
    "UCl_3GtLVGBu_eZLUEs8b3TQ",
    "UC6Ii_a_SowH8hlxdQhfwBlA",
]

def load_last_videos():
    try:
        with open(LAST_VIDEO_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_last_videos(last_videos):
    with open(LAST_VIDEO_FILE, "w") as f:
        json.dump(last_videos, f)

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHANNEL, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data)
        return response.ok
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return False

def process_channel(channel_id, last_videos):
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return
    
    channel_name = feed.feed.title
    last_seen_id = last_videos.get(channel_id)
    new_videos = []

    for entry in feed.entries:
        video_id = entry.yt_videoid
        if video_id == last_seen_id:
            break
        new_videos.append(entry)

    for video in reversed(new_videos):
        message = f"New video from {channel_name}:\n{video.title}\n{video.link}"
        if send_to_telegram(message):
            last_videos[channel_id] = video.yt_videoid

def main():
    last_videos = load_last_videos()
    for channel_id in YOUTUBE_CHANNEL_IDS:
        process_channel(channel_id, last_videos)
    save_last_videos(last_videos)

if __name__ == "__main__":
    while True:
        main()
        time.sleep(CHECK_INTERVAL)
