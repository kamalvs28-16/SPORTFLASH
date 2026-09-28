import streamlit as st
import json
import os
import pandas as pd


# ============================================================
# SPORTFLASH
# AI FOOTBALL PERFORMANCE ANALYTICS DASHBOARD
# ============================================================

st.set_page_config(
    page_title="SPORTFLASH AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DIRECTORIES
# ============================================================

RESULTS_DIR = "results"
HEATMAP_DIR = os.path.join(RESULTS_DIR, "heatmaps")


# ============================================================
# EXISTING SPORTFLASH FILES
# ============================================================

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

ACCELERATION_FILE = os.path.join(
    RESULTS_DIR,
    "acceleration_results.json"
)

ZONE_FILE = os.path.join(
    RESULTS_DIR,
    "zone_results.json"
)

BALL_FILE = os.path.join(
    RESULTS_DIR,
    "ball_results.json"
)

AI_FILE = os.path.join(
    RESULTS_DIR,
    "ai_insights.json"
)

NUTRITION_FILE = os.path.join(
    RESULTS_DIR,
    "nutrition_recommendations.json"
)

RANKING_FILE = os.path.join(
    RESULTS_DIR,
    "player_ranking.json"
)

TEAM_FILE = os.path.join(
    RESULTS_DIR,
    "team_analysis.json"
)

COMPARISON_FILE = os.path.join(
    RESULTS_DIR,
    "player_comparison.json"
)


# ============================================================
# NEW ADVANCED ANALYSIS FILES
# ============================================================

TRACKING_FILE = os.path.join(
    RESULTS_DIR,
    "tracking_results.json"
)

TEAM_CLASSIFICATION_FILE = os.path.join(
    RESULTS_DIR,
    "team_classification.json"
)

TEAM_HEATMAP_POSITIONS_FILE = os.path.join(
    RESULTS_DIR,
    "team_heatmap_positions.json"
)

TEAM_A_HEATMAP_FILE = os.path.join(
    RESULTS_DIR,
    "team_a_heatmap.png"
)

TEAM_B_HEATMAP_FILE = os.path.join(
    RESULTS_DIR,
    "team_b_heatmap.png"
)

PITCH_CALIBRATION_FILE = os.path.join(
    RESULTS_DIR,
    "pitch_calibration.json"
)

HOMOGRAPHY_FILE = os.path.join(
    RESULTS_DIR,
    "homography_positions.json"
)

DISTANCE_FILE = os.path.join(
    RESULTS_DIR,
    "distance_analysis.json"
)

CAMERA_FILE = os.path.join(
    RESULTS_DIR,
    "camera_motion.json"
)

DYNAMIC_CALIBRATION_FILE = os.path.join(
    RESULTS_DIR,
    "dynamic_calibration.json"
)

DYNAMIC_DISTANCE_FILE = os.path.join(
    RESULTS_DIR,
    "dynamic_distance_analysis.json"
)

EVENT_FILE = os.path.join(
    RESULTS_DIR,
    "event_detection.json"
)

MATCH_REPORT_FILE = os.path.join(
    RESULTS_DIR,
    "match_report.json"
)


# ============================================================
# VIDEO
# ============================================================

VIDEO_FILE = os.path.join(
    "videos",
    "football.mp4"
)


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    if not os.path.exists(file_path):
        return {}

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


# ============================================================
# HELPERS
# ============================================================

def safe_float(
    value,
    default=0.0
):

    try:

        return float(value)

    except:

        return default


def safe_int(
    value,
    default=0
):

    try:

        return int(value)

    except:

        return default


def file_available(path):

    return os.path.exists(path)


# ============================================================
# LOAD EXISTING DATA
# ============================================================

performance_data = load_json(
    PERFORMANCE_FILE
)

movement_data = load_json(
    MOVEMENT_FILE
)

speed_data = load_json(
    SPEED_FILE
)

acceleration_data = load_json(
    ACCELERATION_FILE
)

zone_data = load_json(
    ZONE_FILE
)

ball_data = load_json(
    BALL_FILE
)

ai_data = load_json(
    AI_FILE
)

nutrition_data = load_json(
    NUTRITION_FILE
)

ranking_data = load_json(
    RANKING_FILE
)

team_data = load_json(
    TEAM_FILE
)

comparison_data = load_json(
    COMPARISON_FILE
)


# ============================================================
# LOAD ADVANCED DATA
# ============================================================

tracking_data = load_json(
    TRACKING_FILE
)

team_classification_data = load_json(
    TEAM_CLASSIFICATION_FILE
)

team_heatmap_positions = load_json(
    TEAM_HEATMAP_POSITIONS_FILE
)

pitch_calibration_data = load_json(
    PITCH_CALIBRATION_FILE
)

homography_data = load_json(
    HOMOGRAPHY_FILE
)

distance_data = load_json(
    DISTANCE_FILE
)

camera_data = load_json(
    CAMERA_FILE
)

dynamic_calibration_data = load_json(
    DYNAMIC_CALIBRATION_FILE
)

dynamic_distance_data = load_json(
    DYNAMIC_DISTANCE_FILE
)

event_data = load_json(
    EVENT_FILE
)

match_report_data = load_json(
    MATCH_REPORT_FILE
)


# ============================================================
# EXTRACT MATCH REPORT SECTIONS
# ============================================================

match_team = match_report_data.get(
    "team_analysis",
    {}
)

match_movement = match_report_data.get(
    "movement_analysis",
    {}
)

match_events = match_report_data.get(
    "event_analysis",
    {}
)

match_camera = match_report_data.get(
    "camera_analysis",
    {}
)

match_calibration = match_report_data.get(
    "calibration_analysis",
    {}
)

match_top_players = match_report_data.get(
    "top_players",
    {}
)

match_player_reports = match_report_data.get(
    "player_reports",
    []
)


# ============================================================
# PLAYER FUNCTIONS
# ============================================================

def get_player_performance(player_id):

    data = performance_data.get(
        str(player_id),
        {}
    )

    if isinstance(data, dict):

        return safe_float(
            data.get(
                "performance_score",
                data.get(
                    "score",
                    0
                )
            )
        )

    if isinstance(
        data,
        (int, float)
    ):

        return float(data)

    return 0.0


def get_player_movement(player_id):

    data = movement_data.get(
        str(player_id),
        0
    )

    if isinstance(data, dict):

        return safe_float(
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

    if isinstance(
        data,
        (int, float)
    ):

        return float(data)

    return 0.0


def get_player_speed(player_id):

    data = speed_data.get(
        str(player_id),
        {}
    )

    if not isinstance(
        data,
        dict
    ):

        return 0.0, 0.0, "pixels/sec"

    average = safe_float(
        data.get(
            "average_speed",
            data.get(
                "average_speed_pixels_per_second",
                0
            )
        )
    )

    maximum = safe_float(
        data.get(
            "maximum_speed",
            data.get(
                "maximum_speed_pixels_per_second",
                0
            )
        )
    )

    unit = data.get(
        "unit",
        "pixels/sec"
    )

    return (
        average,
        maximum,
        unit
    )


def get_player_acceleration(player_id):

    data = acceleration_data.get(
        str(player_id),
        {}
    )

    if not isinstance(
        data,
        dict
    ):

        return {
            "average_acceleration": 0,
            "maximum_acceleration": 0,
            "average_deceleration": 0,
            "maximum_deceleration": 0,
            "acceleration_events": 0,
            "deceleration_events": 0,
            "unit": "pixels/sec²"
        }

    return {

        "average_acceleration":
            safe_float(
                data.get(
                    "average_acceleration",
                    data.get(
                        "average_acceleration_pixels_per_second_squared",
                        0
                    )
                )
            ),

        "maximum_acceleration":
            safe_float(
                data.get(
                    "maximum_acceleration",
                    data.get(
                        "maximum_acceleration_pixels_per_second_squared",
                        0
                    )
                )
            ),

        "average_deceleration":
            safe_float(
                data.get(
                    "average_deceleration",
                    data.get(
                        "average_deceleration_pixels_per_second_squared",
                        0
                    )
                )
            ),

        "maximum_deceleration":
            safe_float(
                data.get(
                    "maximum_deceleration",
                    data.get(
                        "maximum_deceleration_pixels_per_second_squared",
                        0
                    )
                )
            ),

        "acceleration_events":
            safe_int(
                data.get(
                    "acceleration_events",
                    0
                )
            ),

        "deceleration_events":
            safe_int(
                data.get(
                    "deceleration_events",
                    0
                )
            ),

        "unit":
            data.get(
                "unit",
                "pixels/sec²"
            )
    }


def get_player_zone(player_id):

    data = zone_data.get(
        str(player_id),
        {}
    )

    if not isinstance(
        data,
        dict
    ):

        return {
            "defensive": 0,
            "midfield": 0,
            "attacking": 0
        }

    return {

        "defensive":
            safe_float(
                data.get(
                    "defensive",
                    0
                )
            ),

        "midfield":
            safe_float(
                data.get(
                    "midfield",
                    0
                )
            ),

        "attacking":
            safe_float(
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

    return safe_int(
        interaction_data.get(
            str(player_id),
            0
        )
    )


def get_player_ai(player_id):

    data = ai_data.get(
        str(player_id),
        {}
    )

    if isinstance(
        data,
        dict
    ):

        return data

    return {}


def get_player_nutrition(player_id):

    data = nutrition_data.get(
        str(player_id),
        {}
    )

    if isinstance(
        data,
        dict
    ):

        return data

    return {}


# ============================================================
# FIND EXISTING PLAYER IDS
# ============================================================

player_ids = set()


datasets = [
    performance_data,
    movement_data,
    speed_data,
    acceleration_data,
    zone_data
]


for dataset in datasets:

    if isinstance(
        dataset,
        dict
    ):

        for player_id in dataset.keys():

            try:

                player_ids.add(
                    int(player_id)
                )

            except:

                pass


# ============================================================
# ALSO ADD ADVANCED PLAYER IDS
# ============================================================

if isinstance(
    dynamic_distance_data,
    dict
):

    advanced_players = (
        dynamic_distance_data.get(
            "players",
            []
        )
    )

    if isinstance(
        advanced_players,
        list
    ):

        for player in advanced_players:

            try:

                player_ids.add(
                    int(
                        player.get(
                            "player_id"
                        )
                    )
                )

            except:

                pass


if isinstance(
    match_player_reports,
    list
):

    for player in match_player_reports:

        try:

            player_ids.add(
                int(
                    player.get(
                        "player_id"
                    )
                )
            )

        except:

            pass


player_ids = sorted(
    player_ids
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "⚽ SPORTFLASH AI"
)

st.subheader(
    "Football Performance & Tactical Analytics"
)

st.write(
    "Computer vision based football analysis "
    "using player tracking, team classification, "
    "movement analysis, field calibration, "
    "speed estimation, event detection and AI insights."
)

st.markdown("---")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚽ SPORTFLASH"
)

st.sidebar.caption(
    "AI Football Analytics Platform"
)

st.sidebar.markdown("---")


pages = [

    "🏠 Dashboard Overview",

    "👤 Player Analytics",

    "👥 Team Classification",

    "🔥 Team Heatmaps",

    "⚡ Speed & Distance",

    "🚀 Acceleration",

    "🗺️ Field Zones",

    "⚽ Ball Analysis",

    "🎯 Event Detection",

    "📹 Camera Motion",

    "📐 Field Calibration",

    "🏆 Player Ranking",

    "🤖 AI Insights",

    "🥗 Nutrition",

    "🔍 Player Comparison",

    "📄 Match Report",

    "📊 Data Status"

]


selected_page = st.sidebar.radio(
    "Navigation",
    pages
)


st.sidebar.markdown("---")

st.sidebar.success(
    "AI Pipeline Loaded"
)


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

if selected_page == "🏠 Dashboard Overview":

    st.header(
        "🏠 SPORTFLASH Dashboard"
    )

    total_players = safe_int(
        match_movement.get(
            "players_analysed",
            len(player_ids)
        )
    )

    detected_players = safe_int(
        match_movement.get(
            "total_players_detected",
            len(player_ids)
        )
    )

    team_a = safe_int(
        match_team.get(
            "team_a_count",
            0
        )
    )

    team_b = safe_int(
        match_team.get(
            "team_b_count",
            0
        )
    )

    events = safe_int(
        match_events.get(
            "total_events",
            0
        )
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(
            "Players Analysed",
            total_players
        )

    with col2:

        st.metric(
            "Players Detected",
            detected_players
        )

    with col3:

        st.metric(
            "Team A",
            team_a
        )

    with col4:

        st.metric(
            "Team B",
            team_b
        )

    with col5:

        st.metric(
            "Potential Events",
            events
        )


    st.markdown("---")


    # --------------------------------------------------------
    # VIDEO
    # --------------------------------------------------------

    st.header(
        "🎥 Match Video"
    )

    if file_available(
        VIDEO_FILE
    ):

        st.video(
            VIDEO_FILE
        )

    else:

        st.warning(
            "videos/football.mp4 not found."
        )


    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    st.header(
        "🧠 AI Analysis Pipeline"
    )

    pipeline = {

        "Player Detection & Tracking":
            file_available(
                TRACKING_FILE
            ),

        "Team Classification":
            file_available(
                TEAM_CLASSIFICATION_FILE
            ),

        "Team Heatmaps":
            (
                file_available(
                    TEAM_A_HEATMAP_FILE
                )
                and
                file_available(
                    TEAM_B_HEATMAP_FILE
                )
            ),

        "Homography":
            file_available(
                HOMOGRAPHY_FILE
            ),

        "Distance Analysis":
            file_available(
                DISTANCE_FILE
            ),

        "Camera Motion":
            file_available(
                CAMERA_FILE
            ),

        "Dynamic Calibration":
            file_available(
                DYNAMIC_CALIBRATION_FILE
            ),

        "Dynamic Distance":
            file_available(
                DYNAMIC_DISTANCE_FILE
            ),

        "Event Detection":
            file_available(
                EVENT_FILE
            ),

        "Match Report":
            file_available(
                MATCH_REPORT_FILE
            )
    }


    pipeline_rows = []

    for module, available in pipeline.items():

        pipeline_rows.append(
            {
                "Module":
                    module,

                "Status":
                    "✅ Complete"
                    if available
                    else "❌ Missing"
            }
        )


    st.dataframe(
        pd.DataFrame(
            pipeline_rows
        ),
        width="stretch",
        hide_index=True
    )


    st.info(
        "Distance, speed and movement-event values "
        "are potential/estimated analytics and should "
        "not be presented as ground-truth measurements."
    )


# ============================================================
# PLAYER ANALYTICS
# ============================================================

elif selected_page == "👤 Player Analytics":

    st.header(
        "👤 Player Analytics"
    )

    if not player_ids:

        st.error(
            "No player data found."
        )

        st.stop()


    selected_player = st.selectbox(
        "Select Player",
        player_ids
    )


    performance = get_player_performance(
        selected_player
    )

    movement = get_player_movement(
        selected_player
    )

    average_speed, maximum_speed, speed_unit = (
        get_player_speed(
            selected_player
        )
    )

    acceleration = get_player_acceleration(
        selected_player
    )

    zones = get_player_zone(
        selected_player
    )

    interactions = get_ball_interactions(
        selected_player
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Performance",
            f"{performance:.2f}/100"
        )


    with col2:

        st.metric(
            "Movement",
            f"{movement:.2f}"
        )


    with col3:

        st.metric(
            "Average Speed",
            f"{average_speed:.2f}"
        )


    with col4:

        st.metric(
            "Max Speed",
            f"{maximum_speed:.2f}"
        )


    st.markdown("---")


    player_table = pd.DataFrame(
        [
            {
                "Metric":
                    "Performance Score",

                "Value":
                    performance
            },

            {
                "Metric":
                    "Movement",

                "Value":
                    movement
            },

            {
                "Metric":
                    "Average Speed",

                "Value":
                    average_speed
            },

            {
                "Metric":
                    "Maximum Speed",

                "Value":
                    maximum_speed
            },

            {
                "Metric":
                    "Average Acceleration",

                "Value":
                    acceleration[
                        "average_acceleration"
                    ]
            },

            {
                "Metric":
                    "Maximum Acceleration",

                "Value":
                    acceleration[
                        "maximum_acceleration"
                    ]
            },

            {
                "Metric":
                    "Ball Interactions",

                "Value":
                    interactions
            }
        ]
    )


    st.dataframe(
        player_table,
        width="stretch",
        hide_index=True
    )


    st.subheader(
        "📊 Player Metrics"
    )

    st.bar_chart(
        player_table.set_index(
            "Metric"
        )
    )


    # Player heatmap

    heatmap_path = os.path.join(
        HEATMAP_DIR,
        f"player_{selected_player}_heatmap.png"
    )


    if file_available(
        heatmap_path
    ):

        st.subheader(
            "🔥 Player Heatmap"
        )

        st.image(
            heatmap_path,
            caption=
            f"Player {selected_player} Heatmap",
            width="stretch"
        )


# ============================================================
# TEAM CLASSIFICATION
# ============================================================

elif selected_page == "👥 Team Classification":

    st.header(
        "👥 AI Team Classification"
    )

    summary = team_classification_data.get(
        "summary",
        {}
    )


    team_a_players = summary.get(
        "team_a_players",
        []
    )

    team_b_players = summary.get(
        "team_b_players",
        []
    )


    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "Team A"
        )

        st.metric(
            "Players",
            safe_int(
                summary.get(
                    "team_a_count",
                    len(team_a_players)
                )
            )
        )

        st.write(
            team_a_players
        )


    with col2:

        st.subheader(
            "Team B"
        )

        st.metric(
            "Players",
            safe_int(
                summary.get(
                    "team_b_count",
                    len(team_b_players)
                )
            )
        )

        st.write(
            team_b_players
        )


    st.markdown("---")


    st.subheader(
        "📊 Team Distribution"
    )


    team_distribution = pd.DataFrame(
        {
            "Players": [
                len(team_a_players),
                len(team_b_players)
            ]
        },

        index=[
            "Team A",
            "Team B"
        ]
    )


    st.bar_chart(
        team_distribution
    )


    st.warning(
        "Team A and Team B are algorithmic labels "
        "generated by the classification pipeline. "
        "They are not the real-world team names."
    )


# ============================================================
# TEAM HEATMAPS
# ============================================================

elif selected_page == "🔥 Team Heatmaps":

    st.header(
        "🔥 Team Movement Heatmaps"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "Team A Heatmap"
        )

        if file_available(
            TEAM_A_HEATMAP_FILE
        ):

            st.image(
                TEAM_A_HEATMAP_FILE,
                width="stretch"
            )

        else:

            st.warning(
                "Team A heatmap unavailable."
            )


    with col2:

        st.subheader(
            "Team B Heatmap"
        )

        if file_available(
            TEAM_B_HEATMAP_FILE
        ):

            st.image(
                TEAM_B_HEATMAP_FILE,
                width="stretch"
            )

        else:

            st.warning(
                "Team B heatmap unavailable."
            )


    st.info(
        "These heatmaps currently represent "
        "player movement in image/pixel coordinates."
    )


    if team_heatmap_positions:

        st.subheader(
            "📍 Team Position Data"
        )

        positions = (
            team_heatmap_positions.get(
                "positions",
                []
            )
        )


        if positions:

            st.dataframe(
                pd.DataFrame(
                    positions
                ).head(500),
                width="stretch",
                hide_index=True
            )


# ============================================================
# SPEED & DISTANCE
# ============================================================

elif selected_page == "⚡ Speed & Distance":

    st.header(
        "⚡ Dynamic Speed & Distance Analysis"
    )


    st.warning(
        "These measurements are estimates generated "
        "from the current computer-vision calibration "
        "pipeline."
    )


    players = dynamic_distance_data.get(
        "players",
        []
    )


    if players:

        rows = []


        for player in players:

            rows.append(
                {
                    "Player":
                        player.get(
                            "player_id",
                            0
                        ),

                    "Distance (m)":
                        safe_float(
                            player.get(
                                "total_distance_m",
                                0
                            )
                        ),

                    "Average Speed (km/h)":
                        safe_float(
                            player.get(
                                "average_speed_kmh",
                                0
                            )
                        ),

                    "Maximum Speed (km/h)":
                        safe_float(
                            player.get(
                                "maximum_speed_kmh",
                                0
                            )
                        ),

                    "Valid Movements":
                        safe_int(
                            player.get(
                                "valid_movements",
                                0
                            )
                        ),

                    "Rejected":
                        safe_int(
                            player.get(
                                "rejected_movements",
                                0
                            )
                        ),

                    "Active Time (sec)":
                        safe_float(
                            player.get(
                                "active_time_seconds",
                                0
                            )
                        )
                }
            )


        dynamic_df = pd.DataFrame(
            rows
        )


        st.dataframe(
            dynamic_df,
            width="stretch",
            hide_index=True
        )


        st.subheader(
            "📏 Distance by Player"
        )


        st.bar_chart(
            dynamic_df.set_index(
                "Player"
            )[
                "Distance (m)"
            ]
        )


        st.subheader(
            "🏎️ Maximum Speed by Player"
        )


        st.bar_chart(
            dynamic_df.set_index(
                "Player"
            )[
                "Maximum Speed (km/h)"
            ]
        )


    else:

        st.warning(
            "dynamic_distance_analysis.json "
            "is not available."
        )


# ============================================================
# ACCELERATION
# ============================================================

elif selected_page == "🚀 Acceleration":

    st.header(
        "🚀 Acceleration & Deceleration"
    )


    rows = []


    for player_id in player_ids:

        acceleration = get_player_acceleration(
            player_id
        )


        rows.append(
            {
                "Player":
                    player_id,

                "Avg Acceleration":
                    acceleration[
                        "average_acceleration"
                    ],

                "Max Acceleration":
                    acceleration[
                        "maximum_acceleration"
                    ],

                "Avg Deceleration":
                    acceleration[
                        "average_deceleration"
                    ],

                "Max Deceleration":
                    acceleration[
                        "maximum_deceleration"
                    ],

                "Acceleration Events":
                    acceleration[
                        "acceleration_events"
                    ],

                "Deceleration Events":
                    acceleration[
                        "deceleration_events"
                    ]
            }
        )


    acceleration_df = pd.DataFrame(
        rows
    )


    st.dataframe(
        acceleration_df,
        width="stretch",
        hide_index=True
    )


    st.subheader(
        "📊 Maximum Acceleration"
    )


    st.bar_chart(
        acceleration_df.set_index(
            "Player"
        )[
            "Max Acceleration"
        ]
    )


# ============================================================
# FIELD ZONES
# ============================================================

elif selected_page == "🗺️ Field Zones":

    st.header(
        "🗺️ Field Zone Analysis"
    )


    if not player_ids:

        st.warning(
            "No players available."
        )

    else:

        selected_player = st.selectbox(
            "Select Player",
            player_ids,
            key="zone_player"
        )


        zones = get_player_zone(
            selected_player
        )


        zone_df = pd.DataFrame(
            {
                "Zone": [
                    "Defensive",
                    "Midfield",
                    "Attacking"
                ],

                "Percentage": [
                    zones["defensive"],
                    zones["midfield"],
                    zones["attacking"]
                ]
            }
        )


        col1, col2, col3 = (
            st.columns(3)
        )


        with col1:

            st.metric(
                "Defensive",
                f"{zones['defensive']:.2f}%"
            )


        with col2:

            st.metric(
                "Midfield",
                f"{zones['midfield']:.2f}%"
            )


        with col3:

            st.metric(
                "Attacking",
                f"{zones['attacking']:.2f}%"
            )


        st.bar_chart(
            zone_df.set_index(
                "Zone"
            )
        )


# ============================================================
# BALL ANALYSIS
# ============================================================

elif selected_page == "⚽ Ball Analysis":

    st.header(
        "⚽ Ball Analysis"
    )


    total_interactions = safe_int(
        ball_data.get(
            "total_player_ball_interactions",
            0
        )
    )


    average_ball_speed = safe_float(
        ball_data.get(
            "average_ball_speed_pixels_per_second",
            0
        )
    )


    maximum_ball_speed = safe_float(
        ball_data.get(
            "maximum_ball_speed_pixels_per_second",
            0
        )
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "Total Interactions",
            total_interactions
        )


    with col2:

        st.metric(
            "Average Ball Speed",
            f"{average_ball_speed:.2f} px/s"
        )


    with col3:

        st.metric(
            "Maximum Ball Speed",
            f"{maximum_ball_speed:.2f} px/s"
        )


    interaction_data = ball_data.get(
        "interaction_counts",
        {}
    )


    if isinstance(
        interaction_data,
        dict
    ) and interaction_data:

        interaction_rows = []


        for player, count in (
            interaction_data.items()
        ):

            interaction_rows.append(
                {
                    "Player":
                        player,

                    "Interactions":
                        safe_int(count)
                }
            )


        interaction_df = pd.DataFrame(
            interaction_rows
        )


        st.subheader(
            "Player-Ball Interactions"
        )


        st.dataframe(
            interaction_df,
            width="stretch",
            hide_index=True
        )


        st.bar_chart(
            interaction_df.set_index(
                "Player"
            )
        )


    st.caption(
        "Ball speed is currently represented in "
        "pixel-based units."
    )


# ============================================================
# EVENT DETECTION
# ============================================================

elif selected_page == "🎯 Event Detection":

    st.header(
        "🎯 AI Event Detection"
    )


    event_summary = event_data.get(
        "summary",
        {}
    )


    total_events = safe_int(
        event_summary.get(
            "total_events",
            match_events.get(
                "total_events",
                0
            )
        )
    )


    event_counts = event_summary.get(
        "event_counts",
        match_events.get(
            "event_counts",
            {}
        )
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Total Events",
            total_events
        )


    with col2:

        st.metric(
            "Potential Sprints",
            safe_int(
                event_counts.get(
                    "potential_sprint",
                    0
                )
            )
        )


    with col3:

        st.metric(
            "Low Movement",
            safe_int(
                event_counts.get(
                    "low_movement_period",
                    0
                )
            )
        )


    with col4:

        st.metric(
            "Tracking Warnings",
            safe_int(
                event_counts.get(
                    "tracking_quality_warning",
                    0
                )
            )
        )


    st.markdown("---")


    if event_counts:

        event_df = pd.DataFrame(
            {
                "Events":
                    event_counts
            }
        )


        st.subheader(
            "📊 Event Distribution"
        )


        st.bar_chart(
            event_df
        )


    events = event_data.get(
        "events",
        []
    )


    if events:

        st.subheader(
            "📋 Detected Events"
        )


        event_rows = []


        for event in events:

            event_rows.append(
                {
                    "Player":
                        event.get(
                            "player_id",
                            "-"
                        ),

                    "Event Type":
                        event.get(
                            "event_type",
                            "-"
                        ),

                    "Speed":
                        event.get(
                            "maximum_speed_kmh",
                            "-"
                        )
                }
            )


        st.dataframe(
            pd.DataFrame(
                event_rows
            ),
            width="stretch",
            hide_index=True
        )


    st.info(
        "Events are potential/estimated movement "
        "events and should not be treated as confirmed "
        "real-world football events."
    )


# ============================================================
# CAMERA MOTION
# ============================================================

elif selected_page == "📹 Camera Motion":

    st.header(
        "📹 Camera Motion Analysis"
    )


    summary = camera_data.get(
        "summary",
        match_camera
    )


    average_translation = safe_float(
        summary.get(
            "average_translation_pixels",
            0
        )
    )


    maximum_translation = safe_float(
        summary.get(
            "maximum_translation_pixels",
            0
        )
    )


    average_rotation = safe_float(
        summary.get(
            "average_rotation_degrees",
            0
        )
    )


    maximum_rotation = safe_float(
        summary.get(
            "maximum_rotation_degrees",
            0
        )
    )


    moving_frames = safe_int(
        summary.get(
            "moving_frames",
            0
        )
    )


    stable_frames = safe_int(
        summary.get(
            "stable_frames",
            0
        )
    )


    col1, col2 = (
        st.columns(2)
    )


    with col1:

        st.metric(
            "Average Movement",
            f"{average_translation:.2f} px"
        )

        st.metric(
            "Maximum Movement",
            f"{maximum_translation:.2f} px"
        )


    with col2:

        st.metric(
            "Average Rotation",
            f"{average_rotation:.4f}°"
        )

        st.metric(
            "Maximum Rotation",
            f"{maximum_rotation:.4f}°"
        )


    camera_frames = pd.DataFrame(
        {
            "Frames": [
                moving_frames,
                stable_frames
            ]
        },

        index=[
            "Moving",
            "Stable"
        ]
    )


    st.subheader(
        "🎥 Camera Stability"
    )


    st.bar_chart(
        camera_frames
    )


    motion_counts = summary.get(
        "motion_counts",
        {}
    )


    if motion_counts:

        st.subheader(
            "Camera Motion Types"
        )


        motion_df = pd.DataFrame(
            {
                "Frames":
                    motion_counts
            }
        )


        st.bar_chart(
            motion_df
        )


# ============================================================
# FIELD CALIBRATION
# ============================================================

elif selected_page == "📐 Field Calibration":

    st.header(
        "📐 Field & Dynamic Calibration"
    )


    calibration_summary = (
        dynamic_calibration_data.get(
            "summary",
            {}
        )
    )


    homography_frames = safe_int(
        calibration_summary.get(
            "homography_frames",
            match_calibration.get(
                "homography_frames",
                0
            )
        )
    )


    camera_frames = safe_int(
        calibration_summary.get(
            "camera_motion_frames",
            match_calibration.get(
                "camera_motion_frames",
                0
            )
        )
    )


    positions = safe_int(
        calibration_summary.get(
            "total_player_positions",
            match_calibration.get(
                "total_player_positions",
                0
            )
        )
    )


    reliable = safe_int(
        calibration_summary.get(
            "reliable_camera_matches",
            match_calibration.get(
                "reliable_camera_matches",
                0
            )
        )
    )


    unreliable = safe_int(
        calibration_summary.get(
            "unreliable_camera_matches",
            match_calibration.get(
                "unreliable_camera_matches",
                0
            )
        )
    )


    total_matches = (
        reliable +
        unreliable
    )


    if total_matches > 0:

        reliability = (
            reliable /
            total_matches
        ) * 100

    else:

        reliability = 0


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "Homography Frames",
            homography_frames
        )


    with col2:

        st.metric(
            "Camera Motion Frames",
            camera_frames
        )


    with col3:

        st.metric(
            "Player Positions",
            positions
        )


    col4, col5, col6 = (
        st.columns(3)
    )


    with col4:

        st.metric(
            "Reliable Matches",
            reliable
        )


    with col5:

        st.metric(
            "Unreliable Matches",
            unreliable
        )


    with col6:

        st.metric(
            "Reliability",
            f"{reliability:.2f}%"
        )


    st.subheader(
        "📊 Calibration Reliability"
    )


    st.progress(
        min(
            max(
                reliability / 100,
                0
            ),
            1
        )
    )


    # Pitch calibration file

    if pitch_calibration_data:

        st.subheader(
            "📐 Pitch Calibration"
        )


        st.json(
            pitch_calibration_data
        )


    st.warning(
        "The current dynamic calibration aligns "
        "camera-motion information with homography "
        "positions. It does not recompute a "
        "frame-specific homography for every frame."
    )


# ============================================================
# PLAYER RANKING
# ============================================================

elif selected_page == "🏆 Player Ranking":

    st.header(
        "🏆 Player Ranking"
    )


    ranking_rows = []


    if isinstance(
        ranking_data,
        list
    ):

        for index, player in enumerate(
            ranking_data,
            start=1
        ):

            if isinstance(
                player,
                dict
            ):

                ranking_rows.append(
                    {
                        "Rank":
                            index,

                        "Player":
                            player.get(
                                "player_id",
                                player.get(
                                    "id",
                                    "-"
                                )
                            ),

                        "Score":
                            safe_float(
                                player.get(
                                    "performance_score",
                                    player.get(
                                        "score",
                                        0
                                    )
                                )
                            )
                    }
                )


    elif isinstance(
        ranking_data,
        dict
    ):

        ranking_list = ranking_data.get(
            "ranking",
            ranking_data.get(
                "players",
                []
            )
        )


        if isinstance(
            ranking_list,
            list
        ):

            for index, player in enumerate(
                ranking_list,
                start=1
            ):

                if isinstance(
                    player,
                    dict
                ):

                    ranking_rows.append(
                        {
                            "Rank":
                                index,

                            "Player":
                                player.get(
                                    "player_id",
                                    player.get(
                                        "id",
                                        "-"
                                    )
                                ),

                            "Score":
                                safe_float(
                                    player.get(
                                        "performance_score",
                                        player.get(
                                            "score",
                                            0
                                        )
                                    )
                                )
                        }
                    )


    # fallback

    if not ranking_rows:

        for player_id in player_ids:

            ranking_rows.append(
                {
                    "Player":
                        player_id,

                    "Score":
                        get_player_performance(
                            player_id
                        )
                }
            )


        ranking_rows = sorted(
            ranking_rows,
            key=lambda x:
                x["Score"],
            reverse=True
        )


        for index, row in enumerate(
            ranking_rows,
            start=1
        ):

            row["Rank"] = index


    ranking_df = pd.DataFrame(
        ranking_rows
    )


    st.dataframe(
        ranking_df,
        width="stretch",
        hide_index=True
    )


# ============================================================
# AI INSIGHTS
# ============================================================

elif selected_page == "🤖 AI Insights":

    st.header(
        "🤖 AI Performance Insights"
    )


    if not player_ids:

        st.warning(
            "No players available."
        )

    else:

        selected_player = st.selectbox(
            "Select Player",
            player_ids,
            key="ai_player"
        )


        ai_player = get_player_ai(
            selected_player
        )


        if ai_player:

            st.json(
                ai_player
            )

        else:

            st.info(
                "AI insight data is not available "
                "for this player."
            )


# ============================================================
# NUTRITION
# ============================================================

elif selected_page == "🥗 Nutrition":

    st.header(
        "🥗 Nutrition & Recovery"
    )


    if not player_ids:

        st.warning(
            "No players available."
        )

    else:

        selected_player = st.selectbox(
            "Select Player",
            player_ids,
            key="nutrition_player"
        )


        nutrition = get_player_nutrition(
            selected_player
        )


        if nutrition:

            st.json(
                nutrition
            )

            st.caption(
                "Nutrition recommendations are general "
                "sports-nutrition guidance and not medical advice."
            )

        else:

            st.info(
                "Nutrition data unavailable."
            )


# ============================================================
# PLAYER COMPARISON
# ============================================================

elif selected_page == "🔍 Player Comparison":

    st.header(
        "🔍 Player Comparison"
    )


    if len(player_ids) < 2:

        st.warning(
            "At least two players are required."
        )

    else:

        col1, col2 = (
            st.columns(2)
        )


        with col1:

            player_a = st.selectbox(
                "Player A",
                player_ids,
                key="comparison_a"
            )


        with col2:

            player_b = st.selectbox(
                "Player B",
                player_ids,
                index=
                1
                if player_a != player_ids[1]
                else 0,
                key="comparison_b"
            )


        if player_a == player_b:

            st.warning(
                "Select two different players."
            )

        else:

            speed_a, max_a, _ = (
                get_player_speed(
                    player_a
                )
            )


            speed_b, max_b, _ = (
                get_player_speed(
                    player_b
                )
            )


            accel_a = get_player_acceleration(
                player_a
            )


            accel_b = get_player_acceleration(
                player_b
            )


            zone_a = get_player_zone(
                player_a
            )


            zone_b = get_player_zone(
                player_b
            )


            comparison_df = pd.DataFrame(
                {
                    f"Player {player_a}": [

                        get_player_performance(
                            player_a
                        ),

                        get_player_movement(
                            player_a
                        ),

                        speed_a,

                        max_a,

                        accel_a[
                            "average_acceleration"
                        ],

                        zone_a[
                            "attacking"
                        ],

                        get_ball_interactions(
                            player_a
                        )
                    ],


                    f"Player {player_b}": [

                        get_player_performance(
                            player_b
                        ),

                        get_player_movement(
                            player_b
                        ),

                        speed_b,

                        max_b,

                        accel_b[
                            "average_acceleration"
                        ],

                        zone_b[
                            "attacking"
                        ],

                        get_ball_interactions(
                            player_b
                        )
                    ]
                },

                index=[

                    "Performance Score",

                    "Movement",

                    "Average Speed",

                    "Maximum Speed",

                    "Average Acceleration",

                    "Attacking Zone %",

                    "Ball Interactions"
                ]
            )


            st.dataframe(
                comparison_df,
                width="stretch"
            )


            st.subheader(
                "📊 Comparison Chart"
            )


            st.bar_chart(
                comparison_df
            )


# ============================================================
# MATCH REPORT
# ============================================================

elif selected_page == "📄 Match Report":

    st.header(
        "📄 SPORTFLASH Match Report"
    )


    if not match_report_data:

        st.error(
            "match_report.json not found."
        )

    else:

        col1, col2, col3, col4 = (
            st.columns(4)
        )


        with col1:

            st.metric(
                "Players Analysed",
                safe_int(
                    match_movement.get(
                        "players_analysed",
                        0
                    )
                )
            )


        with col2:

            st.metric(
                "Team A",
                safe_int(
                    match_team.get(
                        "team_a_count",
                        0
                    )
                )
            )


        with col3:

            st.metric(
                "Team B",
                safe_int(
                    match_team.get(
                        "team_b_count",
                        0
                    )
                )
            )


        with col4:

            st.metric(
                "Potential Events",
                safe_int(
                    match_events.get(
                        "total_events",
                        0
                    )
                )
            )


        st.markdown("---")


        st.subheader(
            "🏃 Movement Analysis"
        )


        top_distance = match_movement.get(
            "top_distance_player",
            {}
        )


        top_speed = match_movement.get(
            "top_maximum_speed_player",
            {}
        )


        top_average = match_movement.get(
            "top_average_speed_player",
            {}
        )


        col1, col2, col3 = (
            st.columns(3)
        )


        with col1:

            st.metric(
                "Highest Estimated Distance",
                f"Player {top_distance.get('player_id', '-')}"
            )

            st.write(
                f"{safe_float(top_distance.get('total_distance_m', 0)):.2f} m"
            )


        with col2:

            st.metric(
                "Highest Estimated Max Speed",
                f"Player {top_speed.get('player_id', '-')}"
            )

            st.write(
                f"{safe_float(top_speed.get('maximum_speed_kmh', 0)):.2f} km/h"
            )


        with col3:

            st.metric(
                "Highest Estimated Average Speed",
                f"Player {top_average.get('player_id', '-')}"
            )

            st.write(
                f"{safe_float(top_average.get('average_speed_kmh', 0)):.2f} km/h"
            )


        st.markdown("---")


        st.subheader(
            "🎯 Event Analysis"
        )


        event_counts = match_events.get(
            "event_counts",
            {}
        )


        if event_counts:

            st.bar_chart(
                pd.DataFrame(
                    {
                        "Events":
                            event_counts
                    }
                )
            )


        st.markdown("---")


        st.subheader(
            "📹 Camera Analysis"
        )


        camera_table = pd.DataFrame(
            [
                {
                    "Metric":
                        "Average Translation",

                    "Value":
                        f"{safe_float(match_camera.get('average_translation_pixels', 0)):.2f} px"
                },

                {
                    "Metric":
                        "Maximum Translation",

                    "Value":
                        f"{safe_float(match_camera.get('maximum_translation_pixels', 0)):.2f} px"
                },

                {
                    "Metric":
                        "Average Rotation",

                    "Value":
                        f"{safe_float(match_camera.get('average_rotation_degrees', 0)):.4f}°"
                },

                {
                    "Metric":
                        "Maximum Rotation",

                    "Value":
                        f"{safe_float(match_camera.get('maximum_rotation_degrees', 0)):.4f}°"
                }
            ]
        )


        st.dataframe(
            camera_table,
            width="stretch",
            hide_index=True
        )


        st.markdown("---")


        st.subheader(
            "📐 Calibration"
        )


        st.metric(
            "Calibration Reliability",
            f"{safe_float(match_calibration.get('reliability_percent', 0)):.2f}%"
        )


        st.warning(
            match_report_data.get(
                "warning",
                "Distance, speed and movement events "
                "are estimated analytics."
            )
        )


        st.download_button(
            "⬇️ Download Match Report JSON",

            data=json.dumps(
                match_report_data,
                indent=2
            ),

            file_name=
            "SPORTFLASH_match_report.json",

            mime=
            "application/json"
        )


# ============================================================
# DATA STATUS
# ============================================================

elif selected_page == "📊 Data Status":

    st.header(
        "📊 SPORTFLASH Data Status"
    )


    files = {

        "Performance":
            PERFORMANCE_FILE,

        "Movement":
            MOVEMENT_FILE,

        "Speed":
            SPEED_FILE,

        "Acceleration":
            ACCELERATION_FILE,

        "Field Zones":
            ZONE_FILE,

        "Ball":
            BALL_FILE,

        "AI Insights":
            AI_FILE,

        "Nutrition":
            NUTRITION_FILE,

        "Ranking":
            RANKING_FILE,

        "Team Analysis":
            TEAM_FILE,

        "Tracking":
            TRACKING_FILE,

        "Team Classification":
            TEAM_CLASSIFICATION_FILE,

        "Team A Heatmap":
            TEAM_A_HEATMAP_FILE,

        "Team B Heatmap":
            TEAM_B_HEATMAP_FILE,

        "Pitch Calibration":
            PITCH_CALIBRATION_FILE,

        "Homography":
            HOMOGRAPHY_FILE,

        "Distance Analysis":
            DISTANCE_FILE,

        "Camera Motion":
            CAMERA_FILE,

        "Dynamic Calibration":
            DYNAMIC_CALIBRATION_FILE,

        "Dynamic Distance":
            DYNAMIC_DISTANCE_FILE,

        "Event Detection":
            EVENT_FILE,

        "Match Report":
            MATCH_REPORT_FILE,

        "Football Video":
            VIDEO_FILE
    }


    rows = []


    for name, path in files.items():

        available = file_available(
            path
        )


        if available:

            try:

                size = (
                    os.path.getsize(
                        path
                    )
                    /
                    1024
                )

                size_text = (
                    f"{size:.1f} KB"
                )

            except:

                size_text = "-"

        else:

            size_text = "-"


        rows.append(
            {
                "Module":
                    name,

                "Status":
                    "✅ Available"
                    if available
                    else "❌ Missing",

                "File":
                    path,

                "Size":
                    size_text
            }
        )


    status_df = pd.DataFrame(
        rows
    )


    st.dataframe(
        status_df,
        width="stretch",
        hide_index=True
    )


    available = sum(
        file_available(
            path
        )
        for path in files.values()
    )


    total = len(
        files
    )


    st.metric(
        "Available Files",
        f"{available}/{total}"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "SPORTFLASH AI | Football Performance Analytics | "
    "Computer Vision + Player Tracking + Calibration + "
    "Movement Intelligence"
)