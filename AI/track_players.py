from ultralytics import YOLO

print("SPORTFLASH PLAYER TRACKING")
print("Loading YOLO model...")

# Load YOLO model
model = YOLO("yolo11n.pt")

print("YOLO MODEL LOADED!")
print("Starting player tracking...")

# Track players in the football video
results = model.track(
    source="E:\\SPORTFLASH\\videos\\football.mp4",
    save=True,
    conf=0.5,
    persist=True
)

print("Player tracking completed!")