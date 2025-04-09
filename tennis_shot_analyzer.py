import json
import sys
import zipfile
import os
import csv
from datetime import datetime
import re

# Helper function to get player position
def get_player_pos(samples, time, team):
    closest = min(samples, key=lambda s: abs(s["time"] - time))
    for p in closest.get("players", []):
        if p["team"] == team:
            return p["pos"]["x"], p["pos"]["y"]
    return None, None

# Helper function to get hit position
def get_hit_pos(samples, time):
    for s in samples:
        if s.get("event") == "hit" and abs(s["time"] - time) <= 0.01:
            pos = s.get("ball", {}).get("pos", {})
            return pos.get("x"), pos.get("y"), pos.get("z")
    return None, None, None

# Helper function to get next bounce position
def get_next_bounce_pos(samples, time):
    future_bounces = [s for s in samples if s.get("event") == "bounce" and s["time"] > time]
    if future_bounces:
        next_bounce = min(future_bounces, key=lambda s: s["time"])
        pos = next_bounce.get("ball", {}).get("pos", {})
        return pos.get("x"), pos.get("y")
    return None, None

# Process the JSON file to extract rows
def process_json_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    match = data["match"]
    season = match["season"]
    tournament_id = match["tournament_id"]
    draw_code = match["draw_code"]
    players = {p["team"]: p["external_id"] for p in match["players"]}

    seq = data["sequences"]
    set_no = seq["set"]
    game_no = seq["game"]
    point_no = seq["point"]
    serve_no = seq["serve"]
    rally_no = seq["rally"]

    samples = data["samples"]
    rows = []

    for shot in data.get("shots", []):
        time = shot.get("time", 0.0)
        duration = shot.get("duration", 0.0)
        time_utc = shot.get("time_utc")
        end_time_utc = None

        if time_utc and duration:
            try:
                start = datetime.fromisoformat(time_utc.replace("Z", "+00:00"))
                end_ts = start.timestamp() + duration
                end_time_utc = datetime.utcfromtimestamp(end_ts).isoformat() + "Z"
            except Exception as e:
                print(f"Warning: Failed to calculate end timestamp for shot at time {time}. Error: {e}")
                end_time_utc = None

        hitter_team = shot.get("team")
        receiver_team = 1 if hitter_team == 2 else 2

        hitter_x, hitter_y = get_player_pos(samples, time, hitter_team)
        receiver_x, receiver_y = get_player_pos(samples, time, receiver_team)
        ball_hit_x, ball_hit_y, ball_hit_z = get_hit_pos(samples, time)
        ball_bounce_x, ball_bounce_y = get_next_bounce_pos(samples, time)

        row = {
            "season": season,
            "tournament_id": tournament_id,
            "draw_code": draw_code,
            "set": set_no,
            "game": game_no,
            "point": point_no,
            "serve": serve_no,
            "rally": rally_no,
            "shot_no": shot.get("shot_no"),
            "hitter_external_id": players.get(hitter_team),
            "stroke": shot.get("stroke"),
            "spin_type": shot.get("spin", {}).get("type"),
            "spin_rpm": shot.get("spin", {}).get("rpm"),
            "speed_ms": shot.get("speed_ms"),
            "call": shot.get("call"),
            "shot_start_timestamp": time_utc,
            "shot_end_timestamp": end_time_utc,
            "ball_hit_x": ball_hit_x,
            "ball_hit_y": ball_hit_y,
            "ball_hit_z": ball_hit_z,
            "ball_bounce_x": ball_bounce_x,
            "ball_bounce_y": ball_bounce_y,
            "hitter_x": hitter_x,
            "hitter_y": hitter_y,
            "receiver_x": receiver_x,
            "receiver_y": receiver_y,
        }

        rows.append(row)

    return rows

# Function to sort files numerically
def numeric_key(filename):
    return [int(num) for num in re.findall(r'\d+', filename)]

def main():
    if len(sys.argv) != 3:
        print("Usage: python your_script.py <path_to_zip> <output_csv_name>")
        sys.exit(1)

    zip_path = sys.argv[1]
    output_csv = sys.argv[2]

    if not zipfile.is_zipfile(zip_path):
        print("Invalid ZIP file.")
        sys.exit(1)

    extract_dir = os.path.splitext(zip_path)[0]
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    json_dir = os.path.join(extract_dir, "data")

    if not os.path.exists(json_dir):
        print(f"❌ Expected 'data/' folder inside ZIP, but didn't find it at: {json_dir}")
        sys.exit(1)

    json_files = sorted(
        [f for f in os.listdir(json_dir) if f.endswith(".json")],
        key=numeric_key
    )

    all_rows = []
    for filename in json_files:
        file_path = os.path.join(json_dir, filename)
        try:
            rows = process_json_file(file_path)
            all_rows.extend(rows)
            print(f"✅ Processed: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to process {filename}: {e}")

    if all_rows:
        columns = list(all_rows[0].keys())
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"🎉 Done! All data written to {output_csv}")
    else:
        print("😕 No data found to write.")

if __name__ == "__main__":
    main()
