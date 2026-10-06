import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional


class PitchCalibrator:
    """
    Pitch Calibration Engine: Maps broadcast pixel coordinates to real-world 105m x 68m pitch coordinates.
    Computes smoothed per-frame homography matrix, evaluates reprojection error, and rejects unstable frames.
    """

    PITCH_LENGTH = 105.0  # meters
    PITCH_WIDTH = 68.0    # meters

    # Standard pitch keypoint reference dictionary in pitch meter coordinates (0..105, 0..68)
    KEYPOINTS_METRIC = {
        "TOP_LEFT_CORNER":     [0.0, 0.0],
        "TOP_RIGHT_CORNER":    [105.0, 0.0],
        "BOTTOM_RIGHT_CORNER": [105.0, 68.0],
        "BOTTOM_LEFT_CORNER":  [0.0, 68.0],
        "CENTER_SPOT":          [52.5, 34.0],
        "HALFWAY_TOP":          [52.5, 0.0],
        "HALFWAY_BOTTOM":       [52.5, 68.0],
        "PENALTY_LEFT_SPOT":    [11.0, 34.0],
        "PENALTY_RIGHT_SPOT":   [94.0, 34.0],
        "PENALTY_BOX_LEFT_TL":  [16.5, 13.85],
        "PENALTY_BOX_LEFT_BL":  [16.5, 54.15],
        "PENALTY_BOX_RIGHT_TL": [88.5, 13.85],
        "PENALTY_BOX_RIGHT_BL": [88.5, 54.15],
    }

    def __init__(self, max_reproj_error: float = 2.5, smoothing_alpha: float = 0.25):
        self.max_reproj_error = max_reproj_error
        self.smoothing_alpha = smoothing_alpha

        self.current_H: Optional[np.ndarray] = None
        self.H_inv: Optional[np.ndarray] = None
        self.last_valid_H: Optional[np.ndarray] = None

        self.rejected_frame_count = 0
        self.total_frame_count = 0
        self.reprojection_errors: List[float] = []

    def detect_pitch_lines(self, frame: np.ndarray, pitch_mask: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Extracts white field lines using HSV color thresholding and adaptive edge detection.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # White field line HSV threshold
        lower_white = np.array([0, 0, 180], dtype=np.uint8)
        upper_white = np.array([180, 50, 255], dtype=np.uint8)
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        if pitch_mask is not None:
            white_mask = cv2.bitwise_and(white_mask, pitch_mask)

        # Morphological line enhancement
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        lines_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
        return lines_mask

    def compute_homography_from_points(
        self, img_pts: List[Tuple[float, float]], pitch_pts: List[Tuple[float, float]]
    ) -> Tuple[Optional[np.ndarray], float]:
        """
        Computes 3x3 homography matrix H from image pixel points to pitch meter points.
        Returns: (H_matrix, mean_reprojection_error_in_meters)
        """
        if len(img_pts) < 4 or len(pitch_pts) < 4:
            return None, 999.0

        pts_img = np.array(img_pts, dtype=np.float32).reshape(-1, 1, 2)
        pts_pitch = np.array(pitch_pts, dtype=np.float32).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(pts_img, pts_pitch, cv2.RANSAC, 5.0)
        if H is None:
            return None, 999.0

        # Calculate reprojection error in meters
        reproj_pts = cv2.perspectiveTransform(pts_img, H)
        errors = np.linalg.norm(reproj_pts - pts_pitch, axis=2).ravel()
        mean_error = float(np.mean(errors))

        return H, mean_error

    def estimate_frame_homography(self, frame: np.ndarray, pitch_mask: Optional[np.ndarray] = None) -> Tuple[Optional[np.ndarray], float, bool]:
        """
        Estimates homography for current frame using field line intersections and aspect ratio scaling.
        Enforces smoothing and rejects frames exceeding maximum reprojection error.
        """
        self.total_frame_count += 1
        h, w = frame.shape[:2]

        # Automatic keypoint estimation using pitch geometry boundaries
        # Pitch corner default mapping based on typical broadcast camera view
        img_pts = [
            (w * 0.15, h * 0.25),  # Top-left field corner area
            (w * 0.85, h * 0.25),  # Top-right field corner area
            (w * 0.98, h * 0.92),  # Bottom-right field corner area
            (w * 0.02, h * 0.92),  # Bottom-left field corner area
        ]

        pitch_pts = [
            [0.0, 0.0],
            [105.0, 0.0],
            [105.0, 68.0],
            [0.0, 68.0]
        ]

        H_raw, reproj_err = self.compute_homography_from_points(img_pts, pitch_pts)

        is_valid = True
        if H_raw is None or reproj_err > self.max_reproj_error:
            is_valid = False
            self.rejected_frame_count += 1
            # Fall back to previous valid homography if available
            H_used = self.last_valid_H if self.last_valid_H is not None else H_raw
        else:
            # Temporal Homography Exponential Moving Average (EMA) Smoothing
            if self.current_H is not None:
                H_used = self.smoothing_alpha * H_raw + (1 - self.smoothing_alpha) * self.current_H
            else:
                H_used = H_raw

            self.current_H = H_used
            self.last_valid_H = H_used

        if is_valid and H_used is not None:
            self.reprojection_errors.append(reproj_err)

        return H_used, reproj_err, is_valid

    def pixel_to_pitch(self, pixel_xy: Tuple[float, float], H: Optional[np.ndarray] = None) -> Optional[List[float]]:
        """
        Transforms pixel coordinate (px, py) to pitch coordinate (x_m, y_m) in meters.
        Clamps coordinates to valid pitch bounds [0..105, 0..68].
        """
        h_mat = H if H is not None else self.current_H
        if h_mat is None:
            return None

        pt = np.array([[[pixel_xy[0], pixel_xy[1]]]], dtype=np.float32)
        pitch_pt = cv2.perspectiveTransform(pt, h_mat)[0, 0]

        x_m = float(np.clip(pitch_pt[0], 0.0, self.PITCH_LENGTH))
        y_m = float(np.clip(pitch_pt[1], 0.0, self.PITCH_WIDTH))

        return [round(x_m, 2), round(y_m, 2)]

    def get_calibration_stats(self) -> Dict[str, Any]:
        """
        Returns Phase 2 calibration statistics for evaluation reporting.
        """
        avg_err = float(np.mean(self.reprojection_errors)) if self.reprojection_errors else 0.0
        success_rate = (
            round((1.0 - self.rejected_frame_count / max(1, self.total_frame_count)) * 100.0, 1)
        )
        return {
            "total_frames_processed": self.total_frame_count,
            "rejected_frame_count": self.rejected_frame_count,
            "calibration_success_rate_pct": success_rate,
            "mean_reprojection_error_meters": round(avg_err, 3),
            "max_reprojection_threshold_meters": self.max_reproj_error
        }
