from ultralytics import YOLO
import cv2
from collections import defaultdict
import json
import os

print("SPORTFLASH FIELD ZONE ANALYSIS")
print("--------------------------------")

# Load YOLO model
model = YOLO("yolo11n.pt")

video_path = "E:\\SPORTFLASH\\videos\\football.mp4"

cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)

if fps == 0:
    fps = 30

print(f"Video FPS: {fps}")

# Store zone counts for each player
zone_counts = defaultdict(lambda: {
    "defensive": 0,
    "midfield": 0,
    "attacking": 0
})

frame_count = 0

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_count += 1

    results = model.track(
        frame,
        persist=True,
        conf=0.5,
        verbose=False
    )

    if results[0].boxes.id is None:
        continue

    boxes = results[0].boxes.xyxy.cpu().numpy()
    track_ids = results[0].boxes.id.int().cpu().tolist()

    height, width = frame.shape[:2]

    # Divide screen into 3 horizontal zones
    zone_height = height / 3

    for box, player_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        # Player center
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Determine zone
        if center_y < zone_height:

            zone = "attacking"

        elif center_y < zone_height * 2:

            zone = "midfield"

        else:

            zone = "defensive"

        zone_counts[player_id][zone] += 1

cap.release()

print("\nFIELD ZONE RESULTS")
print("------------------")

# Create results folder
os.makedirs("results", exist_ok=True)

zone_results = {}

for player_id, counts in zone_counts.items():

    total = sum(counts.values())

    if total == 0:
        continue

    defensive = counts["defensive"] / total * 100
    midfield = counts["midfield"] / total * 100
    attacking = counts["attacking"] / total * 100

    zone_results[str(player_id)] = {
        "defensive": round(defensive, 2),
        "midfield": round(midfield, 2),
        "attacking": round(attacking, 2)
    }

    print(f"\nPlayer {player_id}")

    print(f"Defensive : {defensive:.1f}%")
    print(f"Midfield  : {midfield:.1f}%")
    print(f"Attacking : {attacking:.1f}%")

# Save JSON
output_file = "results/zone_results.json"

with open(output_file, "w") as file:

    json.dump(
        zone_results,
        file,
        indent=4
    )

print("\nZone analysis completed!")

print(f"Results saved to:")
print(output_file)