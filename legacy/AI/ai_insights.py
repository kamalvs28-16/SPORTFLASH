import json
import os

print("======================================")
print(" SPORTFLASH AI PERFORMANCE INSIGHTS")
print("======================================")

# ------------------------------------------------
# FILE PATHS
# ------------------------------------------------

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

# ------------------------------------------------
# LOAD JSON FILE
# ------------------------------------------------

def load_json(file_path):

    if not os.path.exists(file_path):
        print(f"WARNING: File not found -> {file_path}")
        return {}

    with open(file_path, "r") as file:
        return json.load(file)


performance_data = load_json(performance_file)
movement_data = load_json(movement_file)
speed_data = load_json(speed_file)
zone_data = load_json(zone_file)
ball_data = load_json(ball_file)

print("\nAll available analysis files loaded.")

# ------------------------------------------------
# GET PLAYER IDS
# ------------------------------------------------

player_ids = set()

player_ids.update(performance_data.keys())
player_ids.update(movement_data.keys())
player_ids.update(speed_data.keys())
player_ids.update(zone_data.keys())

player_ids = sorted(
    player_ids,
    key=lambda x: int(x)
)

# ------------------------------------------------
# AI INSIGHT FUNCTION
# ------------------------------------------------

def generate_insight(
    player_id,
    performance,
    movement,
    speed,
    zone,
    interactions
):

    score = performance.get(
        "performance_score",
        0
    )

    movement_value = movement

    average_speed = speed.get(
        "average_speed",
        0
    )

    maximum_speed = speed.get(
        "maximum_speed",
        0
    )

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

    # --------------------------------------------
    # PERFORMANCE LEVEL
    # --------------------------------------------

    if score >= 80:

        performance_level = "Excellent"

    elif score >= 60:

        performance_level = "Good"

    elif score >= 40:

        performance_level = "Average"

    else:

        performance_level = "Needs Improvement"

    # --------------------------------------------
    # MOVEMENT ANALYSIS
    # --------------------------------------------

    if movement_value > 3000:

        movement_insight = (
            "The player shows high movement activity "
            "throughout the match."
        )

    elif movement_value > 1500:

        movement_insight = (
            "The player shows moderate movement "
            "activity."
        )

    else:

        movement_insight = (
            "The player shows relatively low movement "
            "activity."
        )

    # --------------------------------------------
    # SPEED ANALYSIS
    # --------------------------------------------

    if average_speed > 300:

        speed_insight = (
            "The player demonstrates strong average "
            "movement speed."
        )

    elif average_speed > 150:

        speed_insight = (
            "The player's average movement speed "
            "is moderate."
        )

    else:

        speed_insight = (
            "The player's average movement speed "
            "is relatively low."
        )

    # --------------------------------------------
    # FIELD POSITION ANALYSIS
    # --------------------------------------------

    zone_values = {
        "defensive": defensive,
        "midfield": midfield,
        "attacking": attacking
    }

    dominant_zone = max(
        zone_values,
        key=zone_values.get
    )

    if dominant_zone == "defensive":

        zone_insight = (
            "The player spent most of the tracked "
            "time in the defensive zone."
        )

    elif dominant_zone == "midfield":

        zone_insight = (
            "The player spent most of the tracked "
            "time in the midfield zone."
        )

    else:

        zone_insight = (
            "The player spent most of the tracked "
            "time in the attacking zone."
        )

    # --------------------------------------------
    # BALL INTERACTION ANALYSIS
    # --------------------------------------------

    if interactions >= 10:

        ball_insight = (
            "The player was frequently involved in "
            "player-ball interactions."
        )

    elif interactions >= 5:

        ball_insight = (
            "The player had a moderate number of "
            "ball interactions."
        )

    elif interactions > 0:

        ball_insight = (
            "The player had limited ball interactions."
        )

    else:

        ball_insight = (
            "No significant player-ball interactions "
            "were detected."
        )

    # --------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------

    recommendations = []

    if movement_value < 1500:

        recommendations.append(
            "Increase movement and off-ball activity."
        )

    if average_speed < 150:

        recommendations.append(
            "Improve acceleration and movement speed."
        )

    if attacking < 20:

        recommendations.append(
            "Increase attacking-zone involvement."
        )

    if defensive < 20:

        recommendations.append(
            "Improve defensive positioning."
        )

    if interactions < 5:

        recommendations.append(
            "Increase involvement in ball situations."
        )

    if not recommendations:

        recommendations.append(
            "Maintain current performance and "
            "continue improving consistency."
        )

    # --------------------------------------------
    # FINAL INSIGHT
    # --------------------------------------------

    insight = {

        "player_id": player_id,

        "performance_level": performance_level,

        "performance_score": round(
            score,
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

        "dominant_zone": dominant_zone,

        "ball_interactions": interactions,

        "analysis": {

            "movement": movement_insight,

            "speed": speed_insight,

            "zone": zone_insight,

            "ball": ball_insight

        },

        "recommendations": recommendations
    }

    return insight


# ------------------------------------------------
# GENERATE INSIGHTS FOR ALL PLAYERS
# ------------------------------------------------

all_insights = {}

for player_id in player_ids:

    performance = performance_data.get(
        player_id,
        {}
    )

    movement_info = movement_data.get(
        player_id,
        0
    )

    speed_info = speed_data.get(
        player_id,
        {}
    )

    zone_info = zone_data.get(
        player_id,
        {}
    )

    # Movement JSON may contain either
    # a number or a dictionary

    if isinstance(
        movement_info,
        dict
    ):

        movement_value = movement_info.get(
            "total_distance",
            movement_info.get(
                "movement",
                0
            )
        )

    else:

        movement_value = movement_info

    # --------------------------------------------
    # BALL INTERACTION COUNT
    # --------------------------------------------

    interaction_counts = ball_data.get(
        "interaction_counts",
        {}
    )

    interactions = interaction_counts.get(
        player_id,
        0
    )

    # --------------------------------------------
    # GENERATE INSIGHT
    # --------------------------------------------

    insight = generate_insight(

        player_id,

        performance,

        movement_value,

        speed_info,

        zone_info,

        interactions
    )

    all_insights[player_id] = insight


# ------------------------------------------------
# SAVE RESULTS
# ------------------------------------------------

output_file = os.path.join(
    RESULTS_DIR,
    "ai_insights.json"
)

with open(
    output_file,
    "w"
) as file:

    json.dump(
        all_insights,
        file,
        indent=4
    )


# ------------------------------------------------
# DISPLAY RESULTS
# ------------------------------------------------

print("\n======================================")
print(" AI PERFORMANCE INSIGHTS")
print("======================================")

for player_id, insight in all_insights.items():

    print(
        f"\nPlayer {player_id}"
    )

    print(
        f"Performance Score : "
        f"{insight['performance_score']}/100"
    )

    print(
        f"Performance Level : "
        f"{insight['performance_level']}"
    )

    print(
        f"Dominant Zone : "
        f"{insight['dominant_zone']}"
    )

    print(
        f"Ball Interactions : "
        f"{insight['ball_interactions']}"
    )

    print("\nAnalysis:")

    print(
        "-",
        insight["analysis"]["movement"]
    )

    print(
        "-",
        insight["analysis"]["speed"]
    )

    print(
        "-",
        insight["analysis"]["zone"]
    )

    print(
        "-",
        insight["analysis"]["ball"]
    )

    print("\nRecommendations:")

    for recommendation in insight[
        "recommendations"
    ]:

        print(
            "-",
            recommendation
        )


print("\n======================================")
print(" AI INSIGHTS COMPLETED")
print("======================================")

print(
    f"\nResults saved to:\n{output_file}"
)