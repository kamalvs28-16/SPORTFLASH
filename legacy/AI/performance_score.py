import json
import os

print("======================================")
print(" SPORTFLASH PERFORMANCE SCORE")
print("======================================")

# --------------------------------------
# Load movement results
# --------------------------------------

movement_file = "results/movement_results.json"

if not os.path.exists(movement_file):
    print("ERROR: movement_results.json not found!")
    exit()

with open(movement_file, "r") as file:
    movement_data = json.load(file)

print("Movement data loaded successfully.")


# --------------------------------------
# Load speed results
# --------------------------------------

speed_file = "results/speed_results.json"

if not os.path.exists(speed_file):
    print("ERROR: speed_results.json not found!")
    exit()

with open(speed_file, "r") as file:
    speed_data = json.load(file)

print("Speed data loaded successfully.")


# --------------------------------------
# Find players available in both files
# --------------------------------------

players = set(movement_data.keys()) & set(speed_data.keys())

if not players:
    print("ERROR: No common players found!")
    exit()

print(f"Players available for scoring: {len(players)}")


# --------------------------------------
# Find maximum values
# --------------------------------------

max_movement = max(
    movement_data[player]
    for player in players
)

max_average_speed = max(
    speed_data[player]["average_speed"]
    for player in players
)

max_maximum_speed = max(
    speed_data[player]["maximum_speed"]
    for player in players
)


# --------------------------------------
# Calculate performance score
# --------------------------------------

performance_results = {}

for player in players:

    movement = movement_data[player]

    average_speed = speed_data[player]["average_speed"]

    maximum_speed = speed_data[player]["maximum_speed"]


    # Normalize movement to 0-100
    movement_score = (
        movement / max_movement
    ) * 100


    # Normalize average speed to 0-100
    average_speed_score = (
        average_speed / max_average_speed
    ) * 100


    # Normalize maximum speed to 0-100
    maximum_speed_score = (
        maximum_speed / max_maximum_speed
    ) * 100


    # ----------------------------------
    # Weighted final score
    # ----------------------------------

    final_score = (
        movement_score * 0.40
        + average_speed_score * 0.35
        + maximum_speed_score * 0.25
    )


    performance_results[player] = {

        "movement": round(
            movement,
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

        "movement_score": round(
            movement_score,
            2
        ),

        "average_speed_score": round(
            average_speed_score,
            2
        ),

        "maximum_speed_score": round(
            maximum_speed_score,
            2
        ),

        "performance_score": round(
            final_score,
            2
        )
    }


# --------------------------------------
# Display results
# --------------------------------------

print("\n======================================")
print(" PLAYER PERFORMANCE RESULTS")
print("======================================")


sorted_players = sorted(
    performance_results.items(),
    key=lambda x: x[1]["performance_score"],
    reverse=True
)


for player, data in sorted_players:

    print(f"\nPlayer {player}")

    print(
        f"Movement: "
        f"{data['movement']:.2f} pixels"
    )

    print(
        f"Average Speed: "
        f"{data['average_speed']:.2f} pixels/sec"
    )

    print(
        f"Maximum Speed: "
        f"{data['maximum_speed']:.2f} pixels/sec"
    )

    print(
        f"Performance Score: "
        f"{data['performance_score']:.2f}/100"
    )


# --------------------------------------
# Save performance results
# --------------------------------------

os.makedirs(
    "results",
    exist_ok=True
)

output_file = (
    "results/performance_scores.json"
)

with open(
    output_file,
    "w"
) as file:

    json.dump(
        performance_results,
        file,
        indent=4
    )


print("\n======================================")
print(" PERFORMANCE ANALYSIS COMPLETED")
print("======================================")

print(
    "Results saved to:"
)

print(
    "results/performance_scores.json"
)

print("======================================")