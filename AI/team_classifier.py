import os
import json
import cv2
import numpy as np
from collections import defaultdict, Counter
from sklearn.cluster import KMeans
from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_PATH = "videos/football.mp4"
MODEL_PATH = "yolo11n.pt"

OUTPUT_DIR = "results"
OUTPUT_JSON = os.path.join(
    OUTPUT_DIR,
    "team_classification.json"
)

# Process every Nth frame
FRAME_INTERVAL = 10

# Minimum usable jersey pixels
MIN_PIXELS = 50

# Number of team clusters
N_CLUSTERS = 2

# YOLO confidence
CONFIDENCE = 0.5

# ByteTrack configuration
TRACKER = "bytetrack.yaml"


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# EXTRACT PLAYER JERSEY COLOR
# ============================================================

def extract_player_color(
    frame,
    x1,
    y1,
    x2,
    y2
):
    """
    Extract the central upper-body region
    of a football player.

    The head and legs are excluded as much
    as possible because they can introduce
    background and skin/short colors.
    """

    frame_height, frame_width = frame.shape[:2]

    # --------------------------------------------------------
    # Keep coordinates inside image
    # --------------------------------------------------------

    x1 = max(
        0,
        min(x1, frame_width - 1)
    )

    x2 = max(
        0,
        min(x2, frame_width)
    )

    y1 = max(
        0,
        min(y1, frame_height - 1)
    )

    y2 = max(
        0,
        min(y2, frame_height)
    )

    width = x2 - x1
    height = y2 - y1

    if width <= 0 or height <= 0:
        return None

    # --------------------------------------------------------
    # Central torso region
    # --------------------------------------------------------

    crop_x1 = x1 + int(width * 0.20)
    crop_x2 = x2 - int(width * 0.20)

    crop_y1 = y1 + int(height * 0.20)
    crop_y2 = y1 + int(height * 0.65)

    if crop_x2 <= crop_x1:
        return None

    if crop_y2 <= crop_y1:
        return None

    crop = frame[
        crop_y1:crop_y2,
        crop_x1:crop_x2
    ]

    if crop.size == 0:
        return None

    # --------------------------------------------------------
    # BGR → HSV
    # --------------------------------------------------------

    hsv = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2HSV
    )

    pixels = hsv.reshape(
        -1,
        3
    )

    # --------------------------------------------------------
    # Remove very dark pixels
    # --------------------------------------------------------

    brightness_mask = (
        pixels[:, 2] > 40
    )

    pixels = pixels[
        brightness_mask
    ]

    if len(pixels) < MIN_PIXELS:
        return None

    # --------------------------------------------------------
    # Remove extremely bright pixels
    # --------------------------------------------------------

    brightness_mask = (
        pixels[:, 2] < 245
    )

    pixels = pixels[
        brightness_mask
    ]

    if len(pixels) < MIN_PIXELS:
        return None

    # --------------------------------------------------------
    # Use Hue + Saturation
    # --------------------------------------------------------

    color_features = pixels[
        :,
        :2
    ].astype(
        np.float32
    )

    return color_features


# ============================================================
# CALCULATE MEDIAN PLAYER COLOR
# ============================================================

def calculate_player_color(
    frame,
    box
):

    x1, y1, x2, y2 = box

    color_pixels = extract_player_color(
        frame,
        x1,
        y1,
        x2,
        y2
    )

    if color_pixels is None:
        return None

    median_color = np.median(
        color_pixels,
        axis=0
    )

    return median_color


# ============================================================
# TEAM CLASSIFIER
# ============================================================

class TeamClassifier:

    def __init__(self):

        self.color_samples = []

        self.team_centers = None

    # ========================================================
    # COLLECT COLOR SAMPLES
    # ========================================================

    def collect_colors(
        self,
        video_path,
        model
    ):

        cap = cv2.VideoCapture(
            video_path
        )

        if not cap.isOpened():

            raise FileNotFoundError(
                f"Could not open video: "
                f"{video_path}"
            )

        frame_number = 0

        print(
            "\nCollecting player jersey colors..."
        )

        print(
            f"Processing every "
            f"{FRAME_INTERVAL} frames\n"
        )

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_number += 1

            if (
                frame_number %
                FRAME_INTERVAL
                != 0
            ):
                continue

            # ------------------------------------------------
            # YOLO detection
            # ------------------------------------------------

            results = model(
                frame,
                conf=CONFIDENCE,
                verbose=False
            )

            if not results:
                continue

            result = results[0]

            if result.boxes is None:
                continue

            # ------------------------------------------------
            # Process detections
            # ------------------------------------------------

            for box_data in result.boxes:

                # Class ID
                if box_data.cls is None:
                    continue

                class_id = int(
                    box_data.cls[0].item()
                )

                # COCO class 0 = person
                if class_id != 0:
                    continue

                # Confidence
                if box_data.conf is None:
                    continue

                confidence = float(
                    box_data.conf[0].item()
                )

                if confidence < CONFIDENCE:
                    continue

                # Bounding box
                coordinates = (
                    box_data.xyxy[0]
                    .cpu()
                    .numpy()
                )

                x1, y1, x2, y2 = (
                    coordinates.astype(int)
                )

                # Extract color
                color = calculate_player_color(
                    frame,
                    (
                        x1,
                        y1,
                        x2,
                        y2
                    )
                )

                if color is None:
                    continue

                # Save sample
                self.color_samples.append(
                    {
                        "hue": float(
                            color[0]
                        ),
                        "saturation": float(
                            color[1]
                        )
                    }
                )

        cap.release()

        print(
            f"Collected "
            f"{len(self.color_samples)} "
            f"color samples."
        )

    # ========================================================
    # BUILD K-MEANS CLUSTERS
    # ========================================================

    def build_clusters(self):

        if len(
            self.color_samples
        ) < N_CLUSTERS:

            raise RuntimeError(
                "Not enough player "
                "color samples to "
                "identify two teams."
            )

        data = []

        for sample in (
            self.color_samples
        ):

            data.append(
                [
                    sample["hue"],
                    sample["saturation"]
                ]
            )

        data = np.array(
            data,
            dtype=np.float32
        )

        print(
            "\nRunning K-Means "
            "team clustering..."
        )

        kmeans = KMeans(
            n_clusters=N_CLUSTERS,
            random_state=42,
            n_init=10
        )

        kmeans.fit(data)

        self.team_centers = (
            kmeans.cluster_centers_
        )

        print(
            "\nTeam cluster centers:"
        )

        for index, center in enumerate(
            self.team_centers
        ):

            print(
                f"Cluster {index}: "
                f"Hue={center[0]:.2f}, "
                f"Saturation="
                f"{center[1]:.2f}"
            )

    # ========================================================
    # PREDICT TEAM
    # ========================================================

    def predict_team(
        self,
        color
    ):

        if color is None:
            return "Unknown"

        if self.team_centers is None:
            return "Unknown"

        point = np.array(
            [
                [
                    color[0],
                    color[1]
                ]
            ],
            dtype=np.float32
        )

        distances = np.linalg.norm(
            self.team_centers -
            point,
            axis=1
        )

        cluster = int(
            np.argmin(distances)
        )

        if cluster == 0:
            return "Team A"

        return "Team B"


# ============================================================
# PROCESS VIDEO
# ============================================================

def process_video():

    print(
        "\n======================================"
    )

    print(
        "SPORTFLASH TEAM CLASSIFIER"
    )

    print(
        "TRACKING + JERSEY COLOR + K-MEANS"
    )

    print(
        "======================================"
    )

    # ========================================================
    # CHECK VIDEO
    # ========================================================

    if not os.path.exists(
        VIDEO_PATH
    ):

        raise FileNotFoundError(
            f"Video not found: "
            f"{VIDEO_PATH}"
        )

    # ========================================================
    # LOAD YOLO
    # ========================================================

    print(
        "\nLoading YOLO model..."
    )

    model = YOLO(
        MODEL_PATH
    )

    print(
        "YOLO model loaded."
    )

    # ========================================================
    # CREATE CLASSIFIER
    # ========================================================

    classifier = TeamClassifier()

    # ========================================================
    # STEP 1
    # COLLECT JERSEY COLORS
    # ========================================================

    classifier.collect_colors(
        VIDEO_PATH,
        model
    )

    # ========================================================
    # STEP 2
    # BUILD K-MEANS
    # ========================================================

    classifier.build_clusters()

    # ========================================================
    # STEP 3
    # TRACK PLAYERS
    # ========================================================

    print(
        "\nStarting persistent "
        "player tracking..."
    )

    print(
        "This may take some time...\n"
    )

    # --------------------------------------------------------
    # Player team votes
    #
    # Example:
    #
    # Player 1:
    # Team A = 80
    # Team B = 5
    #
    # Final = Team A
    # --------------------------------------------------------

    player_votes = defaultdict(list)

    # --------------------------------------------------------
    # Color history
    # --------------------------------------------------------

    player_colors = defaultdict(list)

    # --------------------------------------------------------
    # Detection counts
    # --------------------------------------------------------

    player_detection_count = defaultdict(
        int
    )

    # --------------------------------------------------------
    # Open video
    # --------------------------------------------------------

    cap = cv2.VideoCapture(
        VIDEO_PATH
    )

    if not cap.isOpened():

        raise FileNotFoundError(
            f"Could not open video: "
            f"{VIDEO_PATH}"
        )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    print(
        f"Total frames: "
        f"{total_frames}"
    )

    print(
        f"FPS: "
        f"{fps:.2f}"
    )

    frame_number = 0

    # ========================================================
    # FRAME LOOP
    # ========================================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_number += 1

        # ----------------------------------------------------
        # Process every Nth frame
        # ----------------------------------------------------

        if (
            frame_number %
            FRAME_INTERVAL
            != 0
        ):
            continue

        # ----------------------------------------------------
        # YOLO TRACKING
        # ----------------------------------------------------

        results = model.track(
            frame,
            persist=True,
            tracker=TRACKER,
            conf=CONFIDENCE,
            verbose=False
        )

        if not results:
            continue

        result = results[0]

        if result.boxes is None:
            continue

        # ----------------------------------------------------
        # Tracking IDs
        # ----------------------------------------------------

        if result.boxes.id is None:
            continue

        track_ids = (
            result.boxes.id
            .cpu()
            .numpy()
            .astype(int)
        )

        # ====================================================
        # PROCESS EACH DETECTION
        # ====================================================

        for index, box_data in enumerate(
            result.boxes
        ):

            # ------------------------------------------------
            # Make sure tracking ID exists
            # ------------------------------------------------

            if index >= len(
                track_ids
            ):
                continue

            # ------------------------------------------------
            # CLASS ID
            # ------------------------------------------------

            if box_data.cls is None:
                continue

            class_id = int(
                box_data.cls[0].item()
            )

            # COCO class 0 = person
            if class_id != 0:
                continue

            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            if box_data.conf is None:
                continue

            confidence = float(
                box_data.conf[0].item()
            )

            if confidence < CONFIDENCE:
                continue

            # ------------------------------------------------
            # PERSISTENT PLAYER ID
            # ------------------------------------------------

            player_id = int(
                track_ids[index]
            )

            # ------------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------------

            coordinates = (
                box_data.xyxy[0]
                .cpu()
                .numpy()
            )

            x1, y1, x2, y2 = (
                coordinates.astype(int)
            )

            # ------------------------------------------------
            # EXTRACT JERSEY COLOR
            # ------------------------------------------------

            color = calculate_player_color(
                frame,
                (
                    x1,
                    y1,
                    x2,
                    y2
                )
            )

            if color is None:
                continue

            # ------------------------------------------------
            # CLASSIFY TEAM
            # ------------------------------------------------

            team = classifier.predict_team(
                color
            )

            # ------------------------------------------------
            # SAVE TEAM VOTE
            # ------------------------------------------------

            player_votes[
                player_id
            ].append(
                team
            )

            # ------------------------------------------------
            # SAVE COLOR
            # ------------------------------------------------

            player_colors[
                player_id
            ].append(
                {
                    "hue": float(
                        color[0]
                    ),
                    "saturation": float(
                        color[1]
                    )
                }
            )

            # ------------------------------------------------
            # DETECTION COUNT
            # ------------------------------------------------

            player_detection_count[
                player_id
            ] += 1

        # ====================================================
        # PROGRESS
        # ====================================================

        if frame_number % 100 == 0:

            unique_players = len(
                player_votes
            )

            print(
                f"Processed frame "
                f"{frame_number}/"
                f"{total_frames} "
                f"| Players tracked: "
                f"{unique_players}"
            )

    cap.release()

    # ========================================================
    # STEP 4
    # FINAL PLAYER TEAM ASSIGNMENT
    # ========================================================

    print(
        "\nFinalizing "
        "player/team mapping..."
    )

    player_teams = {}

    player_details = {}

    # ========================================================
    # PROCESS EACH PLAYER
    # ========================================================

    for player_id in sorted(
        player_votes.keys()
    ):

        votes = player_votes[
            player_id
        ]

        if not votes:
            continue

        # ----------------------------------------------------
        # Count votes
        # ----------------------------------------------------

        vote_counter = Counter(
            votes
        )

        # ----------------------------------------------------
        # Majority team
        # ----------------------------------------------------

        final_team = (
            vote_counter
            .most_common(1)[0][0]
        )

        # ----------------------------------------------------
        # Color statistics
        # ----------------------------------------------------

        colors = player_colors[
            player_id
        ]

        if colors:

            average_hue = float(
                np.mean(
                    [
                        item["hue"]
                        for item in colors
                    ]
                )
            )

            average_saturation = float(
                np.mean(
                    [
                        item["saturation"]
                        for item in colors
                    ]
                )
            )

        else:

            average_hue = 0.0

            average_saturation = 0.0

        # ----------------------------------------------------
        # Team confidence
        # ----------------------------------------------------

        total_votes = len(
            votes
        )

        winning_votes = (
            vote_counter[
                final_team
            ]
        )

        team_confidence = (
            winning_votes /
            total_votes
        ) * 100

        # ----------------------------------------------------
        # Save mapping
        # ----------------------------------------------------

        player_teams[
            str(player_id)
        ] = final_team

        # ----------------------------------------------------
        # Save details
        # ----------------------------------------------------

        player_details[
            str(player_id)
        ] = {

            "team": final_team,

            "detections": (
                player_detection_count[
                    player_id
                ]
            ),

            "team_votes": {

                "Team A": (
                    vote_counter.get(
                        "Team A",
                        0
                    )
                ),

                "Team B": (
                    vote_counter.get(
                        "Team B",
                        0
                    )
                )
            },

            "team_confidence": round(
                team_confidence,
                2
            ),

            "average_hue": round(
                average_hue,
                2
            ),

            "average_saturation": round(
                average_saturation,
                2
            )
        }

    # ========================================================
    # STEP 5
    # TEAM SUMMARY
    # ========================================================

    team_a_players = []

    team_b_players = []

    for player_id, team in (
        player_teams.items()
    ):

        if team == "Team A":

            team_a_players.append(
                int(player_id)
            )

        elif team == "Team B":

            team_b_players.append(
                int(player_id)
            )

    team_a_players.sort()

    team_b_players.sort()

    # ========================================================
    # STEP 6
    # CREATE FINAL JSON
    # ========================================================

    final_results = {

        "video": VIDEO_PATH,

        "method": {

            "tracking":
                "YOLO persistent tracking",

            "team_classification":
                "HSV jersey color + K-Means",

            "voting":
                "Majority voting across frames",

            "frame_interval":
                FRAME_INTERVAL,

            "confidence_threshold":
                CONFIDENCE
        },

        "player_teams":
            player_teams,

        "summary": {

            "total_players":
                len(player_teams),

            "team_a_players":
                team_a_players,

            "team_b_players":
                team_b_players,

            "team_a_count":
                len(team_a_players),

            "team_b_count":
                len(team_b_players)
        },

        "player_details":
            player_details
    }

    # ========================================================
    # STEP 7
    # SAVE JSON
    # ========================================================

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_results,
            file,
            indent=4
        )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "TEAM CLASSIFICATION COMPLETED"
    )

    print(
        "======================================"
    )

    print(
        f"\nResults saved to:"
    )

    print(
        OUTPUT_JSON
    )

    print(
        "\nClassification summary:"
    )

    print(
        f"Total players: "
        f"{len(player_teams)}"
    )

    print(
        f"Team A: "
        f"{len(team_a_players)}"
    )

    print(
        f"Team B: "
        f"{len(team_b_players)}"
    )

    print(
        "\nPlayer → Team mapping:"
    )

    for player_id in sorted(
        player_teams,
        key=lambda value: int(value)
    ):

        team = player_teams[
            player_id
        ]

        confidence = (
            player_details[
                player_id
            ][
                "team_confidence"
            ]
        )

        print(
            f"Player {player_id}: "
            f"{team} "
            f"({confidence:.1f}% confidence)"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    process_video()