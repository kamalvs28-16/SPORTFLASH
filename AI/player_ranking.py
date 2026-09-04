import json
import os

print("======================================")
print("     SPORTFLASH PLAYER RANKING")
print("======================================")

# --------------------------------------------------
# 1. Check performance score file
# --------------------------------------------------

performance_file = "results/performance_scores.json"

if not os.path.exists(performance_file):
    print("ERROR: performance_scores.json not found!")
    print("Make sure you have already run performance_score.py")
    exit()

# --------------------------------------------------
# 2. Load performance data
# --------------------------------------------------

with open(performance_file, "r") as file:
    performance_data = json.load(file)

print("Performance data loaded successfully.")

# --------------------------------------------------
# 3. Check whether players exist
# --------------------------------------------------

if not performance_data:
    print("ERROR: No player data found!")
    exit()

print(f"Players found: {len(performance_data)}")

# --------------------------------------------------
# 4. Create ranking
# --------------------------------------------------

ranking = sorted(
    performance_data.items(),
    key=lambda x: x[1]["performance_score"],
    reverse=True
)

# --------------------------------------------------
# 5. Display complete ranking
# --------------------------------------------------

print("\n======================================")
print("       PLAYER PERFORMANCE RANKING")
print("======================================")

print(f"{'Rank':<8}{'Player':<12}{'Score':<10}")
print("--------------------------------------")

for rank, (player_id, data) in enumerate(ranking, start=1):

    score = data["performance_score"]

    print(
        f"{rank:<8}"
        f"Player {player_id:<5}"
        f"{score:.2f}/100"
    )

# --------------------------------------------------
# 6. Display Top 5 players
# --------------------------------------------------

print("\n======================================")
print("             TOP 5 PLAYERS")
print("======================================")

top_players = ranking[:5]

for rank, (player_id, data) in enumerate(top_players, start=1):

    score = data["performance_score"]

    if rank == 1:
        medal = "🥇"
    elif rank == 2:
        medal = "🥈"
    elif rank == 3:
        medal = "🥉"
    else:
        medal = " "

    print(
        f"{medal} Rank {rank}: "
        f"Player {player_id} "
        f"→ {score:.2f}/100"
    )

# --------------------------------------------------
# 7. Find best player
# --------------------------------------------------

best_player, best_data = ranking[0]

print("\n======================================")
print("          BEST PERFORMING PLAYER")
print("======================================")

print(f"Player: {best_player}")
print(f"Performance Score: {best_data['performance_score']:.2f}/100")
print(f"Movement: {best_data['movement']:.2f} pixels")
print(f"Average Speed: {best_data['average_speed']:.2f} pixels/sec")
print(f"Maximum Speed: {best_data['maximum_speed']:.2f} pixels/sec")

# --------------------------------------------------
# 8. Save ranking to JSON
# --------------------------------------------------

ranking_data = []

for rank, (player_id, data) in enumerate(ranking, start=1):

    ranking_data.append({
        "rank": rank,
        "player": player_id,
        "performance_score": data["performance_score"],
        "movement": data["movement"],
        "average_speed": data["average_speed"],
        "maximum_speed": data["maximum_speed"]
    })

output_file = "results/player_ranking.json"

with open(output_file, "w") as file:
    json.dump(ranking_data, file, indent=4)

# --------------------------------------------------
# 9. Completion message
# --------------------------------------------------

print("\n======================================")
print("       PLAYER RANKING COMPLETED")
print("======================================")

print("Ranking saved to:")
print("results/player_ranking.json")

print("======================================")