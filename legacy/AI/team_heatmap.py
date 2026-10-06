import json
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# SPORTFLASH TEAM HEATMAP
# ============================================================

print("=" * 38)
print("SPORTFLASH TEAM HEATMAP")
print("=" * 38)


# ------------------------------------------------------------
# File paths
# ------------------------------------------------------------

TRACKING_FILE = "results/tracking_results.json"
TEAM_FILE = "results/team_classification.json"

TEAM_A_OUTPUT = "results/team_a_heatmap.png"
TEAM_B_OUTPUT = "results/team_b_heatmap.png"
POSITIONS_OUTPUT = "results/team_heatmap_positions.json"


# ------------------------------------------------------------
# Check files
# ------------------------------------------------------------

if not os.path.exists(TRACKING_FILE):
    print(f"ERROR: Tracking file not found: {TRACKING_FILE}")
    exit()

if not os.path.exists(TEAM_FILE):
    print(f"ERROR: Team classification file not found: {TEAM_FILE}")
    exit()


# ------------------------------------------------------------
# Load tracking data
# ------------------------------------------------------------

print("Loading tracking data...")

with open(TRACKING_FILE, "r") as f:
    tracking_data = json.load(f)

print("Tracking data loaded.")


# ------------------------------------------------------------
# Load team classification
# ------------------------------------------------------------

print("Loading team classification...")

with open(TEAM_FILE, "r") as f:
    team_data = json.load(f)

print("Team classification loaded.")

print()
print("Tracking data structure:")
print(type(tracking_data))

print("Team classification structure:")
print(type(team_data))


# ------------------------------------------------------------
# Get persistent Player -> Team mapping
# ------------------------------------------------------------

print()
print("Player → Team mapping")


player_teams = team_data.get("player_teams", {})


if not player_teams:

    print("ERROR: player_teams mapping is empty.")
    print()
    print("Expected structure:")
    print("""
{
    "player_teams": {
        "1": "Team A",
        "2": "Team B"
    }
}
""")

    exit()


print(f"Found {len(player_teams)} player/team mappings.")

print()

for player_id, team in player_teams.items():
    print(f"Player {player_id} → {team}")


# ------------------------------------------------------------
# Prepare position storage
# ------------------------------------------------------------

team_a_positions = []
team_b_positions = []


# ------------------------------------------------------------
# Read tracking frames
# ------------------------------------------------------------

frames = tracking_data.get("frames", [])

if not frames:
    print()
    print("ERROR: No tracking frames found.")
    exit()


print()
print(f"Processing {len(frames)} frames...")


# ------------------------------------------------------------
# Extract player positions
# ------------------------------------------------------------

for frame_data in frames:

    players = frame_data.get("players", [])

    for player in players:

        player_id = str(player.get("player_id"))

        # Ignore players without team classification
        if player_id not in player_teams:
            continue

        team = player_teams[player_id]

        # ----------------------------------------------------
        # Use bottom-center of bounding box.
        # This is closer to the player's field position
        # than the bounding-box center.
        # ----------------------------------------------------

        if "center_x" in player:
            x = player["center_x"]
        else:
            x = (player["x1"] + player["x2"]) / 2

        if "bottom_y" in player:
            y = player["bottom_y"]
        else:
            y = player["y2"]

        if team == "Team A":
            team_a_positions.append([x, y])

        elif team == "Team B":
            team_b_positions.append([x, y])


# ------------------------------------------------------------
# Convert to NumPy arrays
# ------------------------------------------------------------

team_a_positions = np.array(team_a_positions)
team_b_positions = np.array(team_b_positions)


print()
print("=" * 38)
print("POSITION SUMMARY")
print("=" * 38)

print(f"Team A positions: {len(team_a_positions)}")
print(f"Team B positions: {len(team_b_positions)}")


# ------------------------------------------------------------
# Check whether positions exist
# ------------------------------------------------------------

if len(team_a_positions) == 0:
    print("WARNING: No positions found for Team A.")

if len(team_b_positions) == 0:
    print("WARNING: No positions found for Team B.")

if len(team_a_positions) == 0 and len(team_b_positions) == 0:
    print()
    print("ERROR: No team positions could be generated.")
    exit()


# ------------------------------------------------------------
# Save position data
# ------------------------------------------------------------

positions_output = {
    "team_a": team_a_positions.tolist(),
    "team_b": team_b_positions.tolist()
}


with open(POSITIONS_OUTPUT, "w") as f:
    json.dump(positions_output, f, indent=4)


print()
print(f"Position data saved:")
print(POSITIONS_OUTPUT)


# ------------------------------------------------------------
# Get video dimensions
# ------------------------------------------------------------

VIDEO_FILE = tracking_data.get(
    "video",
    "videos/football.mp4"
)

if not os.path.exists(VIDEO_FILE):
    VIDEO_FILE = "videos/football.mp4"


cap = cv2.VideoCapture(VIDEO_FILE)

if cap.isOpened():

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cap.release()

else:

    print("WARNING: Could not read video dimensions.")

    width = 1920
    height = 1080


print()
print(f"Video dimensions: {width} x {height}")


# ============================================================
# FUNCTION: CREATE HEATMAP
# ============================================================

def create_heatmap(
    positions,
    title,
    output_file,
    width,
    height
):

    if len(positions) == 0:
        print(f"Skipping {title} - no positions.")
        return

    x = positions[:, 0]
    y = positions[:, 1]

    plt.figure(figsize=(12, 7))

    plt.hist2d(
        x,
        y,
        bins=50
    )

    plt.colorbar(
        label="Player Position Density"
    )

    plt.xlim(0, width)
    plt.ylim(height, 0)

    plt.xlabel("Image X")
    plt.ylabel("Image Y")

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200
    )

    plt.close()

    print(f"Heatmap saved: {output_file}")


# ------------------------------------------------------------
# Create Team A heatmap
# ------------------------------------------------------------

create_heatmap(
    team_a_positions,
    "SPORTFLASH - Team A Heatmap",
    TEAM_A_OUTPUT,
    width,
    height
)


# ------------------------------------------------------------
# Create Team B heatmap
# ------------------------------------------------------------

create_heatmap(
    team_b_positions,
    "SPORTFLASH - Team B Heatmap",
    TEAM_B_OUTPUT,
    width,
    height
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 38)
print("TEAM HEATMAP COMPLETED")
print("=" * 38)

print()
print("Generated files:")

if os.path.exists(TEAM_A_OUTPUT):
    print(f"✓ {TEAM_A_OUTPUT}")

if os.path.exists(TEAM_B_OUTPUT):
    print(f"✓ {TEAM_B_OUTPUT}")

if os.path.exists(POSITIONS_OUTPUT):
    print(f"✓ {POSITIONS_OUTPUT}")

print()
print("NOTE:")
print("These heatmaps use image/pixel coordinates.")
print("They are NOT real football-pitch coordinates yet.")
print()
print("Homography and field calibration will convert")
print("these positions into real pitch coordinates later.")