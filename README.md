Tennis Match Data Processor
A Python script that processes tennis match tracking data from JSON files and generates comprehensive shot-by-shot analytics in CSV format.

Features
Batch Processing: Handles multiple match files packaged in a ZIP archive

Detailed Shot Analysis: Extracts 25+ metrics per shot including:

Ball trajectory (hit position, bounce position)

Player positions (hitter and receiver coordinates)

Stroke characteristics (spin type, speed, call outcome)

Match context (set, game, point, serve numbers)

Command Line Interface: Simple one-command execution

Data Consolidation: Combines data from multiple matches into a single CSV

Technical Details
Processes official tennis match tracking data format

Handles complex JSON structures with nested event data

Precise temporal-spatial calculations for shot events

Memory-efficient streaming processing of large datasets

Example Usage
bash
Copy
python process_tennis_data.py tournament_matches.zip
Outputs: tennis_shots_combined.csv with all match data

Use Cases
Tennis analytics platforms

Coach performance analysis tools

Broadcast visualization systems

Player development tracking
