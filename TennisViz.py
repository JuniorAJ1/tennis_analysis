import json
import sys
import zipfile
import os

import csv
from datetime import datetime

# Load JSON
with open("1_1_2_1_1.json", "r") as f:
    data = json.load(f)

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
rows = []
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

    rows.append(row)

# Output CSV
columns = list(rows[0].keys()) if rows else []

with open("shot_by_shot_output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print("✅ Done! CSV saved as shot_by_shot_output.csv")
