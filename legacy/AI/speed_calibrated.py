import cv2
import json
import os
import numpy as np
from collections import defaultdict, deque
from ultralytics import YOLO


# ============================================================
# SPORTFLASH - ROBUST PLAYER SPEED ANALYSIS
# ============================================================

print("=" * 60)
print("       SPORTFLASH PLAYER SPEED ANALYSIS")
print("=" * 60)


# ============================================================
# PATHS
# ============================================================

VIDEO_PATH = r"E:\SPORTFLASH\videos\football.mp4"
MODEL_PATH = r"E:\SPORTFLASH\yolo11n.pt"
RESULTS_DIR = r"E:\SPORTFLASH\results"

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "speed_results.json"
)


# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE = 0.5

# Number of speed values used for smoothing
SMOOTHING_WINDOW = 5

# Ignore extremely large frame-to-frame tracking jumps.
# This is PIXELS/SECOND, not km/h.
MAX_PIXEL_SPEED = 3000.0

# Ignore very small movement caused by detection noise.
MIN_PIXEL_DISTANCE = 0.5


# ============================================================
# CREATE RESULTS DIRECTORY
# ============================================================

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ============================================================
# LOAD YOLO
# ============================================================

print("\nLoading YOLO model...")

model = YOLO(
    MODEL_PATH
)

print("YOLO model loaded successfully.")


# ============================================================
# OPEN VIDEO
# ============================================================

print("\nOpening football video...")

cap = cv2.VideoCapture(
    VIDEO_PATH
)

if not cap.isOpened():

    print("ERROR: Could not open video.")

    exit()


fps = cap.get(
    cv2.CAP_PROP_FPS
)

if fps <= 0:

    fps = 30.0


total_frames = int(
    cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)


print(
    f"Video FPS: {fps:.2f}"
)

print(
    f"Total Frames: {total_frames}"
)


# ============================================================
# PLAYER DATA
# ============================================================

previous_positions = {}

speed_history = defaultdict(
    lambda: deque(
        maxlen=SMOOTHING_WINDOW
    )
)

player_speeds = defaultdict(list)

player_detection_count = defaultdict(int)


# ============================================================
# STATISTICS
# ============================================================

frame_count = 0
accepted_speeds = 0
rejected_speeds = 0


# ============================================================
# PROCESS VIDEO
# ============================================================

print("\nStarting player tracking...")
print("Please wait...\n")


while True:

    success, frame = cap.read()

    if not success:
        break

    frame_count += 1


    # --------------------------------------------------------
    # YOLO TRACKING
    # --------------------------------------------------------

    results = model.track(
        frame,
        persist=True,
        conf=CONFIDENCE,
        verbose=False
    )


    if len(results) == 0:
        continue


    result = results[0]


    if result.boxes.id is None:
        continue


    boxes = (
        result
        .boxes
        .xyxy
        .cpu()
        .numpy()
    )


    track_ids = (
        result
        .boxes
        .id
        .int()
        .cpu()
        .tolist()
    )


    classes = (
        result
        .boxes
        .cls
        .int()
        .cpu()
        .tolist()
    )


    # ========================================================
    # PROCESS EACH DETECTED OBJECT
    # ========================================================

    for box, player_id, class_id in zip(
        boxes,
        track_ids,
        classes
    ):

        # COCO class 0 = person
        if class_id != 0:
            continue


        x1, y1, x2, y2 = box


        # ----------------------------------------------------
        # PLAYER CENTER
        # ----------------------------------------------------

        center_x = (
            x1 + x2
        ) / 2.0

        center_y = (
            y1 + y2
        ) / 2.0


        current_position = (
            center_x,
            center_y
        )


        player_detection_count[
            player_id
        ] += 1


        # ----------------------------------------------------
        # FIRST DETECTION
        # ----------------------------------------------------

        if player_id not in previous_positions:

            previous_positions[
                player_id
            ] = current_position

            continue


        previous_x, previous_y = (
            previous_positions[
                player_id
            ]
        )


        # ----------------------------------------------------
        # DISTANCE BETWEEN FRAMES
        # ----------------------------------------------------

        dx = (
            center_x
            - previous_x
        )

        dy = (
            center_y
            - previous_y
        )


        distance_pixels = float(
            np.sqrt(
                dx * dx
                + dy * dy
            )
        )


        # ----------------------------------------------------
        # UPDATE POSITION
        # ----------------------------------------------------

        previous_positions[
            player_id
        ] = current_position


        # ----------------------------------------------------
        # IGNORE TINY MOVEMENT
        # ----------------------------------------------------

        if distance_pixels < MIN_PIXEL_DISTANCE:

            continue


        # ----------------------------------------------------
        # CALCULATE PIXEL SPEED
        # ----------------------------------------------------

        speed_pixels_per_second = (
            distance_pixels
            * fps
        )


        # ----------------------------------------------------
        # OUTLIER FILTER
        # ----------------------------------------------------

        if (
            speed_pixels_per_second
            > MAX_PIXEL_SPEED
        ):

            rejected_speeds += 1

            continue


        # ----------------------------------------------------
        # SPEED SMOOTHING
        # ----------------------------------------------------

        speed_history[
            player_id
        ].append(
            speed_pixels_per_second
        )


        smoothed_speed = float(
            np.mean(
                speed_history[
                    player_id
                ]
            )
        )


        player_speeds[
            player_id
        ].append(
            smoothed_speed
        )


        accepted_speeds += 1


    # ========================================================
    # PROGRESS
    # ========================================================

    if frame_count % 100 == 0:

        progress = (
            frame_count
            / total_frames
            * 100
        )

        print(
            f"Processing: {progress:.1f}%"
        )


# ============================================================
# RELEASE VIDEO
# ============================================================

cap.release()


print("\nVideo processing completed.")


# ============================================================
# CREATE FINAL RESULTS
# ============================================================

speed_results = {}


for player_id, speeds in player_speeds.items():

    if len(speeds) < 5:

        continue


    speeds_array = np.array(
        speeds,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # REMOVE EXTREME VALUES USING 95TH PERCENTILE
    # --------------------------------------------------------

    if len(speeds_array) >= 10:

        lower = np.percentile(
            speeds_array,
            5
        )

        upper = np.percentile(
            speeds_array,
            95
        )

        filtered = speeds_array[
            (speeds_array >= lower)
            &
            (speeds_array <= upper)
        ]

        if len(filtered) > 0:

            speeds_array = filtered


    # --------------------------------------------------------
    # FINAL VALUES
    # --------------------------------------------------------

    average_speed = float(
        np.mean(
            speeds_array
        )
    )


    maximum_speed = float(
        np.max(
            speeds_array
        )
    )


    # --------------------------------------------------------
    # SAVE PLAYER
    # --------------------------------------------------------

    speed_results[
        str(player_id)
    ] = {

        "average_speed":
            round(
                average_speed,
                2
            ),

        "maximum_speed":
            round(
                maximum_speed,
                2
            ),

        "unit":
            "pixels/sec",

        "speed_samples":
            len(speeds),

        "detections":
            player_detection_count[
                player_id
            ]

    }


# ============================================================
# SAVE JSON
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        speed_results,
        file,
        indent=4
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("          FINAL SPEED RESULTS")
print("=" * 60)


if len(speed_results) == 0:

    print(
        "\nERROR: No player speed data was generated."
    )

    print(
        "Check YOLO tracking and video."
    )

else:

    for player_id, data in speed_results.items():

        print(
            f"\nPlayer {player_id}"
        )

        print(
            f"Average Speed : "
            f"{data['average_speed']:.2f} pixels/sec"
        )

        print(
            f"Maximum Speed : "
            f"{data['maximum_speed']:.2f} pixels/sec"
        )

        print(
            f"Speed Samples : "
            f"{data['speed_samples']}"
        )


print("\n")
print("=" * 60)

print(
    f"Players analyzed: "
    f"{len(speed_results)}"
)

print(
    f"Accepted speed samples: "
    f"{accepted_speeds}"
)

print(
    f"Rejected tracking outliers: "
    f"{rejected_speeds}"
)

print(
    "\nResults saved to:"
)

print(
    OUTPUT_FILE
)

print("=" * 60)

print(
    "\nSPORTFLASH SPEED ANALYSIS COMPLETED"
)