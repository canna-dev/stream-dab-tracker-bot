# Stream Dab Tracker Bot

A real-time Twitch dab trigger system with AI and Discord integration.

## 🔥 Features
- Real-time transcription from any Twitch stream
- GPT-4 and keyword-based political trigger detection
- Discord bot with slash commands and dropdowns
- 15-second rewind clip generation and upload
- Difficulty control via `/setdifficulty`
- Trigger list management via `trigger_keywords.json`

---

## 📦 Requirements
- Python 3.10+
- FFmpeg installed and in PATH
- Discord bot token & channel ID
- OpenAI API key (GPT-4)

Install dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file:
```dotenv
DISCORD_TOKEN=your_discord_token
DISCORD_CHANNEL_ID=your_channel_id
OPENAI_API_KEY=your_openai_api_key
```

Set your config:
```json
{
  "clip_length": 15,
  "default_stream_url": "",
  "trigger_keywords_file": "trigger_keywords.json",
  "difficulty": "medium"
}
```

---

## 🚀 Run
Launch the tracker with:
```bash
python launcher.py --stream https://twitch.tv/yourtarget
```

---

## 🔧 Discord Commands
- `/setdifficulty` → Dropdown to select Easy/Medium/Hard
- `/resetdifficulty` → Resets to default

---

## 📂 Project Structure
- `stream_monitor.py` – Audio capture, transcription, trigger detection
- `analyzer.py` – GPT + keyword analysis, sends alerts
- `discord_bot.py` – Slash commands, difficulty selection
- `launcher.py` – One-line launcher

---

## 🛑 Notes
- Uses `faster-whisper` for real-time transcription
- All clips and audio chunks saved locally
- GPT calls are rate-limited by your OpenAI plan

---

## 📎 License
MIT
