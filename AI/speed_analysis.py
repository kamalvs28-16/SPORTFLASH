from ultralytics import YOLO
import cv2
import math
from collections import defaultdict

print("SPORTFLASH PLAYER SPEED ANALYSIS")
print("----------------------------------")

model = YOLO("yolo11n.pt")

video_path = "E:\\SPORTFLASH\\videos\\football.mp4"

cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")

# Store previous position of each player
previous_positions = {}

# Store speeds for each player
player_speeds = defaultdict(list)

frame_number = 0

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

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

    for box, player_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        # Player center
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        current_position = (center_x, center_y)

        if player_id in previous_positions:

            previous_x, previous_y = previous_positions[player_id]

            # Pixel movement between frames
            pixel_distance = math.sqrt(
                (center_x - previous_x) ** 2 +
                (center_y - previous_y) ** 2
            )

            # Time between frames
            time_seconds = 1 / fps

            # Pixel speed
            pixel_speed = pixel_distance / time_seconds

            player_speeds[player_id].append(pixel_speed)

        previous_positions[player_id] = current_position


cap.release()

print("\nPLAYER SPEED RESULTS")
print("--------------------")

for player_id, speeds in player_speeds.items():

    if len(speeds) == 0:
        continue

    average_speed = sum(speeds) / len(speeds)
    maximum_speed = max(speeds)

    print(f"\nPlayer {player_id}")
    print(f"Average Speed: {average_speed:.2f} pixels/sec")
    print(f"Maximum Speed: {maximum_speed:.2f} pixels/sec")

print("\nSpeed analysis completed!")