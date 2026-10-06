from ultralytics import YOLO

print("SPORTFLASH STARTED")
print("Loading YOLO model...")

# Load pre-trained YOLO model
model = YOLO("yolo11n.pt")

print("YOLO MODEL LOADED!")
print("Starting football video analysis...")

# Analyze football video
results = model.predict(
    source="E:\\SPORTFLASH\\videos\\football.mp4",
    save=True,
    conf=0.5
)

print("Football video analysis completed!")