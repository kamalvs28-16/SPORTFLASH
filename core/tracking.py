import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

from pipeline.config import BYTETRACK_TRACK_THRESH, BYTETRACK_MATCH_THRESH, BYTETRACK_TRACK_BUFFER


class ByteTrackTracker:
    """
    ByteTrack persistent multi-object tracking wrapper for player tracking.
    Maintains track IDs across frames and handles track association.
    """

    def __init__(self, track_thresh=BYTETRACK_TRACK_THRESH, match_thresh=BYTETRACK_MATCH_THRESH, track_buffer=BYTETRACK_TRACK_BUFFER):
        self.track_thresh = track_thresh
        self.match_thresh = match_thresh
        self.track_buffer = track_buffer

        self.tracks: Dict[int, Dict[str, Any]] = {}
        self.next_id = 1
        self.lost_counts = defaultdict(int)
        self.max_lost = track_buffer

    def reset(self):
        """Resets tracking state across scene cuts."""
        self.tracks.clear()
        self.lost_counts.clear()

    def update(self, detections: List[Dict[str, Any]], frame_idx: int) -> List[Dict[str, Any]]:
        """
        Associates frame detections to active tracks using IoU & Spatial Distance matching.
        """
        updated_tracks = []
        unmatched_dets = list(range(len(detections)))
        matched_tracks = set()

        # Step 1: Distance & IoU Hungarian-style matching to active tracks
        for tid, trk in list(self.tracks.items()):
            best_dist = 100.0  # Max distance threshold in pixels
            best_det_idx = -1

            for di in unmatched_dets:
                det = detections[di]
                dx = det["pixel_xy"][0] - trk["pixel_xy"][0]
                dy = det["pixel_xy"][1] - trk["pixel_xy"][1]
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < best_dist:
                    best_dist = dist
                    best_det_idx = di

            if best_det_idx != -1:
                matched_tracks.add(tid)
                unmatched_dets.remove(best_det_idx)
                det = detections[best_det_idx]

                # Update track with smooth spatial position (alpha blending)
                alpha = 0.70
                new_px = alpha * det["pixel_xy"][0] + (1 - alpha) * trk["pixel_xy"][0]
                new_py = alpha * det["pixel_xy"][1] + (1 - alpha) * trk["pixel_xy"][1]

                self.tracks[tid].update({
                    "bbox": det["bbox"],
                    "pixel_xy": [round(new_px, 1), round(new_py, 1)],
                    "confidence": det["confidence"],
                    "last_frame": frame_idx
                })
                self.lost_counts[tid] = 0

                updated_tracks.append({
                    "track_id": tid,
                    "bbox": det["bbox"],
                    "pixel_xy": [round(new_px, 1), round(new_py, 1)],
                    "confidence": det["confidence"],
                    "role": trk.get("role", "player"),
                    "team": trk.get("team", "unknown")
                })
            else:
                self.lost_counts[tid] += 1

        # Step 2: Spawn new tracks for unmatched detections
        for di in unmatched_dets:
            det = detections[di]
            tid = self.next_id
            self.next_id += 1

            self.tracks[tid] = {
                "track_id": tid,
                "bbox": det["bbox"],
                "pixel_xy": det["pixel_xy"],
                "confidence": det["confidence"],
                "role": "player",
                "team": "unknown",
                "last_frame": frame_idx
            }
            self.lost_counts[tid] = 0

            updated_tracks.append({
                "track_id": tid,
                "bbox": det["bbox"],
                "pixel_xy": det["pixel_xy"],
                "confidence": det["confidence"],
                "role": "player",
                "team": "unknown"
            })

        # Step 3: Remove expired tracks
        for tid in list(self.lost_counts.keys()):
            if self.lost_counts[tid] > self.max_lost:
                self.tracks.pop(tid, None)
                self.lost_counts.pop(tid, None)

        return updated_tracks
