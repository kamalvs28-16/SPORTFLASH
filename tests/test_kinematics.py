import unittest
import math


def compute_speed_and_distance(positions: list, fps: float = 30.0) -> tuple:
    """
    Helper function to compute total distance (m) and average speed (km/h)
    from pitch position trajectory list: [(frame, x_m, y_m), ...]
    """
    if len(positions) < 2:
        return 0.0, 0.0

    total_dist = 0.0
    speeds_kmh = []

    for i in range(1, len(positions)):
        f0, x0, y0 = positions[i - 1]
        f1, x1, y1 = positions[i]

        dt = (f1 - f0) / fps
        if dt <= 0:
            continue

        dx = x1 - x0
        dy = y1 - y0
        step_dist = math.sqrt(dx * dx + dy * dy)

        # Physics jump filter ( Usain bolt max speed ~12m/s )
        if step_dist / dt > 15.0:
            continue

        total_dist += step_dist
        v_kmh = (step_dist / dt) * 3.6
        speeds_kmh.append(v_kmh)

    avg_speed = float(sum(speeds_kmh) / len(speeds_kmh)) if speeds_kmh else 0.0
    return round(total_dist, 2), round(avg_speed, 2)


class TestKinematicsSynthetic(unittest.TestCase):

    def test_known_10m_in_2s_equals_18kmh(self):
        """
        Non-negotiable requirement test:
        A player moving 10 meters in 2 seconds at 30 fps must equal 18.0 km/h.
        """
        fps = 30.0
        start_frame = 1
        end_frame = int(start_frame + 2.0 * fps)  # 60 frames

        positions = []
        for f in range(start_frame, end_frame + 1):
            t = (f - start_frame) / fps  # 0 to 2.0 s
            x = (t / 2.0) * 10.0          # 0 to 10.0 m
            y = 0.0
            positions.append((f, x, y))

        dist, avg_speed = compute_speed_and_distance(positions, fps=fps)

        self.assertAlmostEqual(dist, 10.0, delta=0.05)
        self.assertAlmostEqual(avg_speed, 18.0, delta=0.1)

    def test_stationary_player(self):
        fps = 30.0
        positions = [(f, 15.0, 20.0) for f in range(1, 61)]
        dist, avg_speed = compute_speed_and_distance(positions, fps=fps)

        self.assertEqual(dist, 0.0)
        self.assertEqual(avg_speed, 0.0)


if __name__ == "__main__":
    unittest.main()
