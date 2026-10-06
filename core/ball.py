import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

from pipeline.config import BALL_MAX_LOST_FRAMES, BALL_KALMAN_R_NOISE


class BallKalmanFilter:
    """
    2D Constant Velocity Kalman Filter for football tracking.
    State: [x, y, vx, vy]^T
    """

    def __init__(self, dt: float = 0.04):
        self.dt = dt
        # State transition matrix
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1]
        ], dtype=np.float32)

        # Measurement matrix (observing x, y)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)

        # Covariance matrices
        self.P = np.eye(4, dtype=np.float32) * 100.0
        self.Q = np.eye(4, dtype=np.float32) * 1.0  # Process noise
        self.R = np.eye(2, dtype=np.float32) * BALL_KALMAN_R_NOISE  # Measurement noise

        self.x = np.zeros((4, 1), dtype=np.float32)
        self.initialized = False

    def init(self, cx: float, cy: float):
        self.x = np.array([[cx], [cy], [0.0], [0.0]], dtype=np.float32)
        self.P = np.eye(4, dtype=np.float32) * 10.0
        self.initialized = True

    def predict(self) -> Tuple[float, float]:
        if not self.initialized:
            return 0.0, 0.0
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return float(self.x[0, 0]), float(self.x[1, 0])

    def update(self, cx: float, cy: float):
        z = np.array([[cx], [cy]], dtype=np.float32)
        y = z - self.H @ self.x  # Innovation
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
        self.x = self.x + K @ y
        self.P = (np.eye(4, dtype=np.float32) - K @ self.H) @ self.P


class BallTracker:
    """
    Dedicated ball detector, Kalman filter, short-gap interpolation, and trail buffer.
    """

    def __init__(self, max_lost_frames: int = BALL_MAX_LOST_FRAMES):
        self.max_lost_frames = max_lost_frames
        self.kalman = BallKalmanFilter()
        self.lost_counter = 0
        self.last_known_detection: Optional[Dict[str, Any]] = None
        self.trail: List[Tuple[float, float]] = []
        self.max_trail_len = 30
        self.interpolated_count = 0

    def process_frame(self, ball_det: Optional[Dict[str, Any]], frame_idx: int) -> Optional[Dict[str, Any]]:
        """
        Updates ball state with Kalman prediction/update and short-gap interpolation.
        Returns canonical ball dict or None if ball is lost.
        """
        if ball_det is not None:
            cx, cy = ball_det["pixel_xy"]
            if not self.kalman.initialized:
                self.kalman.init(cx, cy)
            else:
                self.kalman.predict()
                self.kalman.update(cx, cy)

            smooth_x, smooth_y = float(self.kalman.x[0, 0]), float(self.kalman.x[1, 0])
            self.lost_counter = 0
            
            output_ball = {
                "bbox": ball_det["bbox"],
                "pixel_xy": [round(smooth_x, 1), round(smooth_y, 1)],
                "confidence": ball_det["confidence"],
                "role": "ball",
                "is_interpolated": False
            }
            self.last_known_detection = output_ball
            self.trail.append((smooth_x, smooth_y))

        else:
            # Ball lost: predict using Kalman filter if within gap limit
            self.lost_counter += 1
            if self.kalman.initialized and self.lost_counter <= self.max_lost_frames:
                pred_x, pred_y = self.kalman.predict()
                self.interpolated_count += 1
                
                output_ball = {
                    "bbox": [pred_x - 10, pred_y - 10, pred_x + 10, pred_y + 10],
                    "pixel_xy": [round(pred_x, 1), round(pred_y, 1)],
                    "confidence": max(0.1, 0.50 - self.lost_counter * 0.04),
                    "role": "ball",
                    "is_interpolated": True
                }
                self.trail.append((pred_x, pred_y))
            else:
                output_ball = None

        if len(self.trail) > self.max_trail_len:
            self.trail.pop(0)

        return output_ball
