from ultralytics import YOLO
import math

print("SPORTFLASH PERFORMANCE ANALYSIS")
print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO MODEL LOADED!")
print("Analyzing player performance...")

previous_positions = {}
total_distance = {}

results = model.track(
    source="E:\\SPORTFLASH\\videos\\football.mp4",
    stream=True,
    persist=True,
    conf=0.5
)

for result in results:

    if result.boxes.id is None:
        continue

    boxes = result.boxes.xyxy.cpu().numpy()
    track_ids = result.boxes.id.int().cpu().tolist()

    for box, track_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        current_position = (center_x, center_y)

        if track_id not in previous_positions:
            previous_positions[track_id] = current_position
            total_distance[track_id] = 0
            continue

        previous_x, previous_y = previous_positions[track_id]

        distance = math.sqrt(
            (center_x - previous_x) ** 2 +
            (center_y - previous_y) ** 2
        )

        total_distance[track_id] += distance

        previous_positions[track_id] = current_position


print("\nPLAYER PERFORMANCE")
print("------------------")

for player_id, distance in total_distance.items():

    # Activity classification
    if distance >= 2500:
        activity = "HIGH"
        score = 90
    elif distance >= 1000:
        activity = "MEDIUM"
        score = 70
    else:
        activity = "LOW"
        score = 50

    print(
        f"Player {player_id}: "
        f"{distance:.2f} pixels | "
        f"Activity: {activity} | "
        f"Score: {score}/100"
    )

print("\nPerformance analysis completed!")