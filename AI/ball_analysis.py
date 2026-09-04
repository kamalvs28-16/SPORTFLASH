from ultralytics import YOLO
import cv2
import json
import os
import math

print("======================================")
print(" SPORTFLASH BALL ANALYSIS")
print("======================================")

# --------------------------------------------------
# LOAD YOLO MODEL
# --------------------------------------------------

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO model loaded!")

# --------------------------------------------------
# VIDEO
# --------------------------------------------------

video_path = "E:\\SPORTFLASH\\videos\\football.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")

# --------------------------------------------------
# DATA
# --------------------------------------------------

ball_positions = []

ball_speeds = []

player_positions = {}

interactions = []

frame_number = 0

# Maximum distance in pixels for possible interaction
INTERACTION_DISTANCE = 120

# --------------------------------------------------
# PROCESS VIDEO
# --------------------------------------------------

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    results = model.track(
        frame,
        persist=True,
        conf=0.25,
        verbose=False
    )

    result = results[0]

    if result.boxes is None:
        continue

    boxes = result.boxes.xyxy.cpu().numpy()

    classes = result.boxes.cls.cpu().numpy()

    track_ids = None

    if result.boxes.id is not None:
        track_ids = result.boxes.id.int().cpu().tolist()

    current_ball = None
    current_players = []

    # --------------------------------------------------
    # DETECT OBJECTS
    # --------------------------------------------------

    for index, box in enumerate(boxes):

        x1, y1, x2, y2 = box

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        class_id = int(classes[index])

        # COCO:
        # 0 = person
        # 32 = sports ball
        #
        # YOLO11n COCO model uses class 32 for sports ball.

        if class_id == 32:

            current_ball = (
                float(center_x),
                float(center_y)
            )

        elif class_id == 0:

            if track_ids is not None:

                player_id = track_ids[index]

                current_players.append(
                    (
                        player_id,
                        float(center_x),
                        float(center_y)
                    )
                )

    # --------------------------------------------------
    # STORE PLAYER POSITIONS
    # --------------------------------------------------

    for player_id, x, y in current_players:

        if player_id not in player_positions:

            player_positions[player_id] = []

        player_positions[player_id].append(
            (
                frame_number,
                x,
                y
            )
        )

    # --------------------------------------------------
    # BALL POSITION
    # --------------------------------------------------

    if current_ball is not None:

        ball_x, ball_y = current_ball

        ball_positions.append(
            (
                frame_number,
                ball_x,
                ball_y
            )
        )

        # --------------------------------------------------
        # BALL SPEED
        # --------------------------------------------------

        if len(ball_positions) >= 2:

            previous_frame, previous_x, previous_y = (
                ball_positions[-2]
            )

            current_frame, current_x, current_y = (
                ball_positions[-1]
            )

            distance = math.sqrt(
                (current_x - previous_x) ** 2 +
                (current_y - previous_y) ** 2
            )

            frame_difference = (
                current_frame - previous_frame
            )

            if frame_difference > 0:

                time_seconds = frame_difference / fps

                speed = distance / time_seconds

                ball_speeds.append(speed)

        # --------------------------------------------------
        # PLAYER-BALL INTERACTION
        # --------------------------------------------------

        for player_id, player_x, player_y in current_players:

            distance_to_ball = math.sqrt(
                (player_x - ball_x) ** 2 +
                (player_y - ball_y) ** 2
            )

            if distance_to_ball <= INTERACTION_DISTANCE:

                interactions.append(
                    {
                        "frame": frame_number,
                        "player_id": int(player_id),
                        "distance_pixels": round(
                            distance_to_ball,
                            2
                        )
                    }
                )

# --------------------------------------------------
# RELEASE VIDEO
# --------------------------------------------------

cap.release()

# --------------------------------------------------
# CALCULATE RESULTS
# --------------------------------------------------

print("\n======================================")
print(" BALL ANALYSIS RESULTS")
print("======================================")

# Ball speed
if ball_speeds:

    average_ball_speed = (
        sum(ball_speeds) / len(ball_speeds)
    )

    maximum_ball_speed = max(ball_speeds)

else:

    average_ball_speed = 0
    maximum_ball_speed = 0

# --------------------------------------------------
# REMOVE DUPLICATE INTERACTION EVENTS
# --------------------------------------------------

unique_interactions = []

last_interaction = {}

for interaction in interactions:

    player_id = interaction["player_id"]

    frame = interaction["frame"]

    # Avoid counting the same player every frame
    if player_id not in last_interaction:

        unique_interactions.append(interaction)

        last_interaction[player_id] = frame

    else:

        previous_frame = last_interaction[player_id]

        # Require at least 30 frames between events
        if frame - previous_frame >= 30:

            unique_interactions.append(interaction)

            last_interaction[player_id] = frame

# --------------------------------------------------
# INTERACTION COUNT BY PLAYER
# --------------------------------------------------

interaction_counts = {}

for interaction in unique_interactions:

    player_id = str(
        interaction["player_id"]
    )

    if player_id not in interaction_counts:

        interaction_counts[player_id] = 0

    interaction_counts[player_id] += 1

# --------------------------------------------------
# PRINT RESULTS
# --------------------------------------------------

print(
    f"Ball positions detected: "
    f"{len(ball_positions)}"
)

print(
    f"Average ball speed: "
    f"{average_ball_speed:.2f} pixels/sec"
)

print(
    f"Maximum ball speed: "
    f"{maximum_ball_speed:.2f} pixels/sec"
)

print(
    f"Possible player-ball interactions: "
    f"{len(unique_interactions)}"
)

if interaction_counts:

    print("\nPLAYER-BALL INTERACTIONS")

    for player_id, count in sorted(
        interaction_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"Player {player_id}: "
            f"{count} interaction(s)"
        )

else:

    print(
        "\nNo player-ball interactions "
        "detected with the current threshold."
    )

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

os.makedirs(
    "results",
    exist_ok=True
)

output_data = {

    "ball_positions_detected":
        len(ball_positions),

    "average_ball_speed_pixels_per_second":
        round(average_ball_speed, 2),

    "maximum_ball_speed_pixels_per_second":
        round(maximum_ball_speed, 2),

    "total_player_ball_interactions":
        len(unique_interactions),

    "interaction_counts":
        interaction_counts,

    "interactions":
        unique_interactions
}

output_file = (
    "results/ball_results.json"
)

with open(
    output_file,
    "w"
) as file:

    json.dump(
        output_data,
        file,
        indent=4
    )

print("\n======================================")
print(" BALL ANALYSIS COMPLETED")
print("======================================")

print(
    f"Results saved to: {output_file}"
)