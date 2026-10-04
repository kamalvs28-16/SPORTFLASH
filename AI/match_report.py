import json
import os


# ============================================================
# FILE PATHS
# ============================================================

TEAM_FILE = "results/team_classification.json"
CAMERA_FILE = "results/camera_motion.json"
CALIBRATION_FILE = "results/dynamic_calibration.json"
DISTANCE_FILE = "results/dynamic_distance_analysis.json"
EVENT_FILE = "results/event_detection.json"

OUTPUT_FILE = "results/match_report.json"


# ============================================================
# HELPER FUNCTION
# ============================================================

def load_json(file_path):
    """Load a JSON file safely."""

    if not os.path.exists(file_path):
        print(f"\nERROR: File not found:")
        print(f"       {file_path}")
        raise SystemExit(1)

    with open(file_path, "r") as file:
        return json.load(file)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("SPORTFLASH MATCH REPORT GENERATOR")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading analysis results...")

team_data = load_json(TEAM_FILE)
camera_data = load_json(CAMERA_FILE)
calibration_data = load_json(CALIBRATION_FILE)
distance_data = load_json(DISTANCE_FILE)
event_data = load_json(EVENT_FILE)

print("[OK] Team classification loaded")
print("[OK] Camera motion loaded")
print("[OK] Dynamic calibration loaded")
print("[OK] Dynamic distance analysis loaded")
print("[OK] Event detection loaded")


# ============================================================
# TEAM INFORMATION
# ============================================================

team_summary = team_data.get("summary", {})

total_team_players = int(
    team_summary.get("total_players", 0)
)

team_a_players = team_summary.get(
    "team_a_players",
    []
)

team_b_players = team_summary.get(
    "team_b_players",
    []
)

team_a_count = int(
    team_summary.get("team_a_count", 0)
)

team_b_count = int(
    team_summary.get("team_b_count", 0)
)


# ============================================================
# CAMERA INFORMATION
# ============================================================

camera_summary = camera_data.get(
    "summary",
    {}
)

average_translation = float(
    camera_summary.get(
        "average_translation_pixels",
        0
    )
)

maximum_translation = float(
    camera_summary.get(
        "maximum_translation_pixels",
        0
    )
)

average_rotation = float(
    camera_summary.get(
        "average_rotation_degrees",
        0
    )
)

maximum_rotation = float(
    camera_summary.get(
        "maximum_rotation_degrees",
        0
    )
)

stable_frames = int(
    camera_summary.get(
        "stable_frames",
        0
    )
)

moving_frames = int(
    camera_summary.get(
        "moving_frames",
        0
    )
)

motion_counts = camera_summary.get(
    "motion_counts",
    {}
)


# ============================================================
# DYNAMIC CALIBRATION INFORMATION
# ============================================================

calibration_summary = calibration_data.get(
    "summary",
    {}
)

homography_frames = int(
    calibration_summary.get(
        "homography_frames",
        0
    )
)

camera_motion_frames = int(
    calibration_summary.get(
        "camera_motion_frames",
        0
    )
)

total_player_positions = int(
    calibration_summary.get(
        "total_player_positions",
        0
    )
)

reliable_matches = int(
    calibration_summary.get(
        "reliable_camera_matches",
        0
    )
)

unreliable_matches = int(
    calibration_summary.get(
        "unreliable_camera_matches",
        0
    )
)

total_matches = (
    reliable_matches +
    unreliable_matches
)

if total_matches > 0:

    calibration_reliability = (
        reliable_matches /
        total_matches
    ) * 100

else:

    calibration_reliability = 0.0


# ============================================================
# DISTANCE AND SPEED INFORMATION
# ============================================================

distance_players = distance_data.get(
    "players",
    []
)

distance_summary = distance_data.get(
    "summary",
    {}
)

players_analysed = int(
    distance_summary.get(
        "players_analysed",
        len(distance_players)
    )
)

total_players_detected = int(
    distance_summary.get(
        "total_players_detected",
        0
    )
)


# ============================================================
# SORT PLAYERS BY DISTANCE
# ============================================================

players_by_distance = sorted(
    distance_players,
    key=lambda player:
        player.get(
            "total_distance_m",
            0
        ),
    reverse=True
)


# ============================================================
# SORT PLAYERS BY MAXIMUM SPEED
# ============================================================

players_by_max_speed = sorted(
    distance_players,
    key=lambda player:
        player.get(
            "maximum_speed_kmh",
            0
        ),
    reverse=True
)


# ============================================================
# SORT PLAYERS BY AVERAGE SPEED
# ============================================================

players_by_average_speed = sorted(
    distance_players,
    key=lambda player:
        player.get(
            "average_speed_kmh",
            0
        ),
    reverse=True
)


# ============================================================
# TOP MOVEMENT PLAYER
# ============================================================

if players_by_distance:

    top_distance_player = (
        players_by_distance[0]
    )

else:

    top_distance_player = {}


# ============================================================
# TOP MAX SPEED PLAYER
# ============================================================

if players_by_max_speed:

    top_speed_player = (
        players_by_max_speed[0]
    )

else:

    top_speed_player = {}


# ============================================================
# TOP AVERAGE SPEED PLAYER
# ============================================================

if players_by_average_speed:

    top_average_speed_player = (
        players_by_average_speed[0]
    )

else:

    top_average_speed_player = {}


# ============================================================
# EVENT INFORMATION
# ============================================================

event_summary = event_data.get(
    "summary",
    {}
)

total_events = int(
    event_summary.get(
        "total_events",
        0
    )
)

event_counts = event_summary.get(
    "event_counts",
    {}
)

all_events = event_data.get(
    "events",
    []
)


# ============================================================
# EVENTS BY TYPE
# ============================================================

potential_sprints = [
    event
    for event in all_events
    if event.get("event_type")
    == "potential_sprint"
]

low_movement_events = [
    event
    for event in all_events
    if event.get("event_type")
    == "low_movement_period"
]

tracking_warnings = [
    event
    for event in all_events
    if event.get("event_type")
    == "tracking_quality_warning"
]

high_speed_events = [
    event
    for event in all_events
    if event.get("event_type")
    == "potential_high_speed_movement"
]


# ============================================================
# PLAYER REPORTS
# ============================================================

player_reports = []

for player in distance_players:

    player_id = int(
        player.get(
            "player_id",
            0
        )
    )

    # Determine team
    if player_id in team_a_players:

        team = "Team A"

    elif player_id in team_b_players:

        team = "Team B"

    else:

        team = "Unclassified"

    player_reports.append({

        "player_id":
            player_id,

        "team":
            team,

        "estimated_distance_m":
            player.get(
                "total_distance_m",
                0
            ),

        "estimated_distance_km":
            player.get(
                "total_distance_km",
                0
            ),

        "estimated_average_speed_kmh":
            player.get(
                "average_speed_kmh",
                0
            ),

        "estimated_maximum_speed_kmh":
            player.get(
                "maximum_speed_kmh",
                0
            ),

        "valid_movements":
            player.get(
                "valid_movements",
                0
            ),

        "rejected_movements":
            player.get(
                "rejected_movements",
                0
            ),

        "tracked_positions":
            player.get(
                "tracked_positions",
                0
            ),

        "active_time_seconds":
            player.get(
                "active_time_seconds",
                0
            )
    })


# ============================================================
# FINAL REPORT
# ============================================================

report = {

    "project": "SPORTFLASH",

    "report_type":
        "AI Football Performance Analytics Report",

    "data_status":
        "Potential/estimated analytics",

    "warning":
        (
            "Distance, speed and movement events are "
            "estimates. The current dynamic calibration "
            "aligns camera-motion information with "
            "homography positions but does not recompute "
            "a frame-specific homography."
        ),

    # --------------------------------------------------------
    # Team section
    # --------------------------------------------------------

    "team_analysis": {

        "total_classified_players":
            total_team_players,

        "team_a_count":
            team_a_count,

        "team_b_count":
            team_b_count,

        "team_a_players":
            team_a_players,

        "team_b_players":
            team_b_players
    },

    # --------------------------------------------------------
    # Movement section
    # --------------------------------------------------------

    "movement_analysis": {

        "players_analysed":
            players_analysed,

        "total_players_detected":
            total_players_detected,

        "top_distance_player":
            top_distance_player,

        "top_maximum_speed_player":
            top_speed_player,

        "top_average_speed_player":
            top_average_speed_player
    },

    # --------------------------------------------------------
    # Top players
    # --------------------------------------------------------

    "top_players": {

        "by_distance":
            players_by_distance[:10],

        "by_maximum_speed":
            players_by_max_speed[:10],

        "by_average_speed":
            players_by_average_speed[:10]
    },

    # --------------------------------------------------------
    # Event section
    # --------------------------------------------------------

    "event_analysis": {

        "total_events":
            total_events,

        "event_counts":
            event_counts,

        "potential_sprint_count":
            len(potential_sprints),

        "high_speed_event_count":
            len(high_speed_events),

        "low_movement_event_count":
            len(low_movement_events),

        "tracking_warning_count":
            len(tracking_warnings),

        "potential_sprints":
            potential_sprints,

        "high_speed_events":
            high_speed_events,

        "low_movement_events":
            low_movement_events,

        "tracking_warnings":
            tracking_warnings
    },

    # --------------------------------------------------------
    # Camera section
    # --------------------------------------------------------

    "camera_analysis": {

        "average_translation_pixels":
            average_translation,

        "maximum_translation_pixels":
            maximum_translation,

        "average_rotation_degrees":
            average_rotation,

        "maximum_rotation_degrees":
            maximum_rotation,

        "stable_frames":
            stable_frames,

        "moving_frames":
            moving_frames,

        "motion_counts":
            motion_counts
    },

    # --------------------------------------------------------
    # Calibration section
    # --------------------------------------------------------

    "calibration_analysis": {

        "homography_frames":
            homography_frames,

        "camera_motion_frames":
            camera_motion_frames,

        "total_player_positions":
            total_player_positions,

        "reliable_camera_matches":
            reliable_matches,

        "unreliable_camera_matches":
            unreliable_matches,

        "reliability_percent":
            round(
                calibration_reliability,
                2
            )
    },

    # --------------------------------------------------------
    # Individual players
    # --------------------------------------------------------

    "player_reports":
        player_reports
}


# ============================================================
# SAVE REPORT
# ============================================================

os.makedirs(
    "results",
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w"
) as file:

    json.dump(
        report,
        file,
        indent=2
    )


# ============================================================
# CONSOLE REPORT
# ============================================================

print("\n" + "=" * 70)
print("SPORTFLASH MATCH REPORT")
print("=" * 70)


print("\nTEAM ANALYSIS")
print("-" * 70)

print(
    f"Classified players: "
    f"{total_team_players}"
)

print(
    f"Team A players: "
    f"{team_a_count}"
)

print(
    f"Team B players: "
    f"{team_b_count}"
)


print("\nMOVEMENT ANALYSIS")
print("-" * 70)

print(
    f"Players analysed: "
    f"{players_analysed}"
)

if top_distance_player:

    print(
        f"Highest estimated distance: "
        f"Player "
        f"{top_distance_player.get('player_id')} "
        f"({top_distance_player.get('total_distance_m', 0):.2f} m)"
    )

if top_speed_player:

    print(
        f"Highest estimated maximum speed: "
        f"Player "
        f"{top_speed_player.get('player_id')} "
        f"({top_speed_player.get('maximum_speed_kmh', 0):.2f} km/h)"
    )

if top_average_speed_player:

    print(
        f"Highest estimated average speed: "
        f"Player "
        f"{top_average_speed_player.get('player_id')} "
        f"({top_average_speed_player.get('average_speed_kmh', 0):.2f} km/h)"
    )


print("\nEVENT ANALYSIS")
print("-" * 70)

print(
    f"Total potential events: "
    f"{total_events}"
)

print(
    f"Potential sprints: "
    f"{len(potential_sprints)}"
)

print(
    f"Potential high-speed events: "
    f"{len(high_speed_events)}"
)

print(
    f"Low movement periods: "
    f"{len(low_movement_events)}"
)

print(
    f"Tracking warnings: "
    f"{len(tracking_warnings)}"
)


print("\nCAMERA ANALYSIS")
print("-" * 70)

print(
    f"Average camera movement: "
    f"{average_translation:.2f} pixels"
)

print(
    f"Maximum camera movement: "
    f"{maximum_translation:.2f} pixels"
)

print(
    f"Average rotation: "
    f"{average_rotation:.4f} degrees"
)

print(
    f"Maximum rotation: "
    f"{maximum_rotation:.4f} degrees"
)


print("\nCALIBRATION ANALYSIS")
print("-" * 70)

print(
    f"Homography frames: "
    f"{homography_frames}"
)

print(
    f"Camera motion frames: "
    f"{camera_motion_frames}"
)

print(
    f"Player positions: "
    f"{total_player_positions}"
)

print(
    f"Reliable matches: "
    f"{reliable_matches}"
)

print(
    f"Unreliable matches: "
    f"{unreliable_matches}"
)

print(
    f"Calibration reliability: "
    f"{calibration_reliability:.2f}%"
)


print("\n" + "=" * 70)
print("MATCH REPORT GENERATED SUCCESSFULLY")
print("=" * 70)

print(
    f"\nOutput file: [OK] {OUTPUT_FILE}"
)

print(
    "\nIMPORTANT:"
)

print(
    "Distance, speed and movement events are "
    "potential/estimated analytics."
)