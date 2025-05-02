import subprocess
import threading
import queue
import argparse
import os
import asyncio
from faster_whisper import WhisperModel
from analyzer import analyze_and_alert, client as discord_client

AUDIO_PIPE = "twitch_audio.wav"
CHUNK_DURATION = 15  # seconds
MODEL_SIZE = "base"

model = WhisperModel(MODEL_SIZE, compute_type="float32")

q = queue.Queue()

# Run ffmpeg to extract audio from stream
def start_audio_stream(url):
    print(f"[ffmpeg] Pulling audio from {url}")
    return subprocess.Popen([
        "ffmpeg",
        "-loglevel", "quiet",
        "-i", url,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        AUDIO_PIPE
    ])

# Generate clip from last recorded chunk
def generate_clip(chunk_file):
    mp4_file = chunk_file.replace(".wav", ".mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", chunk_file,
        "-c:v", "libx264", "-c:a", "aac",
        mp4_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return mp4_file

# Background transcription
def transcribe_loop():
    while True:
        if not q.empty():
            audio_file = q.get()
            segments, _ = model.transcribe(audio_file, beam_size=5)
            for seg in segments:
                print(f"[transcript] {seg.text}")
                if asyncio.run(analyze_and_alert(seg.text)):
                    clip_path = generate_clip(audio_file)
                    asyncio.run(post_clip_to_discord(clip_path))

async def post_clip_to_discord(clip_path):
    await discord_client.wait_until_ready()
    channel = discord_client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
    if channel:
        await channel.send(file=discord.File(clip_path))

# Continuously record short audio chunks from pipe
def record_chunks():
    counter = 0
    while True:
        chunk_file = f"chunk_{counter}.wav"
        subprocess.run([
            "ffmpeg", "-y", "-t", str(CHUNK_DURATION),
            "-i", AUDIO_PIPE, chunk_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        q.put(chunk_file)
        counter += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", help="Twitch stream URL", required=True)
    args = parser.parse_args()

    ffmpeg_proc = start_audio_stream(args.stream)

    transcriber_thread = threading.Thread(target=transcribe_loop, daemon=True)
    recorder_thread = threading.Thread(target=record_chunks, daemon=True)

    transcriber_thread.start()
    recorder_thread.start()

    try:
        asyncio.run(discord_client.start(os.getenv("DISCORD_TOKEN")))
    except KeyboardInterrupt:
        ffmpeg_proc.terminate()
        print("[!] Stopped.")
