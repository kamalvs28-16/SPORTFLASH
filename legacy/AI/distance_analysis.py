import json
import os
import math


# ============================================================
# SPORTFLASH - ROBUST DISTANCE & SPEED ANALYSIS
# ============================================================

print("=" * 60)
print("SPORTFLASH DISTANCE & SPEED ANALYSIS")
print("=" * 60)


# ============================================================
# FILES
# ============================================================

HOMOGRAPHY_FILE = "results/homography_positions.json"
OUTPUT_FILE = "results/distance_analysis.json"


# ============================================================
# SETTINGS
# ============================================================

# Maximum realistic instantaneous player speed.
# 12 m/s = 43.2 km/h.
MAX_SPEED_MPS = 12.0

MAX_SPEED_KMH = MAX_SPEED_MPS * 3.6

# Ignore extremely large position jumps.
MAX_FRAME_DISTANCE_M = 3.0

# Minimum number of valid movements required.
MIN_VALID_MOVEMENTS = 3


# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.exists(HOMOGRAPHY_FILE):

    print()
    print("ERROR: Homography file not found:")
    print(HOMOGRAPHY_FILE)
    exit()


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading homography positions...")

with open(HOMOGRAPHY_FILE, "r") as f:
    data = json.load(f)

print("Homography data loaded.")


frames = data.get("frames", [])

fps = float(data.get("fps", 0))


if not frames:

    print()
    print("ERROR: No tracking frames found.")
    exit()


if fps <= 0:

    print()
    print("ERROR: Invalid FPS.")
    exit()


print()
print(f"Frames available: {len(frames)}")
print(f"FPS: {fps:.2f}")


# ============================================================
# COLLECT PLAYER POSITIONS
# ============================================================

player_positions = {}


print()
print("Collecting player positions...")


for frame_data in frames:

    frame_number = frame_data.get("frame")

    players = frame_data.get(
        "players",
        []
    )


    for player in players:

        player_id = str(
            player.get("player_id")
        )


        if (
            "pitch_x_m" not in player
            or "pitch_y_m" not in player
        ):
            continue


        x = float(
            player["pitch_x_m"]
        )

        y = float(
            player["pitch_y_m"]
        )


        if player_id not in player_positions:

            player_positions[player_id] = []


        player_positions[player_id].append(

            {
                "frame": frame_number,
                "x": x,
                "y": y
            }

        )


print(
    f"Unique players found: "
    f"{len(player_positions)}"
)


# ============================================================
# ANALYZE EACH PLAYER
# ============================================================

results = {}


for player_id, positions in player_positions.items():

    if len(positions) < 2:

        continue


    total_distance = 0.0

    valid_distances = []

    valid_speeds = []

    rejected_jumps = 0


    # --------------------------------------------------------
    # Consecutive positions
    # --------------------------------------------------------

    for i in range(1, len(positions)):

        previous = positions[i - 1]

        current = positions[i]


        frame_difference = (
            current["frame"] -
            previous["frame"]
        )


        if frame_difference <= 0:

            continue


        time_seconds = (
            frame_difference / fps
        )


        if time_seconds <= 0:

            continue


        dx = (
            current["x"] -
            previous["x"]
        )

        dy = (
            current["y"] -
            previous["y"]
        )


        distance = math.sqrt(
            dx * dx +
            dy * dy
        )


        # ----------------------------------------------------
        # Calculate speed
        # ----------------------------------------------------

        speed_mps = (
            distance /
            time_seconds
        )


        speed_kmh = (
            speed_mps * 3.6
        )


        # ----------------------------------------------------
        # REJECT TRACKING JUMPS
        # ----------------------------------------------------

        if distance > MAX_FRAME_DISTANCE_M:

            rejected_jumps += 1

            continue


        # ----------------------------------------------------
        # REJECT UNREALISTIC SPEED
        # ----------------------------------------------------

        if speed_mps > MAX_SPEED_MPS:

            rejected_jumps += 1

            continue


        # ----------------------------------------------------
        # Accept valid movement
        # ----------------------------------------------------

        total_distance += distance

        valid_distances.append(
            distance
        )

        valid_speeds.append(
            speed_kmh
        )


    # --------------------------------------------------------
    # Minimum valid movement check
    # --------------------------------------------------------

    if len(valid_distances) < MIN_VALID_MOVEMENTS:

        continue


    # --------------------------------------------------------
    # Average speed
    # --------------------------------------------------------

    average_speed = (
        sum(valid_speeds) /
        len(valid_speeds)
    )


    # --------------------------------------------------------
    # Maximum speed
    # --------------------------------------------------------

    maximum_speed = max(
        valid_speeds
    )


    # --------------------------------------------------------
    # Active tracking time
    # --------------------------------------------------------

    first_frame = positions[0]["frame"]

    last_frame = positions[-1]["frame"]


    active_time = (
        last_frame -
        first_frame
    ) / fps


    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    results[player_id] = {

        "total_distance_m":
            round(
                total_distance,
                2
            ),

        "total_distance_km":
            round(
                total_distance / 1000,
                4
            ),

        "average_speed_kmh":
            round(
                average_speed,
                2
            ),

        "maximum_speed_kmh":
            round(
                maximum_speed,
                2
            ),

        "tracked_positions":
            len(positions),

        "valid_movements":
            len(valid_distances),

        "rejected_movements":
            rejected_jumps,

        "active_time_seconds":
            round(
                active_time,
                2
            )

    }


# ============================================================
# SORT BY DISTANCE
# ============================================================

sorted_players = sorted(

    results.items(),

    key=lambda item:
        item[1]["total_distance_m"],

    reverse=True

)


# ============================================================
# RANKING
# ============================================================

distance_ranking = []


for rank, (
    player_id,
    player_data
) in enumerate(
    sorted_players,
    start=1
):

    distance_ranking.append(

        {

            "rank": rank,

            "player_id":
                player_id,

            "total_distance_m":
                player_data[
                    "total_distance_m"
                ],

            "total_distance_km":
                player_data[
                    "total_distance_km"
                ],

            "average_speed_kmh":
                player_data[
                    "average_speed_kmh"
                ],

            "maximum_speed_kmh":
                player_data[
                    "maximum_speed_kmh"
                ]

        }

    )


# ============================================================
# FINAL OUTPUT
# ============================================================

output = {

    "video":
        data.get(
            "video",
            "videos/football.mp4"
        ),

    "fps":
        fps,

    "coordinate_system":
        {

            "pitch_length_m":
                105.0,

            "pitch_width_m":
                68.0

        },

    "analysis_method":
        {

            "coordinate_source":
                "homography",

            "distance_unit":
                "meters",

            "speed_unit":
                "km/h",

            "maximum_accepted_speed_kmh":
                MAX_SPEED_KMH,

            "maximum_frame_distance_m":
                MAX_FRAME_DISTANCE_M,

            "tracking_jump_filter":
                True

        },

    "total_players":
        len(results),

    "players":
        results,

    "distance_ranking":
        distance_ranking

}


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_FILE,
    "w"
) as f:

    json.dump(
        output,
        f,
        indent=4
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 60)
print("FILTERED DISTANCE ANALYSIS")
print("=" * 60)

print()
print(
    f"Maximum accepted speed: "
    f"{MAX_SPEED_KMH:.1f} km/h"
)

print(
    f"Maximum frame movement: "
    f"{MAX_FRAME_DISTANCE_M:.1f} m"
)


print()

for rank, (
    player_id,
    player_data
) in enumerate(
    sorted_players[:10],
    start=1
):

    print(
        f"{rank}. Player {player_id}"
    )

    print(
        f"   Distance: "
        f"{player_data['total_distance_m']:.2f} m"
    )

    print(
        f"   Average speed: "
        f"{player_data['average_speed_kmh']:.2f} km/h"
    )

    print(
        f"   Maximum speed: "
        f"{player_data['maximum_speed_kmh']:.2f} km/h"
    )

    print(
        f"   Valid movements: "
        f"{player_data['valid_movements']}"
    )

    print(
        f"   Rejected jumps: "
        f"{player_data['rejected_movements']}"
    )

    print()


# ============================================================
# COMPLETION
# ============================================================

print("=" * 60)
print("DISTANCE ANALYSIS COMPLETED")
print("=" * 60)

print()
print(
    f"Players analysed: "
    f"{len(results)}"
)

print()
print(
    f"Output file: "
    f"✓ {OUTPUT_FILE}"
)

print()
print("Tracking-jump filtering applied.")

print()
print("Next module after verification:")
print("camera_motion.py")