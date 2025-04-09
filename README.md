# 🎾 Tennis Shot Analyzer

*A Python tool to process detailed shot-level data from zipped JSON files of tennis matches.*

---

## 📦 Input Format

This script expects a `.zip` file containing one or more `.json` files formatted according to the `tennisviz_take_home_task_data` spec. Each file includes:

- Match metadata
- Player information
- Shot-by-shot tracking
- Ball and player positional data

---

## 🏁 Output

Generates a single CSV file:  
**`tennis_shots_combined.csv`**

Each row = one shot with the following fields:

| **Field** | **Description** |
|-----------|-----------------|
| `season`, `tournament_id`, `draw_code` | Match metadata |
| `set`, `game`, `point`, `serve`, `rally`, `shot_no` | Sequence identifiers |
| `hitter_external_id` | Player who hit the shot |
| `stroke` | Shot type (e.g., forehand, backhand) |
| `spin_type`, `spin_rpm` | Spin data |
| `speed_ms` | Speed of shot (m/s) |
| `call` | Line call (in/out) |
| `shot_start_timestamp`, `shot_end_timestamp` | UTC time window |
| `ball_hit_x/y/z` | 3D hit location |
| `ball_bounce_x/y` | Next bounce position |
| `hitter_x/y`, `receiver_x/y` | Player positions at shot time |

---

## ▶️ How to Run

```bash
python tennis_shot_analyzer.py tennisviz_take_home_task_data.zip
