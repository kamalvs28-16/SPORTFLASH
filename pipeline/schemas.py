from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CanonicalTrackRow(BaseModel):
    """
    Single source of truth tracking record per detected object per frame.
    Strictly follows Non-Negotiable Rule 4.
    """
    frame: int = Field(..., description="Frame index (1-based)")
    time: float = Field(..., description="Timestamp in seconds from video start")
    track_id: int = Field(..., description="Persistent ByteTrack track identifier")
    player_id: Optional[str] = Field(None, description="Linked roster player ID if assigned")
    team: str = Field("unknown", description="Team classification: 'Team A', 'Team B', 'Referee', 'Goalkeeper', 'unknown'")
    role: str = Field("player", description="Role: 'player', 'goalkeeper', 'referee', 'ball'")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2] in pixels")
    pixel_xy: List[float] = Field(..., description="Pixel anchor point [x, y] (bottom center for players, center for ball)")
    pitch_xy: Optional[List[float]] = Field(None, description="Calibrated pitch coordinates in meters [x_m, y_m] (0..105, 0..68)")
    confidence: float = Field(..., description="Detection confidence score (0.0 to 1.0)")
    is_interpolated: bool = Field(False, description="Flag indicating if position was interpolated/predicted")
    is_replay: bool = Field(False, description="Flag indicating if frame belongs to a replay clip")
    scene_id: int = Field(1, description="Scene / shot segment index")


class CanonicalTrackFrame(BaseModel):
    """
    Frame-level aggregated state containing all active tracks and ball state.
    """
    frame: int
    time: float
    scene_id: int = 1
    is_replay: bool = False
    players: List[CanonicalTrackRow] = []
    ball: Optional[CanonicalTrackRow] = None


class DataQualityBadge(BaseModel):
    """
    Data quality and confidence metadata attached to all analytics outputs (Rule 3).
    """
    overall_confidence: float = Field(..., description="Weighted average confidence score (0.0 to 1.0)")
    data_quality: str = Field("HIGH", description="Quality badge: 'HIGH' (>=0.85), 'MEDIUM' (>=0.65), 'LOW' (<0.65)")
    track_stability_ratio: float = Field(..., description="Ratio of stable tracks without rapid switching")
    modified_frame_count: int = Field(0, description="Total count of frames modified by filters/interpolation (Rule 2)")
    modification_logs: List[str] = Field(default_factory=list, description="Audit log of applied filters & counts")
    has_sufficient_data: bool = Field(True, description="False if data is corrupted or insufficient (Rule 1)")
