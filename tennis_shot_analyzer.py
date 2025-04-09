import json
import csv
import sys
import zipfile
from datetime import datetime
from io import TextIOWrapper

def process_json_file(json_file, writer):
    """Process a single JSON file and write its data to the CSV writer"""
    data = json.load(json_file)
    
    # Match metadata
    match = data["match"]
    season = match["season"]
    tournament_id = match["tournament_id"]
    draw_code = match["draw_code"]
    players = {p["team"]: p["external_id"] for p in match["players"]}

    # Sequence metadata
    seq = data["sequences"]
    set_no = seq["set"]
    game_no = seq["game"]
    point_no = seq["point"]
    serve_no = seq["serve"]
    rally_no = seq["rally"]

    samples = data["samples"]

    # Get nearest player positions
    def get_player_pos(time, team):
        closest = min(samples, key=lambda s: abs(s["time"] - time))
        for p in closest.get("players", []):
            if p["team"] == team:
                return p["pos"]["x"], p["pos"]["y"]
        return None, None

    # Get hit position at exact time
    def get_hit_pos(time):
        for s in samples:
            if s.get("event") == "hit" and abs(s["time"] - time) <= 0.01:
                pos = s.get("ball", {}).get("pos", {})
                return pos.get("x"), pos.get("y"), pos.get("z")
        return None, None, None

    # Get next bounce after shot
    def get_next_bounce_pos(time):
        future_bounces = [s for s in samples if s.get("event") == "bounce" and s["time"] > time]
        if future_bounces:
            next_bounce = min(future_bounces, key=lambda s: s["time"])
            pos = next_bounce.get("ball", {}).get("pos", {})
            return pos.get("x"), pos.get("y")
        return None, None

    # Process shots
    for shot in data.get("shots", []):
        time = shot.get("time", 0.0)
        duration = shot.get("duration", 0.0)
        time_utc = shot.get("time_utc")
        end_time_utc = None

        # Estimate end time
        if time_utc and duration:
            try:
                start = datetime.fromisoformat(time_utc.replace("Z", "+00:00"))
                end_ts = start.timestamp() + duration
                end_time_utc = datetime.utcfromtimestamp(end_ts).isoformat() + "Z"
            except:
                end_time_utc = None

        # Who hit / received
        hitter_team = shot.get("team")
        receiver_team = 1 if hitter_team == 2 else 2

        hitter_x, hitter_y = get_player_pos(time, hitter_team)
        receiver_x, receiver_y = get_player_pos(time, receiver_team)
        ball_hit_x, ball_hit_y, ball_hit_z = get_hit_pos(time)
        ball_bounce_x, ball_bounce_y = get_next_bounce_pos(time)

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

        writer.writerow(row)

def main():
    if len(sys.argv) != 2:
        print("Usage: python process_tennis_data.py tennisviz_take_home_task_data.zip")
        sys.exit(1)

    zip_path = sys.argv[1]
    output_csv = "tennis_shots_combined.csv"

    with zipfile.ZipFile(zip_path, 'r') as z:
        # Get all JSON files in the zip
        json_files = [f for f in z.namelist() if f.endswith('.json')]
        
        if not json_files:
            print("No JSON files found in the zip archive")
            return

        # Open CSV file for writing
        with open(output_csv, 'w', newline='') as csvfile:
            # Initialize CSV writer with fieldnames from first JSON file
            with z.open(json_files[0]) as first_file:
                first_data = json.load(TextIOWrapper(first_file, 'utf-8'))
                first_shot = first_data.get("shots", [{}])[0]
                
                # Build fieldnames based on the first shot
                fieldnames = [
                    "season", "tournament_id", "draw_code", "set", "game", "point", 
                    "serve", "rally", "shot_no", "hitter_external_id", "stroke",
                    "spin_type", "spin_rpm", "speed_ms", "call", "shot_start_timestamp",
                    "shot_end_timestamp", "ball_hit_x", "ball_hit_y", "ball_hit_z",
                    "ball_bounce_x", "ball_bounce_y", "hitter_x", "hitter_y",
                    "receiver_x", "receiver_y"
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            # Process all JSON files
            for json_file in json_files:
                try:
                    with z.open(json_file) as f:
                        process_json_file(TextIOWrapper(f, 'utf-8'), writer)
                except Exception as e:
                    print(f"Error processing {json_file}: {str(e)}")
                    continue

    print(f"✅ Done! Combined CSV saved as {output_csv}")
    print(f"Processed {len(json_files)} JSON files")

if __name__ == "__main__":
    main()
