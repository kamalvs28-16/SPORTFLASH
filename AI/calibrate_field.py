import cv2
import numpy as np

VIDEO = "E:\\SPORTFLASH\\videos\\football.mp4"

cap = cv2.VideoCapture(VIDEO)

# Select a frame from the video
frame_number = 100

cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

success, frame = cap.read()

if not success:
    print("Could not read video frame.")
    cap.release()
    exit()

points = []

print("Click 4 points on the football field.")
print("Choose four points that form a known rectangular area.")
print("Press ESC to cancel.")

def mouse_callback(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:

        if len(points) < 4:

            points.append((x, y))

            print(
                f"Point {len(points)}: ({x}, {y})"
            )

            cv2.circle(
                frame,
                (x, y),
                6,
                (255, 0, 0),
                -1
            )

            cv2.imshow("Calibration", frame)


cv2.namedWindow("Calibration")

cv2.setMouseCallback(
    "Calibration",
    mouse_callback
)

while True:

    cv2.imshow("Calibration", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

    if len(points) == 4:
        break

cv2.destroyAllWindows()
cap.release()

if len(points) != 4:

    print("You must select exactly 4 points.")
    exit()

print("\nSelected image points:")

for i, point in enumerate(points):
    print(f"Point {i + 1}: {point}")


# ------------------------------------------------
# REAL-WORLD FIELD COORDINATES
# ------------------------------------------------

# Example rectangular calibration area.
# Replace these dimensions with the actual
# dimensions of the area you selected.

REAL_WIDTH = 20.0
REAL_HEIGHT = 10.0

real_points = np.float32([
    [0, 0],
    [REAL_WIDTH, 0],
    [REAL_WIDTH, REAL_HEIGHT],
    [0, REAL_HEIGHT]
])

image_points = np.float32(points)

# Calculate perspective transformation
matrix = cv2.getPerspectiveTransform(
    image_points,
    real_points
)

print("\nPerspective transformation matrix:")
print(matrix)

# Save calibration matrix
np.save("field_calibration.npy", matrix)

print("\nCalibration completed!")
print("Saved: field_calibration.npy")