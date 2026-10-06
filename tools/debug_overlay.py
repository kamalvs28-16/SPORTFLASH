import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


def hex_to_bgr(hex_str: str, default_bgr=(255, 255, 255)) -> Tuple[int, int, int]:
    try:
        hex_clean = hex_str.lstrip('#')
        if len(hex_clean) == 6:
            r = int(hex_clean[0:2], 16)
            g = int(hex_clean[2:4], 16)
            b = int(hex_clean[4:6], 16)
            return (b, g, r)
    except Exception:
        pass
    return default_bgr


class DebugOverlayRenderer:
    """
    Renders high-quality diagnostic visual overlays on broadcast video frames.
    Includes:
    - Bounding boxes, track IDs, roles, team colors
    - Pitch boundary mask outline
    - Ball motion trail & prediction indicators
    - 2D Top-Down Minimap Tactical Pitch Overlay (Phase 2)
    - Telemetry & Calibration Error Banner
    """

    TEAM_COLORS = {
        "Team A": (60, 60, 240),      # Red BGR
        "Team B": (240, 200, 60),     # Cyan/Yellow BGR
        "Referee": (220, 220, 50),    # Bright Yellow BGR
        "Goalkeeper": (50, 220, 50),  # Neon Green BGR
        "unknown": (180, 180, 180)   # Gray BGR
    }

    def render_minimap(
        self,
        players: List[Dict[str, Any]],
        ball: Optional[Dict[str, Any]],
        map_w: int = 240,
        map_h: int = 155
    ) -> np.ndarray:
        """
        Renders 2D top-down tactical pitch minimap (105m x 68m coordinate projection).
        """
        minimap = np.zeros((map_h, map_w, 3), dtype=np.uint8)
        minimap[:] = (20, 75, 30)  # Pitch Green

        # Pitch Boundary & Markings
        margin = 10
        pw = map_w - 2 * margin
        ph = map_h - 2 * margin

        cv2.rectangle(minimap, (margin, margin), (map_w - margin, map_h - margin), (255, 255, 255), 1)
        # Halfway line
        mid_x = margin + pw // 2
        cv2.line(minimap, (mid_x, margin), (mid_x, map_h - margin), (255, 255, 255), 1)
        # Center circle
        cv2.circle(minimap, (mid_x, map_h // 2), int(ph * 0.15), (255, 255, 255), 1)

        scale_x = pw / 105.0
        scale_y = ph / 68.0

        # Render Players on Minimap
        for p in players:
            pitch_xy = p.get("pitch_xy")
            if pitch_xy is None:
                continue

            xm, ym = pitch_xy
            mx = int(margin + xm * scale_x)
            my = int(margin + ym * scale_y)

            team = p.get("team", "unknown")
            color = self.TEAM_COLORS.get(team, (180, 180, 180))

            cv2.circle(minimap, (mx, my), 5, color, -1)
            cv2.circle(minimap, (mx, my), 6, (0, 0, 0), 1)

        # Render Ball on Minimap
        if ball is not None and ball.get("pitch_xy") is not None:
            bxm, bym = ball["pitch_xy"]
            bmx = int(margin + bxm * scale_x)
            bmy = int(margin + bym * scale_y)
            cv2.circle(minimap, (bmx, bmy), 4, (0, 140, 255), -1)

        return minimap

    def render_frame(
        self,
        frame: np.ndarray,
        players: List[Dict[str, Any]],
        ball: Optional[Dict[str, Any]],
        ball_trail: List[Tuple[float, float]],
        pitch_mask: Optional[np.ndarray] = None,
        reproj_error: float = 0.0,
        frame_idx: int = 0,
        fps: float = 30.0,
        scene_id: int = 1,
        is_replay: bool = False
    ) -> np.ndarray:
        out_frame = frame.copy()

        # 1. Pitch Mask Outline Overlay
        if pitch_mask is not None:
            contours, _ = cv2.findContours(pitch_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cv2.drawContours(out_frame, contours, -1, (0, 255, 120), 2)

        # 2. Render Player Bounding Boxes & Identifiers
        for p in players:
            bx1, by1, bx2, by2 = [int(v) for v in p["bbox"]]
            tid = p.get("track_id", p.get("player_id", "?"))
            team = p.get("team", "unknown")
            conf = p.get("confidence", 0.0)

            color = self.TEAM_COLORS.get(team, (180, 180, 180))

            # Bounding Box
            cv2.rectangle(out_frame, (bx1, by1), (bx2, by2), color, 2)

            # Foot anchor point indicator
            px, py = [int(v) for v in p.get("pixel_xy", [(bx1 + bx2) / 2, by2])]
            cv2.circle(out_frame, (px, py), 4, color, -1)

            # Text Tag Header with pitch_xy if available
            pitch_str = ""
            if p.get("pitch_xy") is not None:
                pitch_str = f" [{p['pitch_xy'][0]:.1f},{p['pitch_xy'][1]:.1f}m]"

            label = f"#{tid} {team[:6]}{pitch_str}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
            cv2.rectangle(out_frame, (bx1, max(0, by1 - 18)), (bx1 + w + 4, max(0, by1)), color, -1)
            cv2.putText(out_frame, label, (bx1 + 2, max(12, by1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1)

        # 3. Render Ball Detection & Motion Trail
        if ball_trail and len(ball_trail) > 1:
            for i in range(1, len(ball_trail)):
                pt1 = (int(ball_trail[i - 1][0]), int(ball_trail[i - 1][1]))
                pt2 = (int(ball_trail[i][0]), int(ball_trail[i][1]))
                alpha = float(i) / len(ball_trail)
                thickness = int(1 + alpha * 3)
                cv2.line(out_frame, pt1, pt2, (0, 165, 255), thickness)

        if ball is not None:
            bx1, by1, bx2, by2 = [int(v) for v in ball["bbox"]]
            b_conf = ball.get("confidence", 0.0)
            is_interp = ball.get("is_interpolated", False)

            b_color = (0, 140, 255) if not is_interp else (0, 255, 255)
            cv2.circle(out_frame, (int((bx1 + bx2) / 2), int((by1 + by2) / 2)), 8, b_color, 2)
            cv2.circle(out_frame, (int((bx1 + bx2) / 2), int((by1 + by2) / 2)), 3, b_color, -1)

            ball_tag = f"BALL {b_conf:.2f}" + (" [PRED]" if is_interp else "")
            cv2.putText(out_frame, ball_tag, (bx1 - 10, max(15, by1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.40, b_color, 1)

        # 4. Render 2D Top-Down Minimap (Phase 2 Requirement)
        minimap = self.render_minimap(players, ball)
        mm_h, mm_w = minimap.shape[:2]
        margin_r = 15
        margin_t = 50
        out_frame[margin_t:margin_t + mm_h, out_frame.shape[1] - mm_w - margin_r:out_frame.shape[1] - margin_r] = minimap
        cv2.rectangle(
            out_frame,
            (out_frame.shape[1] - mm_w - margin_r, margin_t),
            (out_frame.shape[1] - margin_r, margin_t + mm_h),
            (255, 255, 255), 1
        )

        # 5. Diagnostic Telemetry & Calibration Banner
        time_sec = frame_idx / max(1.0, fps)
        banner_h = 42
        cv2.rectangle(out_frame, (0, 0), (out_frame.shape[1], banner_h), (12, 16, 24), -1)
        cv2.line(out_frame, (0, banner_h), (out_frame.shape[1], banner_h), (16, 185, 129), 1)

        telemetry_txt = (
            f"SPORTFLASH PHASE 2 CALIBRATION | Frame: {frame_idx} ({time_sec:.1f}s) | "
            f"Players: {len(players)} | Reproj Error: {reproj_error:.2f}m | "
            f"Scene: {scene_id} | Ball: {'TRACKED' if ball and not ball.get('is_interpolated') else 'PREDICTED' if ball else 'LOST'}"
        )
        cv2.putText(out_frame, telemetry_txt, (14, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1)

        return out_frame
