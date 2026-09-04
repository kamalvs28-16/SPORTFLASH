import json
import os

print("======================================")
print(" SPORTFLASH TEAM ANALYSIS")
print("======================================")

# ============================================================
# FILE PATHS
# ============================================================

RESULTS_DIR = "results"

performance_file = os.path.join(
    RESULTS_DIR,
    "performance_scores.json"
)

movement_file = os.path.join(
    RESULTS_DIR,
    "movement_results.json"
)

speed_file = os.path.join(
    RESULTS_DIR,
    "speed_results.json"
)

zone_file = os.path.join(
    RESULTS_DIR,
    "zone_results.json"
)

ball_file = os.path.join(
    RESULTS_DIR,
    "ball_results.json"
)

# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    if not os.path.exists(file_path):

        print(
            f"WARNING: File not found -> {file_path}"
        )

        return {}

    try:

        with open(
            file_path,
            "r"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"Error reading {file_path}: {error}"
        )

        return {}


performance_data = load_json(
    performance_file
)

movement_data = load_json(
    movement_file
)

speed_data = load_json(
    speed_file
)

zone_data = load_json(
    zone_file
)

ball_data = load_json(
    ball_file
)

# ============================================================
# CHECK DATA
# ============================================================

if not performance_data:

    print(
        "\nERROR: performance_scores.json is empty or missing."
    )

    print(
        "Run performance_score.py first."
    )

    exit()

# ============================================================
# PLAYER IDS
# ============================================================

player_ids = set()

player_ids.update(
    performance_data.keys()
)

player_ids.update(
    movement_data.keys()
)

player_ids.update(
    speed_data.keys()
)

player_ids.update(
    zone_data.keys()
)

player_ids = sorted(
    player_ids,
    key=lambda x: int(x)
)

print(
    f"\nPlayers found: {len(player_ids)}"
)

# ============================================================
# TEAM DATA
# ============================================================

team_players = []

# ============================================================
# BUILD PLAYER DATA
# ============================================================

for player_id in player_ids:

    performance = performance_data.get(
        player_id,
        {}
    )

    movement = movement_data.get(
        player_id,
        0
    )

    speed = speed_data.get(
        player_id,
        {}
    )

    zone = zone_data.get(
        player_id,
        {}
    )

    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    if isinstance(
        movement,
        dict
    ):

        movement_value = movement.get(
            "total_distance",
            movement.get(
                "movement",
                0
            )
        )

    else:

        movement_value = movement

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    performance_score = performance.get(
        "performance_score",
        0
    )

    # --------------------------------------------------------
    # SPEED
    # --------------------------------------------------------

    average_speed = speed.get(
        "average_speed",
        0
    )

    maximum_speed = speed.get(
        "maximum_speed",
        0
    )

    # --------------------------------------------------------
    # ZONES
    # --------------------------------------------------------

    defensive = zone.get(
        "defensive",
        0
    )

    midfield = zone.get(
        "midfield",
        0
    )

    attacking = zone.get(
        "attacking",
        0
    )

    # --------------------------------------------------------
    # BALL INTERACTIONS
    # --------------------------------------------------------

    interaction_counts = ball_data.get(
        "interaction_counts",
        {}
    )

    ball_interactions = interaction_counts.get(
        player_id,
        0
    )

    # --------------------------------------------------------
    # PLAYER RECORD
    # --------------------------------------------------------

    player_record = {

        "player_id": player_id,

        "performance_score": round(
            performance_score,
            2
        ),

        "movement": round(
            movement_value,
            2
        ),

        "average_speed": round(
            average_speed,
            2
        ),

        "maximum_speed": round(
            maximum_speed,
            2
        ),

        "defensive_percentage": round(
            defensive,
            2
        ),

        "midfield_percentage": round(
            midfield,
            2
        ),

        "attacking_percentage": round(
            attacking,
            2
        ),

        "ball_interactions": ball_interactions
    }

    team_players.append(
        player_record
    )

# ============================================================
# HELPER FUNCTION
# ============================================================

def get_best_player(
    players,
    metric
):

    if not players:

        return None

    return max(
        players,
        key=lambda player: player.get(
            metric,
            0
        )
    )

# ============================================================
# TEAM AVERAGES
# ============================================================

number_of_players = len(
    team_players
)

if number_of_players > 0:

    average_performance = sum(
        player["performance_score"]
        for player in team_players
    ) / number_of_players

    average_movement = sum(
        player["movement"]
        for player in team_players
    ) / number_of_players

    average_speed = sum(
        player["average_speed"]
        for player in team_players
    ) / number_of_players

    average_max_speed = sum(
        player["maximum_speed"]
        for player in team_players
    ) / number_of_players

    average_defensive = sum(
        player["defensive_percentage"]
        for player in team_players
    ) / number_of_players

    average_midfield = sum(
        player["midfield_percentage"]
        for player in team_players
    ) / number_of_players

    average_attacking = sum(
        player["attacking_percentage"]
        for player in team_players
    ) / number_of_players

    total_ball_interactions = sum(
        player["ball_interactions"]
        for player in team_players
    )

else:

    average_performance = 0
    average_movement = 0
    average_speed = 0
    average_max_speed = 0
    average_defensive = 0
    average_midfield = 0
    average_attacking = 0
    total_ball_interactions = 0

# ============================================================
# BEST PLAYERS
# ============================================================

best_performer = get_best_player(
    team_players,
    "performance_score"
)

most_active_player = get_best_player(
    team_players,
    "movement"
)

fastest_player = get_best_player(
    team_players,
    "average_speed"
)

highest_max_speed_player = get_best_player(
    team_players,
    "maximum_speed"
)

best_defensive_player = get_best_player(
    team_players,
    "defensive_percentage"
)

best_midfield_player = get_best_player(
    team_players,
    "midfield_percentage"
)

best_attacking_player = get_best_player(
    team_players,
    "attacking_percentage"
)

most_ball_involved_player = get_best_player(
    team_players,
    "ball_interactions"
)

# ============================================================
# TEAM DOMINANT ZONE
# ============================================================

team_zones = {

    "defensive": average_defensive,

    "midfield": average_midfield,

    "attacking": average_attacking

}

team_dominant_zone = max(
    team_zones,
    key=team_zones.get
)

# ============================================================
# TEAM PERFORMANCE LEVEL
# ============================================================

if average_performance >= 80:

    team_performance_level = "Excellent"

elif average_performance >= 60:

    team_performance_level = "Good"

elif average_performance >= 40:

    team_performance_level = "Average"

else:

    team_performance_level = "Needs Improvement"

# ============================================================
# TEAM STRENGTHS
# ============================================================

strengths = []

if average_performance >= 60:

    strengths.append(
        "Overall player performance is strong."
    )

if average_movement >= 2000:

    strengths.append(
        "The team demonstrates strong movement activity."
    )

if average_speed >= 200:

    strengths.append(
        "The team demonstrates good average movement speed."
    )

if average_attacking >= 30:

    strengths.append(
        "The team shows strong attacking-zone involvement."
    )

if average_midfield >= 35:

    strengths.append(
        "The team shows strong midfield involvement."
    )

if average_defensive >= 35:

    strengths.append(
        "The team shows strong defensive-zone involvement."
    )

if total_ball_interactions >= 10:

    strengths.append(
        "The team shows good involvement in ball situations."
    )

if not strengths:

    strengths.append(
        "The team has opportunities to improve overall activity and consistency."
    )

# ============================================================
# TEAM WEAKNESSES
# ============================================================

weaknesses = []

if average_performance < 40:

    weaknesses.append(
        "Overall team performance requires improvement."
    )

if average_movement < 1500:

    weaknesses.append(
        "Team movement activity is relatively low."
    )

if average_speed < 150:

    weaknesses.append(
        "Average team movement speed is relatively low."
    )

if average_attacking < 20:

    weaknesses.append(
        "Attacking-zone involvement could be improved."
    )

if average_defensive < 20:

    weaknesses.append(
        "Defensive-zone involvement could be improved."
    )

if total_ball_interactions < 5:

    weaknesses.append(
        "Ball involvement is relatively low."
    )

if not weaknesses:

    weaknesses.append(
        "No major weakness detected from the current metrics."
    )

# ============================================================
# TEAM SUMMARY
# ============================================================

team_summary = {

    "number_of_players": number_of_players,

    "average_performance_score": round(
        average_performance,
        2
    ),

    "team_performance_level":
        team_performance_level,

    "average_movement": round(
        average_movement,
        2
    ),

    "average_speed": round(
        average_speed,
        2
    ),

    "average_maximum_speed": round(
        average_max_speed,
        2
    ),

    "zone_distribution": {

        "defensive": round(
            average_defensive,
            2
        ),

        "midfield": round(
            average_midfield,
            2
        ),

        "attacking": round(
            average_attacking,
            2
        )
    },

    "dominant_zone":
        team_dominant_zone,

    "total_ball_interactions":
        total_ball_interactions,

    "best_performer":
        best_performer,

    "most_active_player":
        most_active_player,

    "fastest_player":
        fastest_player,

    "highest_max_speed_player":
        highest_max_speed_player,

    "best_defensive_player":
        best_defensive_player,

    "best_midfield_player":
        best_midfield_player,

    "best_attacking_player":
        best_attacking_player,

    "most_ball_involved_player":
        most_ball_involved_player,

    "team_strengths":
        strengths,

    "team_weaknesses":
        weaknesses,

    "player_data":
        team_players
}

# ============================================================
# SAVE TEAM ANALYSIS
# ============================================================

output_file = os.path.join(
    RESULTS_DIR,
    "team_analysis.json"
)

with open(
    output_file,
    "w"
) as file:

    json.dump(
        team_summary,
        file,
        indent=4
    )

# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n======================================")
print(" TEAM PERFORMANCE SUMMARY")
print("======================================")

print(
    f"Number of Players : "
    f"{number_of_players}"
)

print(
    f"Average Performance : "
    f"{average_performance:.2f}/100"
)

print(
    f"Team Performance Level : "
    f"{team_performance_level}"
)

print(
    f"Average Movement : "
    f"{average_movement:.2f} pixels"
)

print(
    f"Average Speed : "
    f"{average_speed:.2f} pixels/sec"
)

print(
    f"Average Maximum Speed : "
    f"{average_max_speed:.2f} pixels/sec"
)

print(
    f"Dominant Zone : "
    f"{team_dominant_zone}"
)

print(
    f"Total Ball Interactions : "
    f"{total_ball_interactions}"
)

# ============================================================
# BEST PLAYERS
# ============================================================

print("\n======================================")
print(" TOP TEAM PERFORMERS")
print("======================================")

if best_performer:

    print(
        f"Best Performer : "
        f"Player {best_performer['player_id']} "
        f"({best_performer['performance_score']:.2f})"
    )

if most_active_player:

    print(
        f"Most Active : "
        f"Player {most_active_player['player_id']} "
        f"({most_active_player['movement']:.2f} pixels)"
    )

if fastest_player:

    print(
        f"Fastest Average Speed : "
        f"Player {fastest_player['player_id']} "
        f"({fastest_player['average_speed']:.2f} px/s)"
    )

if best_attacking_player:

    print(
        f"Best Attacking : "
        f"Player {best_attacking_player['player_id']} "
        f"({best_attacking_player['attacking_percentage']:.2f}%)"
    )

if best_defensive_player:

    print(
        f"Best Defensive : "
        f"Player {best_defensive_player['player_id']} "
        f"({best_defensive_player['defensive_percentage']:.2f}%)"
    )

if most_ball_involved_player:

    print(
        f"Most Ball Involved : "
        f"Player {most_ball_involved_player['player_id']} "
        f"({most_ball_involved_player['ball_interactions']} interactions)"
    )

# ============================================================
# STRENGTHS
# ============================================================

print("\n======================================")
print(" TEAM STRENGTHS")
print("======================================")

for strength in strengths:

    print(
        f"✓ {strength}"
    )

# ============================================================
# WEAKNESSES
# ============================================================

print("\n======================================")
print(" TEAM WEAKNESSES")
print("======================================")

for weakness in weaknesses:

    print(
        f"• {weakness}"
    )

# ============================================================
# COMPLETED
# ============================================================

print("\n======================================")
print(" TEAM ANALYSIS COMPLETED")
print("======================================")

print(
    f"\nResults saved to:\n{output_file}"
)