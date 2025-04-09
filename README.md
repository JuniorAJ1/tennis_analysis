🎾 Tennis Shot Analyzer
A Python tool to process and extract detailed shot-level data from zipped JSON files of tennis match telemetry. The output is a clean, structured CSV with information about each shot, including player positions, ball trajectory, shot type, and more.

📦 Input Format
This script expects a .zip archive containing one or more .json files. Each JSON file should follow the tennisviz_take_home_task_data format, containing metadata, player info, shots, events, and ball/player tracking data.

🏁 Output
A single CSV file named tennis_shots_combined.csv containing one row per shot, with the following fields:

Field	Description
season, tournament_id, draw_code	Match metadata
set, game, point, serve, rally, shot_no	Sequence context
hitter_external_id	Unique ID of the player who hit the shot
stroke	Type of shot (e.g., forehand, backhand)
spin_type, spin_rpm	Spin data, if available
speed_ms	Shot speed in meters/second
call	Line call for the shot (e.g., in, out)
shot_start_timestamp, shot_end_timestamp	UTC timestamps
ball_hit_x/y/z	3D position where ball was hit
ball_bounce_x/y	Position of next bounce after the shot
hitter_x/y, receiver_x/y	Nearest player positions at the time of the shot
▶️ Usage
bash
Copy
Edit
python tennis_shot_analyzer.py tennisviz_take_home_task_data.zip
Example Output
javascript
Copy
Edit
✅ Done! Combined CSV saved as tennis_shots_combined.csv  
Processed 12 JSON files
🧠 How It Works
Loads all .json files from the input ZIP.

For each shot:

Matches with nearest player positions at time of shot.

Identifies ball location at hit and next bounce.

Estimates end timestamp using shot duration.

Writes all extracted data into a single CSV for further analysis.

🛠 Requirements
Python 3.6+

No external dependencies beyond the standard library.

🧪 Tips
Handles malformed files gracefully.

Add your own analytics or visualizations on top of the output CSV.
