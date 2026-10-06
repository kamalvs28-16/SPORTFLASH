from ultralytics import YOLO
import cv2
import math
import statistics

print("======================================")
print(" SPORTFLASH BALL SPEED ANALYSIS")
print("======================================")

# ---------------------------------------
# SETTINGS
# ---------------------------------------

MODEL_PATH = "yolo11n.pt"
VIDEO_PATH = "E:\\SPORTFLASH\\videos\\football.mp4"

# Approximate average player height
PLAYER_HEIGHT_M = 1.75

# Remove unrealistic detection jumps
MAX_BALL_SPEED_KMH = 120.0

# Minimum player bounding-box height
MIN_PLAYER_HEIGHT_PIXELS = 40

# ---------------------------------------
# LOAD MODEL
# ---------------------------------------

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully.")

# ---------------------------------------
# OPEN VIDEO
# ---------------------------------------

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Could not open football video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")

# ---------------------------------------
# VARIABLES
# ---------------------------------------

previous_ball_position = None
previous_ball_frame = None

ball_speeds = []
ball_distances = []

frame_number = 0
ball_detection_count = 0

# ---------------------------------------
# PROCESS VIDEO
# ---------------------------------------

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

    ball_position = None

    # -----------------------------------
    # GET PLAYER HEIGHTS
    # -----------------------------------

    player_heights = []

    if results[0].boxes is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()

        for box, class_id in zip(boxes, classes):

            class_name = model.names[int(class_id)]

            if class_name == "person":

                x1, y1, x2, y2 = box

                player_height_pixels = y2 - y1

                if player_height_pixels >= MIN_PLAYER_HEIGHT_PIXELS:
                    player_heights.append(
                        player_height_pixels
                    )

    # -----------------------------------
    # FIND BALL
    # -----------------------------------

    if results[0].boxes is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()

        for box, class_id in zip(boxes, classes):

            class_name = model.names[int(class_id)]

            if class_name == "sports ball":

                x1, y1, x2, y2 = box

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                ball_position = (
                    center_x,
                    center_y
                )

                ball_detection_count += 1

                break

    # -----------------------------------
    # CALCULATE BALL SPEED
    # -----------------------------------

    if ball_position is not None:

        current_x, current_y = ball_position

        if (
            previous_ball_position is not None
            and previous_ball_frame is not None
        ):

            previous_x, previous_y = (
                previous_ball_position
            )

            # Pixel distance
            pixel_distance = math.sqrt(
                (current_x - previous_x) ** 2 +
                (current_y - previous_y) ** 2
            )

            # Number of frames between detections
            frame_difference = (
                frame_number -
                previous_ball_frame
            )

            if frame_difference > 0:

                # Time between detections
                time_seconds = (
                    frame_difference / fps
                )

                # --------------------------------
                # ESTIMATE PIXEL → METER SCALE
                # --------------------------------

                if len(player_heights) > 0:

                    median_player_height = statistics.median(
                        player_heights
                    )

                    meters_per_pixel = (
                        PLAYER_HEIGHT_M /
                        median_player_height
                    )

                else:

                    # Fallback scale
                    meters_per_pixel = 0.01

                # --------------------------------
                # DISTANCE IN METERS
                # --------------------------------

                distance_m = (
                    pixel_distance *
                    meters_per_pixel
                )

                # --------------------------------
                # SPEED
                # --------------------------------

                speed_mps = (
                    distance_m /
                    time_seconds
                )

                speed_kmh = (
                    speed_mps * 3.6
                )

                # --------------------------------
                # FILTER BAD DETECTIONS
                # --------------------------------

                if speed_kmh <= MAX_BALL_SPEED_KMH:

                    ball_speeds.append(
                        speed_kmh
                    )

                    ball_distances.append(
                        distance_m
                    )

        previous_ball_position = ball_position
        previous_ball_frame = frame_number

# ---------------------------------------
# CLOSE VIDEO
# ---------------------------------------

cap.release()

# ---------------------------------------
# RESULTS
# ---------------------------------------

print("\n")
print("======================================")
print(" SPORTFLASH BALL SPEED RESULTS")
print("======================================")

print(
    f"Frames processed: {frame_number}"
)

print(
    f"Ball detections: {ball_detection_count}"
)

if len(ball_speeds) > 0:

    total_distance = sum(ball_distances)

    average_speed = (
        sum(ball_speeds) /
        len(ball_speeds)
    )

    maximum_speed = max(ball_speeds)

    print(
        f"Ball Distance: "
        f"{total_distance:.2f} m"
    )

    print(
        f"Average Ball Speed: "
        f"{average_speed:.2f} km/h"
    )

    print(
        f"Maximum Ball Speed: "
        f"{maximum_speed:.2f} km/h"
    )

    print(
        f"Valid Speed Measurements: "
        f"{len(ball_speeds)}"
    )

else:

    print("No valid ball speed measurements found.")

print("\n======================================")
print("Ball speed analysis completed!")
print("======================================")