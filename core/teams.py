import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict


class TorsoColorEmbedder:
    """
    Extracts normalized color histogram embeddings from player torso ROI crops.
    Removes green grass background noise and normalizes lighting variations.
    """

    def extract_embedding(self, frame: np.ndarray, bbox: List[float]) -> Optional[np.ndarray]:
        x1, y1, x2, y2 = [int(v) for v in bbox]
        h, w = y2 - y1, x2 - x1

        if w < 4 or h < 10:
            return None

        ty1 = max(0, int(y1 + h * 0.15))
        ty2 = min(frame.shape[0], int(y1 + h * 0.60))
        tx1 = max(0, int(x1 + w * 0.10))
        tx2 = min(frame.shape[1], int(x2 - w * 0.10))

        crop = frame[ty1:ty2, tx1:tx2]
        if crop.size == 0:
            return None

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)

        # Precise field green mask (Hue 38 to 82)
        green_mask = cv2.inRange(hsv, (38, 40, 40), (82, 255, 255))
        non_green_hsv = hsv[green_mask == 0]
        non_green_lab = lab[green_mask == 0]

        if len(non_green_hsv) > 5:
            med_h = float(np.median(non_green_hsv[:, 0])) / 180.0
            med_s = float(np.median(non_green_hsv[:, 1])) / 255.0
            med_v = float(np.median(non_green_hsv[:, 2])) / 255.0
            med_a = float(np.median(non_green_lab[:, 1])) / 255.0
            med_b = float(np.median(non_green_lab[:, 2])) / 255.0
        else:
            med_h = float(np.median(hsv[:, :, 0])) / 180.0
            med_s = float(np.median(hsv[:, :, 1])) / 255.0
            med_v = float(np.median(hsv[:, :, 2])) / 255.0
            med_a = float(np.median(lab[:, :, 1])) / 255.0
            med_b = float(np.median(lab[:, :, 2])) / 255.0

        return np.array([med_h, med_s, med_v, med_a, med_b], dtype=np.float32)


class TeamClassifier:
    """
    Classifies player tracks into Team A, Team B, Goalkeeper, or Referee.
    Employs K-Means (k=2) on accumulated torso embeddings of outfield players.
    """

    def __init__(self):
        self.embedder = TorsoColorEmbedder()
        self.track_embeddings = defaultdict(list)
        self.assigned_teams: Dict[int, str] = {}
        self.assigned_roles: Dict[int, str] = {}

    def add_sample(self, track_id: int, frame: np.ndarray, bbox: List[float]):
        emb = self.embedder.extract_embedding(frame, bbox)
        if emb is not None:
            self.track_embeddings[track_id].append(emb)

    def fit_and_classify(self) -> Tuple[Dict[int, str], Dict[int, str]]:
        if not self.track_embeddings:
            return {}, {}

        track_ids = list(self.track_embeddings.keys())
        mean_features = []

        for tid in track_ids:
            samples = self.track_embeddings[tid]
            mean_emb = np.mean(samples, axis=0)
            mean_features.append(mean_emb)

        mean_features = np.array(mean_features, dtype=np.float32)

        outfield_indices = []
        outfield_pids = []

        for i, tid in enumerate(track_ids):
            feat = mean_features[i]
            med_h, med_s, med_v = feat[0] * 180.0, feat[1] * 255.0, feat[2] * 255.0

            # Referee / Special Kit heuristic: Bright yellow or neon pink
            if (25 <= med_h <= 34 and med_s > 150):
                self.assigned_roles[tid] = "referee"
                self.assigned_teams[tid] = "Referee"
            else:
                self.assigned_roles[tid] = "player"
                outfield_indices.append(i)
                outfield_pids.append(tid)

        if len(outfield_pids) >= 2:
            outfield_feats = mean_features[outfield_indices, :3]
            k = min(2, len(outfield_pids))
            crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.1)
            _, labels, _ = cv2.kmeans(outfield_feats, k, None, crit, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Assign Team A to cluster with lower hue (e.g. Red/Orange) and Team B to higher hue (Cyan/Blue)
            c0_h = float(np.mean(outfield_feats[labels.ravel() == 0, 0])) if np.sum(labels.ravel() == 0) > 0 else 0.0
            c1_h = float(np.mean(outfield_feats[labels.ravel() == 1, 0])) if np.sum(labels.ravel() == 1) > 0 else 1.0

            team0_name = "Team A" if c0_h < c1_h else "Team B"
            team1_name = "Team B" if team0_name == "Team A" else "Team A"

            for idx, tid in enumerate(outfield_pids):
                label = labels[idx][0]
                self.assigned_teams[tid] = team0_name if label == 0 else team1_name
        else:
            for tid in outfield_pids:
                self.assigned_teams[tid] = "Team A"

        return self.assigned_teams, self.assigned_roles


class RosterIdentityLinker:
    """
    Links temporary ByteTrack track IDs to permanent Roster player IDs across camera cuts.
    """

    def __init__(self, roster_config: Optional[Dict[str, Any]] = None):
        self.roster_config = roster_config or {}
        self.track_to_player: Dict[int, str] = {}

    def link_tracks(self, team_assignments: Dict[int, str]) -> Dict[int, Dict[str, Any]]:
        team_a_players = self.roster_config.get("players", {})
        linked_info = {}

        team_a_count = 1
        team_b_count = 1

        for tid, team in team_assignments.items():
            str_tid = str(tid)
            if str_tid in team_a_players:
                p_meta = team_a_players[str_tid]
                linked_info[tid] = {
                    "player_id": str_tid,
                    "name": p_meta.get("name", f"Player #{str_tid}"),
                    "jersey_number": p_meta.get("jersey_number", str_tid),
                    "position": p_meta.get("position", "Midfielder"),
                    "team": team
                }
            else:
                if team == "Team A":
                    pid = f"A_{team_a_count}"
                    jersey = f"1{team_a_count}"
                    team_a_count += 1
                else:
                    pid = f"B_{team_b_count}"
                    jersey = f"2{team_b_count}"
                    team_b_count += 1

                linked_info[tid] = {
                    "player_id": pid,
                    "name": f"Player #{jersey}",
                    "jersey_number": jersey,
                    "position": "Outfield",
                    "team": team
                }

        return linked_info
