import cv2
import numpy as np
import torch
from typing import List, Dict, Any, Tuple, Optional
from ultralytics import YOLO

from pipeline.config import (
    YOLO_MODEL_NAME, DETECTION_IMGSZ, PLAYER_CONF_THRESH, BALL_CONF_THRESH,
    PITCH_MASK_ENABLED, GREEN_HSV_LOWER, GREEN_HSV_UPPER
)


class PitchMasker:
    """
    Computes dynamic pitch boundary mask based on field color thresholding.
    Safely falls back to full-frame if lighting/turf color is non-standard.
    """

    def __init__(self, hsv_lower=GREEN_HSV_LOWER, hsv_upper=GREEN_HSV_UPPER):
        self.hsv_lower = np.array(hsv_lower, dtype=np.uint8)
        self.hsv_upper = np.array(hsv_upper, dtype=np.uint8)

    def get_mask(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        total_area = w * h
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
        
        # Morphological operations to fill holes and smooth pitch mask
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find largest contour corresponding to playing field
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pitch_mask = np.zeros_like(mask)

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            # If field contour is sufficiently large (>= 5% of frame)
            if area >= total_area * 0.05:
                hull = cv2.convexHull(c)
                cv2.drawContours(pitch_mask, [hull], -1, 255, -1)
                
                # Dilate mask to keep line-touching players
                dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
                pitch_mask = cv2.dilate(pitch_mask, dilate_kernel)
                return pitch_mask

        # Fallback: full frame mask
        return np.ones((h, w), dtype=np.uint8) * 255

    def is_inside_pitch(self, mask: np.ndarray, point_xy: Tuple[float, float]) -> bool:
        x, y = int(point_xy[0]), int(point_xy[1])
        h, w = mask.shape
        if 0 <= x < w and 0 <= y < h:
            return bool(mask[y, x] > 0)
        return True


class FootballDetector:
    """
    YOLO11-based high resolution object detector with pitch mask filtering.
    Detects players, referees, goalkeepers, and footballs.
    """

    def __init__(self, model_name: str = YOLO_MODEL_NAME, imgsz: int = DETECTION_IMGSZ):
        self.imgsz = imgsz
        print(f"[INFO] Initializing FootballDetector with model: {model_name} @ {imgsz}px...")
        self.model = YOLO(model_name)
        self.pitch_masker = PitchMasker()

    def detect(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]], np.ndarray]:
        pitch_mask = self.pitch_masker.get_mask(frame) if PITCH_MASK_ENABLED else np.ones(frame.shape[:2], dtype=np.uint8) * 255

        # Run YOLO inference
        results = self.model(frame, imgsz=self.imgsz, verbose=False)[0]

        player_dets = []
        ball_det = None

        if results.boxes is not None and len(results.boxes):
            boxes = results.boxes.xyxy.cpu().numpy()
            confs = results.boxes.conf.cpu().numpy()
            classes = results.boxes.cls.cpu().numpy().astype(int)

            for i, cls_id in enumerate(classes):
                bx1, by1, bx2, by2 = boxes[i]
                conf = float(confs[i])
                w, h = bx2 - bx1, by2 - by1
                cx = float((bx1 + bx2) / 2.0)
                by = float(by2)  # Bottom of bounding box = player feet position

                # COCO Class 0 = person
                if cls_id == 0 and conf >= PLAYER_CONF_THRESH:
                    if w < 6 or h < 12:
                        continue

                    # Pitch mask verification: player foot point must be inside field mask
                    if PITCH_MASK_ENABLED and not self.pitch_masker.is_inside_pitch(pitch_mask, (cx, by)):
                        continue

                    player_dets.append({
                        "bbox": [float(bx1), float(by1), float(bx2), float(by2)],
                        "pixel_xy": [cx, by],
                        "confidence": round(conf, 3),
                        "role": "player",
                        "width": float(w),
                        "height": float(h)
                    })

                # COCO Class 32 = sports ball
                elif cls_id == 32 and conf >= BALL_CONF_THRESH:
                    ball_cx = float((bx1 + bx2) / 2.0)
                    ball_cy = float((by1 + by2) / 2.0)

                    if ball_det is None or conf > ball_det["confidence"]:
                        ball_det = {
                            "bbox": [float(bx1), float(by1), float(bx2), float(by2)],
                            "pixel_xy": [ball_cx, ball_cy],
                            "confidence": round(conf, 3),
                            "role": "ball"
                        }

        return player_dets, ball_det, pitch_mask
