import os

# Project root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# Phase 1-4: Pipeline Configuration Parameters
# --------------------------------------------------------------------------
YOLO_MODEL_NAME = "yolo11m.pt"         # Fine tuned / medium model for accuracy
DETECTION_IMGSZ = 1280                 # 1280px resolution to catch small/distant objects
PLAYER_CONF_THRESH = 0.25              # Detection confidence threshold for person
BALL_CONF_THRESH = 0.15                # Detection confidence threshold for sports ball

# Pitch Mask (reject crowd/bench while covering both natural grass and artificial turf)
PITCH_MASK_ENABLED = True
GREEN_HSV_LOWER = (20, 20, 20)         # Broadened HSV bounds for indoor/artificial turf
GREEN_HSV_UPPER = (135, 255, 255)
PITCH_CONTOUR_MIN_AREA_PCT = 0.05     # Minimum field contour area

# ByteTrack Parameters
BYTETRACK_TRACK_THRESH = 0.30
BYTETRACK_MATCH_THRESH = 0.80
BYTETRACK_TRACK_BUFFER = 45            # 45 frames persistence (~1.5s @ 30fps)

# Scene Cut & Replay Detection
SCENE_CUT_HIST_DIFF_THRESH = 0.60      # HSV histogram chi-square difference threshold
REPLAY_TEXT_DETECT_ENABLED = True

# Ball Kalman & Interpolation
BALL_MAX_LOST_FRAMES = 12              # Maximum gap to interpolate ball trajectories
BALL_KALMAN_R_NOISE = 0.05             # Kalman measurement noise
