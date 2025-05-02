import subprocess
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", help="Twitch stream URL", required=True)
    args = parser.parse_args()

    try:
        print("[Launcher] Starting Dab Tracker system...")
        subprocess.run(["python", "stream_monitor.py", "--stream", args.stream])
    except KeyboardInterrupt:
        print("[Launcher] Shutdown requested. Exiting.")
