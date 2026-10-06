import json
import os


# ============================================================
# SPORTFLASH - PLAYER COMPARISON
# ============================================================

print("=" * 60)
print("        SPORTFLASH PLAYER COMPARISON")
print("=" * 60)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = r"E:\SPORTFLASH"

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

PERFORMANCE_FILE = os.path.join(
    RESULTS_DIR,
    "performance_scores.json"
)

MOVEMENT_FILE = os.path.join(
    RESULTS_DIR,
    "movement_results.json"
)

SPEED_FILE = os.path.join(
    RESULTS_DIR,
    "speed_results.json"
)

ZONE_FILE = os.path.join(
    RESULTS_DIR,
    "zone_results.json"
)

BALL_FILE = os.path.join(
    RESULTS_DIR,
    "ball_results.json"
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "player_comparison.json"
)


# ============================================================
# LOAD JSON FUNCTION
# ============================================================

def load_json(file_path):

    if not os.path.exists(file_path):

        print(
            f"WARNING: File not found: {file_path}"
        )

        return {}

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"ERROR reading {file_path}:"
        )

        print(error)

        return {}


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading analysis data...")

performance_data = load_json(
    PERFORMANCE_FILE
)

movement_data = load_json(
    MOVEMENT_FILE
)

speed_data = load_json(
    SPEED_FILE
)

zone_data = load_json(
    ZONE_FILE
)

ball_data = load_json(
    BALL_FILE
)


print("Data loading completed.")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_performance_score(player_id):

    data = performance_data.get(
        str(player_id),
        {}
    )

    if isinstance(data, dict):

        return float(
            data.get(
                "performance_score",
                data.get("score", 0)
            )
        )

    if isinstance(data, (int, float)):

        return float(data)

    return 0.0


def get_movement(player_id):

    data = movement_data.get(
        str(player_id),
        0
    )

    if isinstance(data, dict):

        return float(
            data.get(
                "total_movement",
                data.get(
                    "movement",
                    data.get(
                        "distance",
                        0
                    )
                )
            )
        )

    if isinstance(data, (int, float)):

        return float(data)

    return 0.0


def get_speed(player_id):

    data = speed_data.get(
        str(player_id),
        {}
    )

    if not isinstance(data, dict):

        return 0.0, 0.0

    average_speed = float(
        data.get(
            "average_speed",
            0
        )
    )

    maximum_speed = float(
        data.get(
            "maximum_speed",
            0
        )
    )

    return average_speed, maximum_speed


def get_zone_data(player_id):

    data = zone_data.get(
        str(player_id),
        {}
    )

    if not isinstance(data, dict):

        return {
            "defensive": 0.0,
            "midfield": 0.0,
            "attacking": 0.0
        }

    return {
        "defensive": float(
            data.get(
                "defensive",
                0
            )
        ),

        "midfield": float(
            data.get(
                "midfield",
                0
            )
        ),

        "attacking": float(
            data.get(
                "attacking",
                0
            )
        )
    }


def get_ball_interactions(player_id):

    interaction_data = ball_data.get(
        "interaction_counts",
        {}
    )

    if not isinstance(
        interaction_data,
        dict
    ):

        return 0

    value = interaction_data.get(
        str(player_id),
        0
    )

    try:

        return int(value)

    except:

        return 0


# ============================================================
# FIND COMMON PLAYERS
# ============================================================

player_ids = set()

player_ids.update(
    str(player_id)
    for player_id in performance_data.keys()
)

player_ids.update(
    str(player_id)
    for player_id in movement_data.keys()
)

player_ids.update(
    str(player_id)
    for player_id in speed_data.keys()
)

player_ids.update(
    str(player_id)
    for player_id in zone_data.keys()
)


if not player_ids:

    print(
        "\nERROR: No players found."
    )

    print(
        "Make sure your analysis JSON files contain data."
    )

    exit()


# ============================================================
# CREATE PLAYER PROFILES
# ============================================================

players = {}


for player_id in sorted(
    player_ids,
    key=lambda x: int(x)
    if x.isdigit()
    else 999999
):

    average_speed, maximum_speed = (
        get_speed(player_id)
    )

    zones = get_zone_data(
        player_id
    )

    players[player_id] = {

        "player_id":
            player_id,

        "performance_score":
            round(
                get_performance_score(
                    player_id
                ),
                2
            ),

        "movement":
            round(
                get_movement(
                    player_id
                ),
                2
            ),

        "average_speed":
            round(
                average_speed,
                2
            ),

        "maximum_speed":
            round(
                maximum_speed,
                2
            ),

        "defensive":
            round(
                zones["defensive"],
                2
            ),

        "midfield":
            round(
                zones["midfield"],
                2
            ),

        "attacking":
            round(
                zones["attacking"],
                2
            ),

        "ball_interactions":
            get_ball_interactions(
                player_id
            )
    }


# ============================================================
# COMPARISON FUNCTION
# ============================================================

def compare_players(
    player_a,
    player_b
):

    a = players[
        str(player_a)
    ]

    b = players[
        str(player_b)
    ]


    # --------------------------------------------------------
    # Determine winners
    # --------------------------------------------------------

    if (
        a["performance_score"]
        > b["performance_score"]
    ):

        overall_winner = str(player_a)

    elif (
        b["performance_score"]
        > a["performance_score"]
    ):

        overall_winner = str(player_b)

    else:

        overall_winner = "Tie"


    if (
        a["average_speed"]
        > b["average_speed"]
    ):

        faster_player = str(player_a)

    elif (
        b["average_speed"]
        > a["average_speed"]
    ):

        faster_player = str(player_b)

    else:

        faster_player = "Tie"


    if (
        a["movement"]
        > b["movement"]
    ):

        more_active_player = str(player_a)

    elif (
        b["movement"]
        > a["movement"]
    ):

        more_active_player = str(player_b)

    else:

        more_active_player = "Tie"


    if (
        a["ball_interactions"]
        > b["ball_interactions"]
    ):

        ball_player = str(player_a)

    elif (
        b["ball_interactions"]
        > a["ball_interactions"]
    ):

        ball_player = str(player_b)

    else:

        ball_player = "Tie"


    if (
        a["attacking"]
        > b["attacking"]
    ):

        attacking_player = str(player_a)

    elif (
        b["attacking"]
        > a["attacking"]
    ):

        attacking_player = str(player_b)

    else:

        attacking_player = "Tie"


    if (
        a["defensive"]
        > b["defensive"]
    ):

        defensive_player = str(player_a)

    elif (
        b["defensive"]
        > a["defensive"]
    ):

        defensive_player = str(player_b)

    else:

        defensive_player = "Tie"


    if (
        a["midfield"]
        > b["midfield"]
    ):

        midfield_player = str(player_a)

    elif (
        b["midfield"]
        > a["midfield"]
    ):

        midfield_player = str(player_b)

    else:

        midfield_player = "Tie"


    # --------------------------------------------------------
    # Return comparison
    # --------------------------------------------------------

    return {

        "player_a":
            a,

        "player_b":
            b,

        "winners": {

            "overall":
                overall_winner,

            "faster":
                faster_player,

            "more_active":
                more_active_player,

            "ball_involvement":
                ball_player,

            "attacking":
                attacking_player,

            "defensive":
                defensive_player,

            "midfield":
                midfield_player
        }
    }


# ============================================================
# CREATE DEFAULT COMPARISON
# ============================================================

sorted_players = sorted(
    players.keys(),
    key=lambda player_id:
        players[player_id][
            "performance_score"
        ],
    reverse=True
)


if len(sorted_players) >= 2:

    default_player_a = (
        sorted_players[0]
    )

    default_player_b = (
        sorted_players[1]
    )

else:

    default_player_a = (
        sorted_players[0]
    )

    default_player_b = (
        sorted_players[0]
    )


comparison = compare_players(
    default_player_a,
    default_player_b
)


# ============================================================
# SAVE RESULT
# ============================================================

output_data = {

    "players": players,

    "default_comparison":
        comparison

}


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output_data,
        file,
        indent=4
    )


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 60)
print("PLAYER COMPARISON RESULTS")
print("=" * 60)


print(
    f"\nPlayer A: "
    f"Player {default_player_a}"
)

print(
    f"Player B: "
    f"Player {default_player_b}"
)


print("\nOverall Winner:")
print(
    comparison[
        "winners"
    ][
        "overall"
    ]
)


print("\nFaster Player:")
print(
    comparison[
        "winners"
    ][
        "faster"
    ]
)


print("\nMore Active Player:")
print(
    comparison[
        "winners"
    ][
        "more_active"
    ]
)


print("\nMore Ball-Involved Player:")
print(
    comparison[
        "winners"
    ][
        "ball_involvement"
    ]
)


print("\nBetter Attacking Presence:")
print(
    comparison[
        "winners"
    ][
        "attacking"
    ]
)


print("\nBetter Defensive Presence:")
print(
    comparison[
        "winners"
    ][
        "defensive"
    ]
)


print("\nBetter Midfield Presence:")
print(
    comparison[
        "winners"
    ][
        "midfield"
    ]
)


print("\n")
print("=" * 60)

print(
    "Comparison data saved to:"
)

print(
    OUTPUT_FILE
)

print("=" * 60)

print(
    "\nSPORTFLASH PLAYER COMPARISON COMPLETED"
)