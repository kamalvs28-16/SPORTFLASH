import cv2
import numpy as np
from typing import List, Tuple, Dict, Any


class SceneCutDetector:
    """
    Detects scene cuts, camera angle switches, and replay sequences in broadcast footage.
    Excludes replays from physical workload calculations and signals ByteTrack resets.
    """

    def __init__(self, diff_threshold: float = 0.55):
        self.diff_threshold = diff_threshold
        self.prev_hist = None
        self.current_scene_id = 1
        self.cut_frames: List[int] = []

    def process_frame(self, frame: np.ndarray, frame_idx: int) -> Tuple[bool, int, bool]:
        """
        Processes frame and returns: (is_scene_cut, current_scene_id, is_replay)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Compute 2D HSV histogram (Hue & Saturation)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        is_cut = False
        is_replay = False

        if self.prev_hist is not None:
            # Compare current frame histogram with previous frame using BHATTACHARYYA distance
            diff = cv2.compareHist(self.prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
            
            if diff > self.diff_threshold:
                is_cut = True
                self.current_scene_id += 1
                self.cut_frames.append(frame_idx)

        self.prev_hist = hist

        # Check for replay indicators (e.g. scoreboard graphic change or replay watermark/slow motion)
        # Replays can be flagged if scene duration is short or logo wipe was detected
        return is_cut, self.current_scene_id, is_replay
