import cv2
import json
import os
import numpy as np


# ============================================================
# SPORTFLASH - CAMERA MOTION ANALYSIS
# ============================================================

print("=" * 60)
print("SPORTFLASH CAMERA MOTION ANALYSIS")
print("=" * 60)


# ============================================================
# FILE PATHS
# ============================================================

VIDEO_FILE = "videos/football.mp4"

OUTPUT_FILE = "results/camera_motion.json"


# ============================================================
# SETTINGS
# ============================================================

# Process every Nth frame.
# This reduces processing time while still detecting
# camera movement.

FRAME_STEP = 5

# Maximum number of feature points used by optical flow.

MAX_CORNERS = 500


# ============================================================
# CHECK VIDEO
# ============================================================

if not os.path.exists(VIDEO_FILE):

    print()
    print("ERROR: Video file not found:")
    print(VIDEO_FILE)

    exit()


# ============================================================
# OPEN VIDEO
# ============================================================

print()
print("Opening football video...")

cap = cv2.VideoCapture(VIDEO_FILE)


if not cap.isOpened():

    print()
    print("ERROR: Could not open video.")

    exit()


fps = cap.get(
    cv2.CAP_PROP_FPS
)

total_frames = int(
    cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)

width = int(
    cap.get(
        cv2.CAP_PROP_FRAME_WIDTH
    )
)

height = int(
    cap.get(
        cv2.CAP_PROP_FRAME_HEIGHT
    )
)


print()
print("Video information")
print("-" * 35)

print(f"Width       : {width}")
print(f"Height      : {height}")
print(f"FPS         : {fps:.2f}")
print(f"Total frames: {total_frames}")

print()
print(
    f"Processing every {FRAME_STEP} frames."
)


# ============================================================
# READ FIRST FRAME
# ============================================================

success, first_frame = cap.read()


if not success:

    print()
    print("ERROR: Could not read first frame.")

    cap.release()

    exit()


previous_gray = cv2.cvtColor(
    first_frame,
    cv2.COLOR_BGR2GRAY
)


# ============================================================
# CAMERA MOTION STORAGE
# ============================================================

motion_data = []

frame_number = 0

processed_frames = 0


# ============================================================
# CAMERA MOTION CLASSIFICATION
# ============================================================

def classify_motion(
    movement_x,
    movement_y,
    rotation,
    scale_change
):

    translation = np.sqrt(
        movement_x ** 2 +
        movement_y ** 2
    )


    # Small camera movement
    if (
        translation < 1.5
        and abs(rotation) < 0.5
    ):

        return "stable"


    # Camera moving horizontally
    if (
        abs(movement_x) >
        abs(movement_y) * 1.5
        and abs(movement_x) >= 1.5
    ):

        if movement_x > 0:
            return "pan_right"

        return "pan_left"


    # Camera moving vertically
    if (
        abs(movement_y) >
        abs(movement_x) * 1.5
        and abs(movement_y) >= 1.5
    ):

        if movement_y > 0:
            return "tilt_down"

        return "tilt_up"


    # Rotation
    if abs(rotation) >= 0.5:

        if rotation > 0:
            return "rotate_clockwise"

        return "rotate_counterclockwise"


    # Zoom
    if abs(scale_change) >= 0.01:

        if scale_change > 0:
            return "zoom_in"

        return "zoom_out"


    return "moving"


# ============================================================
# MAIN PROCESSING LOOP
# ============================================================

while True:

    success, frame = cap.read()


    if not success:

        break


    frame_number += 1


    # --------------------------------------------------------
    # Skip frames
    # --------------------------------------------------------

    if frame_number % FRAME_STEP != 0:

        continue


    current_gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # --------------------------------------------------------
    # Detect feature points in previous frame
    # --------------------------------------------------------

    previous_points = cv2.goodFeaturesToTrack(

        previous_gray,

        maxCorners=MAX_CORNERS,

        qualityLevel=0.01,

        minDistance=10,

        blockSize=7

    )


    if previous_points is None:

        previous_gray = current_gray

        continue


    # --------------------------------------------------------
    # Track feature points
    # --------------------------------------------------------

    current_points, status, errors = cv2.calcOpticalFlowPyrLK(

        previous_gray,

        current_gray,

        previous_points,

        None

    )


    if current_points is None:

        previous_gray = current_gray

        continue


    # --------------------------------------------------------
    # Keep valid points
    # --------------------------------------------------------

    valid_previous = previous_points[
        status == 1
    ]

    valid_current = current_points[
        status == 1
    ]


    if len(valid_previous) < 10:

        previous_gray = current_gray

        continue


    # --------------------------------------------------------
    # Estimate affine camera motion
    # --------------------------------------------------------

    matrix, inliers = cv2.estimateAffinePartial2D(

        valid_previous,

        valid_current,

        method=cv2.RANSAC,

        ransacReprojThreshold=3.0

    )


    if matrix is None:

        previous_gray = current_gray

        continue


    # --------------------------------------------------------
    # Extract transformation
    # --------------------------------------------------------

    a = matrix[0, 0]

    b = matrix[0, 1]

    tx = matrix[0, 2]

    ty = matrix[1, 2]


    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    movement_x = float(tx)

    movement_y = float(ty)


    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

    rotation = np.degrees(
        np.arctan2(
            b,
            a
        )
    )


    # --------------------------------------------------------
    # Scale
    # --------------------------------------------------------

    scale = np.sqrt(
        a * a +
        b * b
    )


    scale_change = (
        scale - 1.0
    )


    # --------------------------------------------------------
    # Number of tracked features
    # --------------------------------------------------------

    feature_count = int(
        len(valid_previous)
    )


    if inliers is not None:

        inlier_count = int(
            np.sum(inliers)
        )

    else:

        inlier_count = 0


    # --------------------------------------------------------
    # Camera motion magnitude
    # --------------------------------------------------------

    translation_magnitude = float(
        np.sqrt(
            movement_x ** 2 +
            movement_y ** 2
        )
    )


    # --------------------------------------------------------
    # Classify
    # --------------------------------------------------------

    motion_type = classify_motion(

        movement_x,

        movement_y,

        rotation,

        scale_change

    )


    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    motion_data.append(

        {

            "frame":
                frame_number,

            "movement_x_pixels":
                round(
                    movement_x,
                    3
                ),

            "movement_y_pixels":
                round(
                    movement_y,
                    3
                ),

            "translation_magnitude_pixels":
                round(
                    translation_magnitude,
                    3
                ),

            "rotation_degrees":
                round(
                    float(rotation),
                    4
                ),

            "scale_change":
                round(
                    float(scale_change),
                    6
                ),

            "feature_points":
                feature_count,

            "inlier_points":
                inlier_count,

            "motion_type":
                motion_type

        }

    )


    processed_frames += 1


    if processed_frames % 25 == 0:

        print(
            f"Processed frame "
            f"{frame_number}/{total_frames}"
        )


    previous_gray = current_gray


# ============================================================
# RELEASE VIDEO
# ============================================================

cap.release()


# ============================================================
# SUMMARY STATISTICS
# ============================================================

print()
print("=" * 60)
print("CAMERA MOTION SUMMARY")
print("=" * 60)


if len(motion_data) == 0:

    print()
    print("ERROR: No camera motion data was generated.")

    exit()


translation_values = [

    item[
        "translation_magnitude_pixels"
    ]

    for item in motion_data

]


rotation_values = [

    abs(
        item[
            "rotation_degrees"
        ]
    )

    for item in motion_data

]


stable_frames = sum(

    1

    for item in motion_data

    if item[
        "motion_type"
    ] == "stable"

)


moving_frames = len(
    motion_data
) - stable_frames


average_translation = (
    sum(translation_values)
    /
    len(translation_values)
)


maximum_translation = max(
    translation_values
)


average_rotation = (
    sum(rotation_values)
    /
    len(rotation_values)
)


maximum_rotation = max(
    rotation_values
)


# ============================================================
# MOTION TYPE COUNTS
# ============================================================

motion_counts = {}


for item in motion_data:

    motion_type = item[
        "motion_type"
    ]


    if motion_type not in motion_counts:

        motion_counts[motion_type] = 0


    motion_counts[motion_type] += 1


# ============================================================
# FINAL OUTPUT
# ============================================================

output = {

    "video":
        VIDEO_FILE,

    "video_information":
        {

            "width":
                width,

            "height":
                height,

            "fps":
                fps,

            "total_frames":
                total_frames

        },

    "analysis":
        {

            "frame_step":
                FRAME_STEP,

            "processed_frames":
                processed_frames,

            "method":
                "Lucas-Kanade optical flow + RANSAC affine estimation"

        },

    "summary":
        {

            "average_translation_pixels":
                round(
                    average_translation,
                    3
                ),

            "maximum_translation_pixels":
                round(
                    maximum_translation,
                    3
                ),

            "average_rotation_degrees":
                round(
                    average_rotation,
                    4
                ),

            "maximum_rotation_degrees":
                round(
                    maximum_rotation,
                    4
                ),

            "stable_frames":
                stable_frames,

            "moving_frames":
                moving_frames,

            "motion_counts":
                motion_counts

        },

    "frames":
        motion_data

}


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "results",
    exist_ok=True
)


with open(
    OUTPUT_FILE,
    "w"
) as f:

    json.dump(
        output,
        f,
        indent=4
    )


# ============================================================
# DISPLAY
# ============================================================

print()

print(
    f"Processed frames: "
    f"{processed_frames}"
)

print()

print(
    f"Average camera movement: "
    f"{average_translation:.2f} pixels"
)

print(
    f"Maximum camera movement: "
    f"{maximum_translation:.2f} pixels"
)

print()

print(
    f"Average rotation: "
    f"{average_rotation:.4f} degrees"
)

print(
    f"Maximum rotation: "
    f"{maximum_rotation:.4f} degrees"
)

print()

print("Motion types:")

for motion_type, count in motion_counts.items():

    print(
        f"  {motion_type}: {count}"
    )


print()
print("=" * 60)
print("CAMERA MOTION ANALYSIS COMPLETED")
print("=" * 60)

print()
print(
    f"Output file: "
    f"✓ {OUTPUT_FILE}"
)

print()
print("Next module:")
print("dynamic_calibration.py")