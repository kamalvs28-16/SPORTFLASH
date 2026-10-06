import cv2
import json
import os
import numpy as np


# ============================================================
# SPORTFLASH - HOMOGRAPHY / PITCH CALIBRATION
# ============================================================

print("=" * 55)
print("SPORTFLASH HOMOGRAPHY / PITCH CALIBRATION")
print("=" * 55)


# ============================================================
# FILE PATHS
# ============================================================

VIDEO_FILE = "videos/football.mp4"

TRACKING_FILE = "results/tracking_results.json"

OUTPUT_JSON = "results/homography_positions.json"

CALIBRATION_FILE = "results/pitch_calibration.json"

CALIBRATION_IMAGE = "results/calibration_frame.jpg"


# ============================================================
# FOOTBALL PITCH DIMENSIONS
# ============================================================

# Standard pitch dimensions used by this project.
# These values define the coordinate system.
PITCH_LENGTH = 105.0
PITCH_WIDTH = 68.0


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(VIDEO_FILE):

    print()
    print("ERROR: Video file not found:")
    print(VIDEO_FILE)
    exit()


if not os.path.exists(TRACKING_FILE):

    print()
    print("ERROR: Tracking file not found:")
    print(TRACKING_FILE)
    exit()


# ============================================================
# LOAD TRACKING DATA
# ============================================================

print()
print("Loading tracking data...")

with open(TRACKING_FILE, "r") as f:
    tracking_data = json.load(f)

print("Tracking data loaded.")


frames = tracking_data.get("frames", [])

if not frames:

    print()
    print("ERROR: No tracking frames found.")
    exit()


print(f"Tracking frames available: {len(frames)}")


# ============================================================
# OPEN VIDEO
# ============================================================

print()
print("Opening football video...")

cap = cv2.VideoCapture(VIDEO_FILE)

if not cap.isOpened():

    print("ERROR: Could not open video.")
    exit()


video_width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

video_height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

fps = cap.get(cv2.CAP_PROP_FPS)

total_frames = int(
    cap.get(cv2.CAP_PROP_FRAME_COUNT)
)


print()
print("Video information")
print("-" * 30)
print(f"Width       : {video_width}")
print(f"Height      : {video_height}")
print(f"FPS         : {fps:.2f}")
print(f"Total frames: {total_frames}")


# ============================================================
# GET A FRAME FOR CALIBRATION
# ============================================================

# We use the middle frame because it often provides
# a useful view of the playing field.

calibration_frame_number = total_frames // 2

cap.set(
    cv2.CAP_PROP_POS_FRAMES,
    calibration_frame_number
)

success, frame = cap.read()

cap.release()


if not success:

    print()
    print("ERROR: Could not read calibration frame.")
    exit()


# ============================================================
# SAVE CALIBRATION FRAME
# ============================================================

os.makedirs("results", exist_ok=True)

cv2.imwrite(
    CALIBRATION_IMAGE,
    frame
)

print()
print("Calibration frame saved:")
print(CALIBRATION_IMAGE)


# ============================================================
# MANUAL POINT SELECTION
# ============================================================

selected_points = []


def mouse_callback(event, x, y, flags, param):

    global selected_points

    if event == cv2.EVENT_LBUTTONDOWN:

        if len(selected_points) < 4:

            selected_points.append((x, y))

            print(
                f"Point {len(selected_points)} selected: "
                f"({x}, {y})"
            )


# ============================================================
# DISPLAY CALIBRATION FRAME
# ============================================================

display_frame = frame.copy()


cv2.namedWindow(
    "SPORTFLASH - Select Pitch Points",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "SPORTFLASH - Select Pitch Points",
    1280,
    720
)

cv2.setMouseCallback(
    "SPORTFLASH - Select Pitch Points",
    mouse_callback
)


print()
print("=" * 55)
print("MANUAL PITCH CALIBRATION")
print("=" * 55)

print()
print("Select FOUR points on the football pitch.")

print()
print("Recommended order:")

print("1. Top-left pitch corner/line point")
print("2. Top-right pitch corner/line point")
print("3. Bottom-right pitch corner/line point")
print("4. Bottom-left pitch corner/line point")

print()
print("Important:")
print("- Select points that belong to the actual pitch.")
print("- Use visible field lines/corners.")
print("- Do NOT select players.")
print("- Do NOT select the image corners unless")
print("  they actually correspond to pitch corners.")

print()
print("Click the four points with the mouse.")
print("Press R to reset points.")
print("Press ENTER after selecting 4 points.")
print("Press ESC to cancel.")


# ============================================================
# INTERACTIVE SELECTION
# ============================================================

while True:

    display_frame = frame.copy()

    # Draw selected points
    for i, point in enumerate(selected_points):

        cv2.circle(
            display_frame,
            point,
            8,
            (0, 255, 0),
            -1
        )

        cv2.putText(
            display_frame,
            str(i + 1),
            (point[0] + 10, point[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


    # Show instruction
    cv2.putText(
        display_frame,
        f"Points selected: {len(selected_points)}/4",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2
    )


    cv2.imshow(
        "SPORTFLASH - Select Pitch Points",
        display_frame
    )


    key = cv2.waitKey(20) & 0xFF


    # ESC
    if key == 27:

        cv2.destroyAllWindows()

        print()
        print("Calibration cancelled.")

        exit()


    # R = reset
    if key == ord("r"):

        selected_points = []

        print()
        print("Points reset. Select four points again.")


    # ENTER
    if key == 13:

        if len(selected_points) == 4:

            break

        else:

            print()
            print(
                f"Please select exactly 4 points. "
                f"Currently selected: {len(selected_points)}"
            )


cv2.destroyAllWindows()


# ============================================================
# DISPLAY SELECTED POINTS
# ============================================================

print()
print("=" * 55)
print("SELECTED IMAGE POINTS")
print("=" * 55)

for i, point in enumerate(selected_points):

    print(
        f"Point {i + 1}: "
        f"x={point[0]}, y={point[1]}"
    )


# ============================================================
# SOURCE POINTS
# ============================================================

source_points = np.array(
    selected_points,
    dtype=np.float32
)


# ============================================================
# DESTINATION PITCH POINTS
# ============================================================

# The selected image points correspond to these
# real-world pitch coordinates.

destination_points = np.array(
    [
        [0.0, 0.0],
        [PITCH_LENGTH, 0.0],
        [PITCH_LENGTH, PITCH_WIDTH],
        [0.0, PITCH_WIDTH]
    ],
    dtype=np.float32
)


# ============================================================
# CALCULATE HOMOGRAPHY MATRIX
# ============================================================

print()
print("Calculating homography matrix...")


H, status = cv2.findHomography(
    source_points,
    destination_points
)


if H is None:

    print()
    print("ERROR: Homography calculation failed.")
    exit()


print()
print("Homography matrix calculated successfully.")


print()
print("Homography matrix:")
print(H)


# ============================================================
# SAVE CALIBRATION INFORMATION
# ============================================================

calibration_data = {

    "video": VIDEO_FILE,

    "video_width": video_width,

    "video_height": video_height,

    "pitch_length_m": PITCH_LENGTH,

    "pitch_width_m": PITCH_WIDTH,

    "source_points": [
        list(point)
        for point in selected_points
    ],

    "destination_points": [
        list(point)
        for point in destination_points.tolist()
    ],

    "homography_matrix": H.tolist()
}


with open(
    CALIBRATION_FILE,
    "w"
) as f:

    json.dump(
        calibration_data,
        f,
        indent=4
    )


print()
print("Calibration saved:")
print(CALIBRATION_FILE)


# ============================================================
# FUNCTION: TRANSFORM IMAGE POINT
# ============================================================

def transform_point(x, y):

    point = np.array(
        [
            [
                [float(x), float(y)]
            ]
        ],
        dtype=np.float32
    )


    transformed = cv2.perspectiveTransform(
        point,
        H
    )


    real_x = float(
        transformed[0][0][0]
    )

    real_y = float(
        transformed[0][0][1]
    )


    return real_x, real_y


# ============================================================
# TRANSFORM TRACKING DATA
# ============================================================

print()
print("=" * 55)
print("TRANSFORMING PLAYER POSITIONS")
print("=" * 55)


homography_frames = []


processed_frames = 0

transformed_positions = 0


for frame_data in frames:

    frame_number = frame_data.get(
        "frame"
    )

    players = frame_data.get(
        "players",
        []
    )


    transformed_players = []


    for player in players:

        player_id = player.get(
            "player_id"
        )


        # ----------------------------------------------------
        # Use player's bottom-center position.
        # This approximates the point where the player's
        # feet contact the pitch.
        # ----------------------------------------------------

        if (
            "center_x" in player
            and "bottom_y" in player
        ):

            image_x = player["center_x"]

            image_y = player["bottom_y"]

        else:

            image_x = (
                player["x1"] +
                player["x2"]
            ) / 2.0

            image_y = player["y2"]


        # ----------------------------------------------------
        # Convert image coordinates to pitch coordinates
        # ----------------------------------------------------

        pitch_x, pitch_y = transform_point(
            image_x,
            image_y
        )


        # ----------------------------------------------------
        # Keep coordinates inside pitch boundaries
        # ----------------------------------------------------

        pitch_x = max(
            0.0,
            min(PITCH_LENGTH, pitch_x)
        )

        pitch_y = max(
            0.0,
            min(PITCH_WIDTH, pitch_y)
        )


        transformed_players.append(

            {
                "player_id": player_id,

                "image_x": round(
                    float(image_x),
                    2
                ),

                "image_y": round(
                    float(image_y),
                    2
                ),

                "pitch_x_m": round(
                    pitch_x,
                    3
                ),

                "pitch_y_m": round(
                    pitch_y,
                    3
                )
            }

        )


        transformed_positions += 1


    homography_frames.append(

        {
            "frame": frame_number,

            "players": transformed_players
        }

    )


    processed_frames += 1


    if processed_frames % 100 == 0:

        print(
            f"Processed frame "
            f"{processed_frames}/{len(frames)}"
        )


# ============================================================
# CREATE OUTPUT
# ============================================================

homography_output = {

    "video": VIDEO_FILE,

    "fps": fps,

    "total_frames": len(frames),

    "coordinate_system": {

        "pitch_length_m": PITCH_LENGTH,

        "pitch_width_m": PITCH_WIDTH,

        "origin": "top-left",

        "x_axis": "pitch length",

        "y_axis": "pitch width"

    },

    "calibration": {

        "method": "four-point planar homography",

        "calibration_file": CALIBRATION_FILE

    },

    "frames": homography_frames

}


# ============================================================
# SAVE OUTPUT
# ============================================================

with open(
    OUTPUT_JSON,
    "w"
) as f:

    json.dump(
        homography_output,
        f,
        indent=4
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 55)
print("HOMOGRAPHY COMPLETED")
print("=" * 55)

print()
print(f"Frames processed       : {processed_frames}")

print(
    f"Player positions transformed: "
    f"{transformed_positions}"
)

print()
print("Generated files:")

print(
    f"✓ {CALIBRATION_FILE}"
)

print(
    f"✓ {OUTPUT_JSON}"
)

print()
print("Coordinate conversion:")
print("IMAGE PIXELS")
print("     ↓")
print("HOMOGRAPHY")
print("     ↓")
print("REAL PITCH METRES")

print()
print(
    f"Pitch coordinate system: "
    f"{PITCH_LENGTH} m × {PITCH_WIDTH} m"
)

print()
print("Next module:")
print("distance_analysis.py")