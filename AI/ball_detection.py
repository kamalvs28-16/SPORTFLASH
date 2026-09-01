from ultralytics import YOLO
import cv2

print("================================")
print(" SPORTFLASH BALL DETECTION")
print("================================")

model = YOLO("yolo11n.pt")

video_path = "E:\\SPORTFLASH\\videos\\football.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Video FPS: {fps}")

frame_count = 0
ball_count = 0

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_count += 1

    results = model.track(
        frame,
        persist=True,
        conf=0.25,
        verbose=False
    )

    for result in results:

        if result.boxes is None:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        for box, class_id in zip(boxes, classes):

            class_name = model.names[int(class_id)]

            # YOLO COCO class for sports ball
            if class_name == "sports ball":

                ball_count += 1

                x1, y1, x2, y2 = box

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                print(
                    f"Frame {frame_count}: "
                    f"Ball detected at "
                    f"({center_x}, {center_y})"
                )

                cv2.rectangle(
                    frame,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5,
                    (0, 0, 255),
                    -1
                )

    # Display every frame
    cv2.imshow("SPORTFLASH - Ball Detection", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()

cv2.destroyAllWindows()

print("\n================================")
print("BALL DETECTION COMPLETED")
print("================================")

print(f"Frames processed: {frame_count}")
print(f"Ball detections: {ball_count}")