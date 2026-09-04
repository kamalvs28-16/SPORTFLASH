import json
import os

print("======================================")
print(" SPORTFLASH NUTRITION RECOMMENDATION")
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

ai_insights_file = os.path.join(
    RESULTS_DIR,
    "ai_insights.json"
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

ai_insights_data = load_json(
    ai_insights_file
)

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

# ============================================================
# NUTRITION RECOMMENDATION FUNCTION
# ============================================================

def generate_nutrition_recommendation(
    player_id,
    performance,
    movement,
    speed,
    zone
):

    recommendations = []

    meal_suggestions = []

    hydration = []

    recovery = []

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    performance_score = performance.get(
        "performance_score",
        0
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

    # ========================================================
    # ACTIVITY LEVEL
    # ========================================================

    if (
        movement_value >= 3000
        or average_speed >= 300
    ):

        activity_level = "High"

    elif (
        movement_value >= 1500
        or average_speed >= 150
    ):

        activity_level = "Moderate"

    else:

        activity_level = "Low"

    # ========================================================
    # CARBOHYDRATE RECOMMENDATION
    # ========================================================

    if activity_level == "High":

        recommendations.append(
            "Prioritize carbohydrate-rich foods "
            "to support high-intensity activity."
        )

        meal_suggestions.extend([
            "Oats",
            "Rice",
            "Whole-grain bread",
            "Bananas",
            "Potatoes"
        ])

    elif activity_level == "Moderate":

        recommendations.append(
            "Maintain a balanced carbohydrate intake "
            "to support training and match activity."
        )

        meal_suggestions.extend([
            "Oats",
            "Rice",
            "Whole-grain bread",
            "Fruits"
        ])

    else:

        recommendations.append(
            "Maintain balanced meals with appropriate "
            "carbohydrate portions for activity level."
        )

        meal_suggestions.extend([
            "Whole grains",
            "Fruits",
            "Vegetables"
        ])

    # ========================================================
    # PROTEIN / RECOVERY
    # ========================================================

    if (
        activity_level == "High"
        or performance_score >= 70
    ):

        recommendations.append(
            "Include a protein-rich meal or snack "
            "after training to support recovery."
        )

        recovery.extend([
            "Eggs",
            "Milk or yogurt",
            "Fish",
            "Chicken",
            "Beans or lentils"
        ])

    else:

        recommendations.append(
            "Maintain regular balanced meals containing "
            "a source of protein."
        )

        recovery.extend([
            "Eggs",
            "Milk or yogurt",
            "Beans",
            "Lentils"
        ])

    # ========================================================
    # HYDRATION
    # ========================================================

    if activity_level == "High":

        recommendations.append(
            "Pay particular attention to hydration "
            "before, during and after activity."
        )

        hydration.extend([
            "Water",
            "Fluids during prolonged activity",
            "Electrolyte-containing fluids when appropriate"
        ])

    else:

        recommendations.append(
            "Maintain regular hydration throughout "
            "the day and around training."
        )

        hydration.extend([
            "Water",
            "Hydrating foods such as fruits"
        ])

    # ========================================================
    # FIELD POSITION
    # ========================================================

    zones = {
        "defensive": defensive,
        "midfield": midfield,
        "attacking": attacking
    }

    dominant_zone = max(
        zones,
        key=zones.get
    )

    if dominant_zone == "attacking":

        position_note = (
            "The player shows relatively high attacking-zone "
            "involvement. A balanced pre- and post-training "
            "meal can support repeated high-intensity actions."
        )

    elif dominant_zone == "midfield":

        position_note = (
            "The player shows strong midfield involvement. "
            "Balanced carbohydrate, protein and hydration "
            "strategies can support repeated activity."
        )

    else:

        position_note = (
            "The player shows strong defensive-zone involvement. "
            "Maintain balanced meals and hydration around training."
        )

    # ========================================================
    # PERFORMANCE LEVEL
    # ========================================================

    if performance_score >= 80:

        performance_level = "Excellent"

    elif performance_score >= 60:

        performance_level = "Good"

    elif performance_score >= 40:

        performance_level = "Average"

    else:

        performance_level = "Needs Improvement"

    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {

        "player_id": player_id,

        "performance_score": round(
            performance_score,
            2
        ),

        "performance_level": performance_level,

        "activity_level": activity_level,

        "dominant_zone": dominant_zone,

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

        "recommendations": recommendations,

        "food_suggestions": meal_suggestions,

        "recovery_foods": recovery,

        "hydration": hydration,

        "position_note": position_note
    }

    return result


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

nutrition_results = {}

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

    result = generate_nutrition_recommendation(
        player_id,
        performance,
        movement,
        speed,
        zone
    )

    nutrition_results[player_id] = result


# ============================================================
# SAVE JSON
# ============================================================

output_file = os.path.join(
    RESULTS_DIR,
    "nutrition_recommendations.json"
)

with open(
    output_file,
    "w"
) as file:

    json.dump(
        nutrition_results,
        file,
        indent=4
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n======================================")
print(" NUTRITION RECOMMENDATIONS")
print("======================================")

for player_id, result in nutrition_results.items():

    print(
        f"\nPlayer {player_id}"
    )

    print(
        f"Performance Level : "
        f"{result['performance_level']}"
    )

    print(
        f"Activity Level : "
        f"{result['activity_level']}"
    )

    print(
        f"Dominant Zone : "
        f"{result['dominant_zone']}"
    )

    print("\nRecommendations:")

    for recommendation in result[
        "recommendations"
    ]:

        print(
            "-",
            recommendation
        )

    print("\nFood Suggestions:")

    print(
        ", ".join(
            result["food_suggestions"]
        )
    )

    print("\nRecovery Foods:")

    print(
        ", ".join(
            result["recovery_foods"]
        )
    )

    print("\nHydration:")

    print(
        ", ".join(
            result["hydration"]
        )
    )


print("\n======================================")
print(" NUTRITION ANALYSIS COMPLETED")
print("======================================")

print(
    f"\nResults saved to:\n{output_file}"
)