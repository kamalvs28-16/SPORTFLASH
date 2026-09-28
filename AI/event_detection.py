import json
import os

INPUT_FILE = "results/dynamic_distance_analysis.json"
OUTPUT_FILE = "results/event_detection.json"

# ------------------------------------------------------
# Detection thresholds
# ------------------------------------------------------

SPRINT_SPEED_KMH = 25.0
HIGH_SPEED_KMH = 18.0
LOW_SPEED_KMH = 5.0

# Minimum amount of valid movement data required
# before creating a movement event.
MIN_VALID_MOVEMENTS_FOR_EVENT = 50

# Prevent isolated maximum-speed spikes from
# automatically becoming sprint events.
MAX_SPEED_AVERAGE_RATIO = 6.0

# Tracking quality warning threshold.
TRACKING_WARNING_PERCENT = 25.0


print("=" * 60)
print("SPORTFLASH IMPROVED EVENT DETECTION")
print("=" * 60)


# ------------------------------------------------------
# Load input
# ------------------------------------------------------

print("\nLoading dynamic distance analysis...")

if not os.path.exists(INPUT_FILE):
    print(f"\nERROR: Input file not found:")
    print(f"       {INPUT_FILE}")
    print("\nRun dynamic distance analysis first:")
    print("python AI\\dynamic_distance_analysis.py")
    raise SystemExit(1)


with open(INPUT_FILE, "r") as f:
    data = json.load(f)


players = data.get("players", [])

print(f"Players available: {len(players)}")


if len(players) == 0:
    print("\nERROR: No player data found.")
    raise SystemExit(1)


# ------------------------------------------------------
# Containers
# ------------------------------------------------------

events = []
player_summaries = []


# ------------------------------------------------------
# Analyse each player
# ------------------------------------------------------

for player in players:

    player_id = int(player["player_id"])

    distance = float(
        player.get("total_distance_m", 0)
    )

    average_speed = float(
        player.get("average_speed_kmh", 0)
    )

    maximum_speed = float(
        player.get("maximum_speed_kmh", 0)
    )

    valid_movements = int(
        player.get("valid_movements", 0)
    )

    rejected_movements = int(
        player.get("rejected_movements", 0)
    )

    tracked_positions = int(
        player.get("tracked_positions", 0)
    )

    active_time = float(
        player.get("active_time_seconds", 0)
    )

    player_events = []


    # --------------------------------------------------
    # Calculate rejection rate
    # --------------------------------------------------

    total_movements = (
        valid_movements +
        rejected_movements
    )

    if total_movements > 0:

        rejection_rate = (
            rejected_movements /
            total_movements
        ) * 100.0

    else:

        rejection_rate = 0.0


    # --------------------------------------------------
    # Calculate speed quality ratio
    # --------------------------------------------------

    if average_speed > 0:

        speed_ratio = (
            maximum_speed /
            average_speed
        )

    else:

        speed_ratio = None


    # --------------------------------------------------
    # Check whether enough data exists
    # --------------------------------------------------

    enough_data = (
        valid_movements >=
        MIN_VALID_MOVEMENTS_FOR_EVENT
    )


    # --------------------------------------------------
    # Check whether maximum speed is reasonable
    # --------------------------------------------------

    if speed_ratio is not None:

        speed_is_reasonable = (
            speed_ratio <=
            MAX_SPEED_AVERAGE_RATIO
        )

    else:

        speed_is_reasonable = False


    # --------------------------------------------------
    # Potential sprint
    # --------------------------------------------------

    if (
        enough_data
        and maximum_speed >= SPRINT_SPEED_KMH
        and speed_is_reasonable
    ):

        event = {
            "player_id": player_id,
            "event_type": "potential_sprint",
            "severity": "high",
            "estimated_max_speed_kmh": round(
                maximum_speed,
                2
            ),
            "estimated_average_speed_kmh": round(
                average_speed,
                2
            ),
            "confidence": "moderate",
            "description": (
                f"Player {player_id} showed "
                f"sustained movement with an "
                f"estimated maximum speed of "
                f"{maximum_speed:.2f} km/h."
            )
        }

        events.append(event)

        player_events.append(
            "potential_sprint"
        )


    # --------------------------------------------------
    # Potential high-speed movement
    # --------------------------------------------------

    elif (
        enough_data
        and maximum_speed >= HIGH_SPEED_KMH
        and speed_is_reasonable
    ):

        event = {
            "player_id": player_id,
            "event_type": "potential_high_speed_movement",
            "severity": "medium",
            "estimated_max_speed_kmh": round(
                maximum_speed,
                2
            ),
            "estimated_average_speed_kmh": round(
                average_speed,
                2
            ),
            "confidence": "moderate",
            "description": (
                f"Player {player_id} showed "
                f"potential high-speed movement."
            )
        }

        events.append(event)

        player_events.append(
            "potential_high_speed_movement"
        )


    # --------------------------------------------------
    # Low movement
    # --------------------------------------------------

    if (
        enough_data
        and average_speed < LOW_SPEED_KMH
    ):

        event = {
            "player_id": player_id,
            "event_type": "low_movement_period",
            "severity": "low",
            "estimated_average_speed_kmh": round(
                average_speed,
                2
            ),
            "confidence": "moderate",
            "description": (
                f"Player {player_id} recorded "
                f"low estimated movement speed."
            )
        }

        events.append(event)

        player_events.append(
            "low_movement_period"
        )


    # --------------------------------------------------
    # Tracking quality warning
    # --------------------------------------------------

    if (
        rejection_rate >
        TRACKING_WARNING_PERCENT
    ):

        event = {
            "player_id": player_id,
            "event_type": "tracking_quality_warning",
            "severity": "medium",
            "rejection_rate_percent": round(
                rejection_rate,
                2
            ),
            "confidence": "high",
            "description": (
                f"Player {player_id} has a "
                f"movement rejection rate of "
                f"{rejection_rate:.2f}%."
            )
        }

        events.append(event)

        player_events.append(
            "tracking_quality_warning"
        )


    # --------------------------------------------------
    # Player summary
    # --------------------------------------------------

    player_summaries.append({
        "player_id": player_id,
        "estimated_distance_m": round(
            distance,
            2
        ),
        "estimated_average_speed_kmh": round(
            average_speed,
            2
        ),
        "estimated_maximum_speed_kmh": round(
            maximum_speed,
            2
        ),
        "valid_movements": valid_movements,
        "rejected_movements": rejected_movements,
        "tracked_positions": tracked_positions,
        "active_time_seconds": round(
            active_time,
            2
        ),
        "rejection_rate_percent": round(
            rejection_rate,
            2
        ),
        "speed_quality_ratio": (
            round(speed_ratio, 2)
            if speed_ratio is not None
            else None
        ),
        "sufficient_data": enough_data,
        "detected_events": player_events
    })


# ------------------------------------------------------
# Event statistics
# ------------------------------------------------------

event_counts = {}

for event in events:

    event_type = event["event_type"]

    if event_type not in event_counts:
        event_counts[event_type] = 0

    event_counts[event_type] += 1


# ------------------------------------------------------
# Create output
# ------------------------------------------------------

output = {
    "video": data.get(
        "video",
        "videos/football.mp4"
    ),

    "method": {
        "source": (
            "Dynamic distance and speed analysis"
        ),

        "sprint_threshold_kmh":
            SPRINT_SPEED_KMH,

        "high_speed_threshold_kmh":
            HIGH_SPEED_KMH,

        "low_movement_threshold_kmh":
            LOW_SPEED_KMH,

        "minimum_valid_movements":
            MIN_VALID_MOVEMENTS_FOR_EVENT,

        "maximum_speed_average_ratio":
            MAX_SPEED_AVERAGE_RATIO,

        "tracking_warning_threshold_percent":
            TRACKING_WARNING_PERCENT,

        "classification":
            "Potential/estimated events",

        "warning": (
            "Events are estimates because the "
            "current dynamic calibration does not "
            "recompute a frame-specific homography."
        )
    },

    "summary": {
        "players_analysed": len(players),
        "total_events": len(events),
        "event_counts": event_counts
    },

    "events": events,

    "player_summaries": player_summaries
}


# ------------------------------------------------------
# Save output
# ------------------------------------------------------

os.makedirs(
    "results",
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w"
) as f:

    json.dump(
        output,
        f,
        indent=2
    )


# ------------------------------------------------------
# Console output
# ------------------------------------------------------

print("\n" + "=" * 60)
print("IMPROVED EVENT DETECTION SUMMARY")
print("=" * 60)

print(
    f"\nPlayers analysed: {len(players)}"
)

print(
    f"Total events detected: {len(events)}"
)

print("\nEvent types:")

if event_counts:

    for event_type, count in event_counts.items():

        print(
            f"  {event_type}: {count}"
        )

else:

    print("  No events detected")


# ------------------------------------------------------
# Top players by distance
# ------------------------------------------------------

print("\nTop player movement summaries:")

sorted_players = sorted(
    player_summaries,
    key=lambda x: x["estimated_distance_m"],
    reverse=True
)


for index, player in enumerate(
    sorted_players[:10],
    start=1
):

    print(
        f"\n{index}. Player "
        f"{player['player_id']}"
    )

    print(
        f"   Distance: "
        f"{player['estimated_distance_m']:.2f} m"
    )

    print(
        f"   Average speed: "
        f"{player['estimated_average_speed_kmh']:.2f} km/h"
    )

    print(
        f"   Maximum speed: "
        f"{player['estimated_maximum_speed_kmh']:.2f} km/h"
    )

    print(
        f"   Valid movements: "
        f"{player['valid_movements']}"
    )

    print(
        f"   Rejection rate: "
        f"{player['rejection_rate_percent']:.2f}%"
    )

    detected_events = player["detected_events"]

    if detected_events:

        print(
            "   Events: "
            + ", ".join(detected_events)
        )

    else:

        print(
            "   Events: None"
        )


# ------------------------------------------------------
# Finished
# ------------------------------------------------------

print("\n" + "=" * 60)
print("EVENT DETECTION COMPLETED")
print("=" * 60)

print(
    f"\nOutput file: ✓ {OUTPUT_FILE}"
)

print(
    "\nNOTE:"
)

print(
    "Events are potential/estimated movement events."
)

print(
    "They should not be presented as "
    "ground-truth football events."
)