import unittest
from pipeline.schemas import CanonicalTrackRow, CanonicalTrackFrame, DataQualityBadge


class TestPipelineSchemas(unittest.TestCase):

    def test_canonical_track_row_valid(self):
        row = CanonicalTrackRow(
            frame=1,
            time=0.033,
            track_id=10,
            player_id="10",
            team="Team A",
            role="player",
            bbox=[100.0, 200.0, 150.0, 300.0],
            pixel_xy=[125.0, 300.0],
            pitch_xy=[52.5, 34.0],
            confidence=0.92,
            is_interpolated=False,
            is_replay=False,
            scene_id=1
        )
        self.assertEqual(row.frame, 1)
        self.assertEqual(row.team, "Team A")
        self.assertAlmostEqual(row.confidence, 0.92)

    def test_data_quality_badge(self):
        badge = DataQualityBadge(
            overall_confidence=0.88,
            data_quality="HIGH",
            track_stability_ratio=0.91,
            modified_frame_count=4,
            modification_logs=["Interpolated 4 ball positions"]
        )
        self.assertTrue(badge.has_sufficient_data)
        self.assertEqual(badge.data_quality, "HIGH")


if __name__ == "__main__":
    unittest.main()
