from ultralytics import YOLO
import matplotlib.pyplot as plt
import os

print("======================================")
print("     SPORTFLASH PLAYER HEATMAP")
print("======================================")

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO MODEL LOADED!")
print("Collecting player movement positions...")

# --------------------------------------------------
# Store positions for each player
# --------------------------------------------------

player_positions = {}

results = model.track(
    source="E:\\SPORTFLASH\\videos\\football.mp4",
    stream=True,
    persist=True,
    conf=0.5
)

for result in results:

    if result.boxes.id is None:
        continue

    boxes = result.boxes.xyxy.cpu().numpy()
    track_ids = result.boxes.id.int().cpu().tolist()

    for box, track_id in zip(boxes, track_ids):

        x1, y1, x2, y2 = box

        # Calculate player center
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        if track_id not in player_positions:
            player_positions[track_id] = []

        player_positions[track_id].append(
            (center_x, center_y)
        )

print("Movement positions collected.")

# --------------------------------------------------
# Create output folder
# --------------------------------------------------

output_folder = "results/heatmaps"

os.makedirs(output_folder, exist_ok=True)

print(f"Heatmaps will be saved in: {output_folder}")

# --------------------------------------------------
# Sort players by number of positions
# --------------------------------------------------

active_players = sorted(
    player_positions.items(),
    key=lambda x: len(x[1]),
    reverse=True
)

# --------------------------------------------------
# Select top 5 tracked players
# --------------------------------------------------

top_players = active_players[:5]

print("\nTop 5 players selected:")

for player_id, positions in top_players:
    print(
        f"Player {player_id}: "
        f"{len(positions)} positions"
    )

# --------------------------------------------------
# Generate heatmaps
# --------------------------------------------------

for player_id, positions in top_players:

    x_values = [p[0] for p in positions]
    y_values = [p[1] for p in positions]

    plt.figure(figsize=(10, 6))

    plt.hist2d(
        x_values,
        y_values,
        bins=30
    )

    plt.colorbar(
        label="Movement Density"
    )

    plt.gca().invert_yaxis()

    plt.title(
        f"SPORTFLASH - Player {player_id} Movement Heatmap"
    )

    plt.xlabel("X Position")
    plt.ylabel("Y Position")

    # --------------------------------------------------
    # Save heatmap
    # --------------------------------------------------

    output_file = os.path.join(
        output_folder,
        f"player_{player_id}_heatmap.png"
    )

    plt.savefig(
        output_file,
        dpi=150,
        bbox_inches="tight"
    )

    print(
        f"Heatmap saved: {output_file}"
    )

    plt.close()

print("\n======================================")
print("       HEATMAP GENERATION COMPLETED")
print("======================================")