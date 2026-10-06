import streamlit as st
import json
import os
import pandas as pd


# ============================================================
# SPORTFLASH - AI FOOTBALL PERFORMANCE ANALYTICS DASHBOARD
# ============================================================

st.set_page_config(
    page_title="SPORTFLASH",
    page_icon="⚽",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

RESULTS_DIR = "results"

HEATMAP_DIR = os.path.join(
    RESULTS_DIR,
    "heatmaps"
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

# NEW
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
# LOAD ALL DATA
# ============================================================

performance_data = load_json(PERFORMANCE_FILE)

movement_data = load_json(MOVEMENT_FILE)

speed_data = load_json(SPEED_FILE)

# NEW
acceleration_data = load_json(
    ACCELERATION_FILE
)

zone_data = load_json(ZONE_FILE)

ball_data = load_json(BALL_FILE)

ai_data = load_json(AI_FILE)

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
# HELPER FUNCTIONS
# ============================================================

def safe_float(value, default=0.0):

    try:
        return float(value)

    except:
        return default


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

    if isinstance(data, (int, float)):

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

    if isinstance(data, (int, float)):

        return float(data)

    return 0.0


def get_player_speed(player_id):

    data = speed_data.get(
        str(player_id),
        {}
    )

    if not isinstance(data, dict):

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

    return average, maximum, unit


# ============================================================
# NEW - ACCELERATION FUNCTION
# ============================================================

def get_player_acceleration(player_id):

    data = acceleration_data.get(
        str(player_id),
        {}
    )

    if not isinstance(data, dict):
        return {
            "average_acceleration": 0.0,
            "maximum_acceleration": 0.0,
            "average_deceleration": 0.0,
            "maximum_deceleration": 0.0,
            "acceleration_events": 0,
            "deceleration_events": 0,
            "unit": "pixels/sec²"
        }

    average_acceleration = safe_float(
        data.get(
            "average_acceleration",
            data.get(
                "average_acceleration_pixels_per_second_squared",
                data.get(
                    "avg_acceleration",
                    0
                )
            )
        )
    )

    maximum_acceleration = safe_float(
        data.get(
            "maximum_acceleration",
            data.get(
                "maximum_acceleration_pixels_per_second_squared",
                data.get(
                    "max_acceleration",
                    0
                )
            )
        )
    )

    average_deceleration = safe_float(
        data.get(
            "average_deceleration",
            data.get(
                "average_deceleration_pixels_per_second_squared",
                data.get(
                    "avg_deceleration",
                    0
                )
            )
        )
    )

    maximum_deceleration = safe_float(
        data.get(
            "maximum_deceleration",
            data.get(
                "maximum_deceleration_pixels_per_second_squared",
                data.get(
                    "max_deceleration",
                    0
                )
            )
        )
    )

    acceleration_events = data.get(
        "acceleration_events",
        data.get(
            "number_of_acceleration_events",
            0
        )
    )

    deceleration_events = data.get(
        "deceleration_events",
        data.get(
            "number_of_deceleration_events",
            0
        )
    )

    return {
        "average_acceleration":
            average_acceleration,

        "maximum_acceleration":
            maximum_acceleration,

        "average_deceleration":
            average_deceleration,

        "maximum_deceleration":
            maximum_deceleration,

        "acceleration_events":
            acceleration_events,

        "deceleration_events":
            deceleration_events,

        "unit":
            data.get(
                "unit",
                "pixels/sec²"
            )
    }


# ============================================================
# FIELD ZONE FUNCTION
# ============================================================

def get_player_zone(player_id):

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
        "defensive": safe_float(
            data.get(
                "defensive",
                0
            )
        ),

        "midfield": safe_float(
            data.get(
                "midfield",
                0
            )
        ),

        "attacking": safe_float(
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

    return int(
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

    if isinstance(data, dict):
        return data

    return {}


def get_player_nutrition(player_id):

    data = nutrition_data.get(
        str(player_id),
        {}
    )

    if isinstance(data, dict):
        return data

    return {}


# ============================================================
# FIND PLAYERS
# ============================================================

player_ids = set()

for player_id in performance_data.keys():
    player_ids.add(str(player_id))

for player_id in movement_data.keys():
    player_ids.add(str(player_id))

for player_id in speed_data.keys():
    player_ids.add(str(player_id))

for player_id in acceleration_data.keys():
    player_ids.add(str(player_id))

for player_id in zone_data.keys():
    player_ids.add(str(player_id))


player_ids = sorted(
    player_ids,
    key=lambda x: int(x)
    if x.isdigit()
    else 999999
)


# ============================================================
# HEADER
# ============================================================

st.title("⚽ SPORTFLASH")

st.subheader(
    "AI-Based Football Performance Analytics"
)

st.write(
    "Analyze player movement, speed, acceleration, "
    "field zones, ball interaction, performance, "
    "AI insights and nutrition recommendations."
)

st.markdown("---")


# ============================================================
# CHECK DATA
# ============================================================

if not player_ids:

    st.error(
        "No player data found."
    )

    st.info(
        "Run the SPORTFLASH analysis scripts first."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚽ SPORTFLASH"
)

st.sidebar.write(
    "Player Analytics"
)

selected_player = st.sidebar.selectbox(
    "Select Player",
    player_ids
)

st.sidebar.markdown("---")

st.sidebar.write(
    "Available Modules"
)

st.sidebar.write("✅ Player Detection")
st.sidebar.write("✅ Player Tracking")
st.sidebar.write("✅ Movement Analysis")
st.sidebar.write("✅ Speed Analysis")
st.sidebar.write("✅ Acceleration Analysis")
st.sidebar.write("✅ Deceleration Analysis")
st.sidebar.write("✅ Heatmap")
st.sidebar.write("✅ Field Zone Analysis")
st.sidebar.write("✅ Ball Analysis")
st.sidebar.write("✅ Performance Score")
st.sidebar.write("✅ Player Ranking")
st.sidebar.write("✅ AI Insights")
st.sidebar.write("✅ Nutrition")
st.sidebar.write("✅ Team Analysis")
st.sidebar.write("✅ Player Comparison")


# ============================================================
# SELECTED PLAYER DATA
# ============================================================

performance_score = get_player_performance(
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

ball_interactions = get_ball_interactions(
    selected_player
)

ai_player = get_player_ai(
    selected_player
)

nutrition_player = get_player_nutrition(
    selected_player
)


# ============================================================
# PERFORMANCE LEVEL
# ============================================================

if performance_score >= 80:

    performance_level = "Excellent"

elif performance_score >= 60:

    performance_level = "Good"

elif performance_score >= 40:

    performance_level = "Average"

else:

    performance_level = "Needs Improvement"


# ============================================================
# PLAYER OVERVIEW
# ============================================================

st.header(
    f"👤 Player {selected_player} Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Performance Score",
        f"{performance_score:.2f}/100"
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
        "Maximum Speed",
        f"{maximum_speed:.2f}"
    )

st.info(
    f"Performance Level: **{performance_level}**"
)


# ============================================================
# PERFORMANCE CHART
# ============================================================

st.header(
    "📊 Performance Metrics"
)

performance_chart = pd.DataFrame(
    {
        "Metric": [
            "Performance",
            "Average Speed",
            "Maximum Speed",
            "Movement",
            "Ball Interactions"
        ],

        "Value": [
            performance_score,
            average_speed,
            maximum_speed,
            movement,
            ball_interactions
        ]
    }
)

st.bar_chart(
    performance_chart.set_index("Metric")
)

st.caption(
    f"Speed values are reported as {speed_unit}. "
    "If the value is pixels/sec, field calibration is still "
    "required for real-world speed."
)


# ============================================================
# MOVEMENT ANALYSIS
# ============================================================

st.markdown("---")

st.header(
    "🏃 Movement Analysis"
)

movement_col1, movement_col2 = st.columns(2)

with movement_col1:

    st.metric(
        "Total Movement",
        f"{movement:.2f}"
    )

with movement_col2:

    if movement >= 4000:

        activity = "Very High"

    elif movement >= 2500:

        activity = "High"

    elif movement >= 1000:

        activity = "Moderate"

    else:

        activity = "Low"

    st.metric(
        "Activity Level",
        activity
    )


# ============================================================
# SPEED ANALYSIS
# ============================================================

st.header(
    "⚡ Speed Analysis"
)

speed_col1, speed_col2 = st.columns(2)

with speed_col1:

    st.metric(
        "Average Speed",
        f"{average_speed:.2f} {speed_unit}"
    )

with speed_col2:

    st.metric(
        "Maximum Speed",
        f"{maximum_speed:.2f} {speed_unit}"
    )


# ============================================================
# ACCELERATION & DECELERATION
# ============================================================

st.markdown("---")

st.header(
    "🚀 Acceleration & Deceleration Analysis"
)

accel_unit = acceleration["unit"]

accel_col1, accel_col2 = st.columns(2)

with accel_col1:

    st.metric(
        "Average Acceleration",
        f"{acceleration['average_acceleration']:.2f} {accel_unit}"
    )

with accel_col2:

    st.metric(
        "Maximum Acceleration",
        f"{acceleration['maximum_acceleration']:.2f} {accel_unit}"
    )


decel_col1, decel_col2 = st.columns(2)

with decel_col1:

    st.metric(
        "Average Deceleration",
        f"{acceleration['average_deceleration']:.2f} {accel_unit}"
    )

with decel_col2:

    st.metric(
        "Maximum Deceleration",
        f"{acceleration['maximum_deceleration']:.2f} {accel_unit}"
    )


event_col1, event_col2 = st.columns(2)

with event_col1:

    st.metric(
        "Acceleration Events",
        acceleration["acceleration_events"]
    )

with event_col2:

    st.metric(
        "Deceleration Events",
        acceleration["deceleration_events"]
    )


acceleration_chart = pd.DataFrame(
    {
        "Metric": [
            "Average Acceleration",
            "Maximum Acceleration",
            "Average Deceleration",
            "Maximum Deceleration"
        ],

        "Value": [
            acceleration["average_acceleration"],
            acceleration["maximum_acceleration"],
            acceleration["average_deceleration"],
            acceleration["maximum_deceleration"]
        ]
    }
)

st.bar_chart(
    acceleration_chart.set_index(
        "Metric"
    )
)

st.caption(
    "Acceleration values are displayed using the units "
    "provided by the acceleration analysis. Pixel-based "
    "values require field calibration for real-world units."
)


# ============================================================
# HEATMAP
# ============================================================

st.markdown("---")

st.header(
    "🔥 Player Movement Heatmap"
)

heatmap_path = os.path.join(
    HEATMAP_DIR,
    f"player_{selected_player}_heatmap.png"
)

if os.path.exists(heatmap_path):

    st.image(
        heatmap_path,
        caption=f"Player {selected_player} Movement Heatmap",
        width="stretch"
    )

else:

    st.warning(
        f"Heatmap for Player {selected_player} not found."
    )


# ============================================================
# FIELD ZONE ANALYSIS
# ============================================================

st.markdown("---")

st.header(
    "🗺️ Field Zone Analysis"
)

st.write(
    f"Movement distribution of Player {selected_player} "
    "across defensive, midfield and attacking zones."
)

zone_col1, zone_col2, zone_col3 = st.columns(3)

with zone_col1:

    st.metric(
        "🛡️ Defensive",
        f"{zones['defensive']:.1f}%"
    )

with zone_col2:

    st.metric(
        "⚽ Midfield",
        f"{zones['midfield']:.1f}%"
    )

with zone_col3:

    st.metric(
        "🎯 Attacking",
        f"{zones['attacking']:.1f}%"
    )


zone_chart = pd.DataFrame(
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

st.bar_chart(
    zone_chart.set_index("Zone")
)


dominant_zone = max(
    zones,
    key=zones.get
)

st.info(
    f"Dominant field zone: "
    f"**{dominant_zone.title()}**"
)


# ============================================================
# BALL ANALYSIS
# ============================================================

st.markdown("---")

st.header(
    "⚽ Ball Analysis"
)

ball_col1, ball_col2 = st.columns(2)

with ball_col1:

    st.metric(
        "Player-Ball Interactions",
        ball_interactions
    )

with ball_col2:

    total_interactions = ball_data.get(
        "total_player_ball_interactions",
        0
    )

    st.metric(
        "Team Ball Interactions",
        total_interactions
    )


ball_speed = safe_float(
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


ball_speed_col1, ball_speed_col2 = st.columns(2)

with ball_speed_col1:

    st.metric(
        "Average Ball Speed",
        f"{ball_speed:.2f} pixels/sec"
    )

with ball_speed_col2:

    st.metric(
        "Maximum Ball Speed",
        f"{maximum_ball_speed:.2f} pixels/sec"
    )

st.caption(
    "Ball speed is currently displayed in pixels/sec. "
    "Real-world ball speed requires proper field calibration."
)


# ============================================================
# AI INSIGHTS
# ============================================================

st.markdown("---")

st.header(
    "🤖 AI Performance Insights"
)

if ai_player:

    level = ai_player.get(
        "performance_level",
        performance_level
    )

    movement_analysis = ai_player.get(
        "movement_analysis",
        ""
    )

    speed_analysis = ai_player.get(
        "speed_analysis",
        ""
    )

    zone_analysis = ai_player.get(
        "dominant_zone",
        dominant_zone.title()
    )

    ball_analysis = ai_player.get(
        "ball_interaction_analysis",
        ""
    )

    recommendations = ai_player.get(
        "recommendations",
        []
    )

    st.success(
        f"Performance Level: **{level}**"
    )

    if movement_analysis:

        st.write(
            f"🏃 **Movement:** {movement_analysis}"
        )

    if speed_analysis:

        st.write(
            f"⚡ **Speed:** {speed_analysis}"
        )

    if zone_analysis:

        st.write(
            f"🗺️ **Zone:** {zone_analysis}"
        )

    if ball_analysis:

        st.write(
            f"⚽ **Ball:** {ball_analysis}"
        )

    if recommendations:

        st.subheader(
            "💡 Recommendations"
        )

        if isinstance(
            recommendations,
            list
        ):

            for recommendation in recommendations:

                st.write(
                    f"• {recommendation}"
                )

        else:

            st.write(
                recommendations
            )

else:

    st.info(
        "AI insight data not available for this player."
    )


# ============================================================
# NUTRITION
# ============================================================

st.markdown("---")

st.header(
    "🥗 Nutrition & Recovery"
)

if nutrition_player:

    activity_level = nutrition_player.get(
        "activity_level",
        "Not available"
    )

    dominant_nutrition_zone = nutrition_player.get(
        "dominant_zone",
        "Not available"
    )

    st.subheader(
        "📋 Activity Profile"
    )

    nutrition_col1, nutrition_col2 = st.columns(2)

    with nutrition_col1:

        st.write(
            f"**Activity Level:** {activity_level}"
        )

    with nutrition_col2:

        st.write(
            f"**Dominant Zone:** "
            f"{dominant_nutrition_zone}"
        )


    food_suggestions = nutrition_player.get(
        "food_suggestions",
        []
    )

    if food_suggestions:

        st.subheader(
            "🍌 Food Suggestions"
        )

        if isinstance(
            food_suggestions,
            list
        ):

            for food in food_suggestions:

                st.write(
                    f"• {food}"
                )

        else:

            st.write(
                food_suggestions
            )


    recovery_foods = nutrition_player.get(
        "recovery_foods",
        []
    )

    if recovery_foods:

        st.subheader(
            "🥛 Recovery Foods"
        )

        if isinstance(
            recovery_foods,
            list
        ):

            for food in recovery_foods:

                st.write(
                    f"• {food}"
                )

        else:

            st.write(
                recovery_foods
            )


    hydration = nutrition_player.get(
        "hydration",
        []
    )

    if hydration:

        st.subheader(
            "💧 Hydration"
        )

        if isinstance(
            hydration,
            list
        ):

            for item in hydration:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                hydration
            )


    recommendations = nutrition_player.get(
        "recommendations",
        []
    )

    if recommendations:

        st.subheader(
            "💡 Nutrition Recommendations"
        )

        if isinstance(
            recommendations,
            list
        ):

            for recommendation in recommendations:

                st.write(
                    f"• {recommendation}"
                )

        else:

            st.write(
                recommendations
            )


    position_note = nutrition_player.get(
        "position_note",
        ""
    )

    if position_note:

        st.info(
            f"⚽ {position_note}"
        )

    st.caption(
        "Nutrition suggestions are general sports-nutrition "
        "guidance and are not medical advice."
    )

else:

    st.info(
        "Nutrition data not available for this player."
    )


# ============================================================
# PLAYER RANKING
# ============================================================

st.markdown("---")

st.header(
    "🏆 Player Ranking"
)

ranking_list = []

if isinstance(
    ranking_data,
    list
):

    ranking_list = ranking_data

elif isinstance(
    ranking_data,
    dict
):

    if isinstance(
        ranking_data.get("ranking"),
        list
    ):

        ranking_list = ranking_data[
            "ranking"
        ]

    elif isinstance(
        ranking_data.get("players"),
        list
    ):

        ranking_list = ranking_data[
            "players"
        ]


if ranking_list:

    ranking_rows = []

    for index, player in enumerate(
        ranking_list,
        start=1
    ):

        if isinstance(
            player,
            dict
        ):

            pid = player.get(
                "player_id",
                player.get(
                    "id",
                    ""
                )
            )

            score = player.get(
                "performance_score",
                player.get(
                    "score",
                    0
                )
            )

            ranking_rows.append(
                {
                    "Rank": index,
                    "Player": f"Player {pid}",
                    "Performance Score":
                        safe_float(score)
                }
            )


    if ranking_rows:

        ranking_df = pd.DataFrame(
            ranking_rows
        )

        st.dataframe(
            ranking_df,
            width="stretch",
            hide_index=True
        )

else:

    ranking_rows = []

    for player_id in player_ids:

        ranking_rows.append(
            {
                "Player":
                    f"Player {player_id}",

                "Performance Score":
                    get_player_performance(
                        player_id
                    )
            }
        )


    ranking_df = pd.DataFrame(
        ranking_rows
    )

    ranking_df = ranking_df.sort_values(
        "Performance Score",
        ascending=False
    )

    ranking_df.insert(
        0,
        "Rank",
        range(
            1,
            len(ranking_df) + 1
        )
    )

    st.dataframe(
        ranking_df,
        width="stretch",
        hide_index=True
    )


# ============================================================
# TEAM ANALYSIS
# ============================================================

st.markdown("---")

st.header(
    "👥 Team Analysis"
)

if team_data:

    team_stats = team_data.get(
        "team_statistics",
        team_data
    )

    if isinstance(
        team_stats,
        dict
    ):

        team_col1, team_col2, team_col3, team_col4 = (
            st.columns(4)
        )

        number_players = team_stats.get(
            "number_of_players",
            team_stats.get(
                "num_players",
                len(player_ids)
            )
        )

        average_performance = team_stats.get(
            "average_performance",
            team_stats.get(
                "average_performance_score",
                0
            )
        )

        average_movement = team_stats.get(
            "average_movement",
            0
        )

        average_speed_team = team_stats.get(
            "average_speed",
            0
        )

        with team_col1:

            st.metric(
                "Players",
                number_players
            )

        with team_col2:

            st.metric(
                "Average Performance",
                f"{safe_float(average_performance):.2f}"
            )

        with team_col3:

            st.metric(
                "Average Movement",
                f"{safe_float(average_movement):.2f}"
            )

        with team_col4:

            st.metric(
                "Average Speed",
                f"{safe_float(average_speed_team):.2f}"
            )


    st.subheader(
        "🏆 Team Leaders"
    )

    best_player = team_data.get(
        "best_performer",
        team_data.get(
            "best_player",
            "Not available"
        )
    )

    fastest_player = team_data.get(
        "fastest_average_speed",
        team_data.get(
            "fastest_player",
            "Not available"
        )
    )

    most_active = team_data.get(
        "most_active",
        team_data.get(
            "most_active_player",
            "Not available"
        )
    )

    best_attacking = team_data.get(
        "best_attacking",
        team_data.get(
            "best_attacking_player",
            "Not available"
        )
    )

    best_defensive = team_data.get(
        "best_defensive",
        team_data.get(
            "best_defensive_player",
            "Not available"
        )
    )


    leader_col1, leader_col2, leader_col3 = (
        st.columns(3)
    )

    with leader_col1:

        st.write(
            f"🏆 **Best Performer:** "
            f"{best_player}"
        )

        st.write(
            f"⚡ **Fastest:** "
            f"{fastest_player}"
        )

    with leader_col2:

        st.write(
            f"🏃 **Most Active:** "
            f"{most_active}"
        )

        st.write(
            f"🎯 **Best Attacking:** "
            f"{best_attacking}"
        )

    with leader_col3:

        st.write(
            f"🛡️ **Best Defensive:** "
            f"{best_defensive}"
        )


    # --------------------------------------------------------
    # TEAM ZONES
    # --------------------------------------------------------

    st.subheader(
        "🗺️ Team Zone Distribution"
    )

    team_zone = team_data.get(
        "team_zone_distribution",
        team_data.get(
            "zone_distribution",
            {}
        )
    )

    if isinstance(
        team_zone,
        dict
    ) and team_zone:

        zone_names = []
        zone_values = []

        for name, value in team_zone.items():

            zone_names.append(
                str(name).title()
            )

            zone_values.append(
                safe_float(value)
            )


        team_zone_df = pd.DataFrame(
            {
                "Zone": zone_names,
                "Percentage": zone_values
            }
        )

        st.bar_chart(
            team_zone_df.set_index(
                "Zone"
            )
        )


    strengths = team_data.get(
        "team_strengths",
        team_data.get(
            "strengths",
            []
        )
    )

    if strengths:

        st.subheader(
            "💪 Team Strengths"
        )

        if isinstance(
            strengths,
            list
        ):

            for strength in strengths:

                st.write(
                    f"• {strength}"
                )

        else:

            st.write(
                strengths
            )


    weaknesses = team_data.get(
        "team_weaknesses",
        team_data.get(
            "weaknesses",
            []
        )
    )

    if weaknesses:

        st.subheader(
            "⚠️ Team Weaknesses"
        )

        if isinstance(
            weaknesses,
            list
        ):

            for weakness in weaknesses:

                st.write(
                    f"• {weakness}"
                )

        else:

            st.write(
                weaknesses
            )

else:

    st.info(
        "Team analysis data not available."
    )


# ============================================================
# PLAYER COMPARISON
# ============================================================

st.markdown("---")

st.header(
    "👥 Player Comparison"
)


if comparison_data:

    comparison_players = comparison_data.get(
        "players",
        {}
    )

else:

    comparison_players = {}


if not comparison_players:

    for player_id in player_ids:

        average_player_speed, maximum_player_speed, _ = (
            get_player_speed(
                player_id
            )
        )

        player_zone = get_player_zone(
            player_id
        )

        player_acceleration = get_player_acceleration(
            player_id
        )

        comparison_players[
            str(player_id)
        ] = {

            "player_id":
                str(player_id),

            "performance_score":
                round(
                    get_player_performance(
                        player_id
                    ),
                    2
                ),

            "movement":
                round(
                    get_player_movement(
                        player_id
                    ),
                    2
                ),

            "average_speed":
                round(
                    average_player_speed,
                    2
                ),

            "maximum_speed":
                round(
                    maximum_player_speed,
                    2
                ),

            # NEW
            "average_acceleration":
                round(
                    player_acceleration[
                        "average_acceleration"
                    ],
                    2
                ),

            # NEW
            "maximum_acceleration":
                round(
                    player_acceleration[
                        "maximum_acceleration"
                    ],
                    2
                ),

            "defensive":
                round(
                    player_zone[
                        "defensive"
                    ],
                    2
                ),

            "midfield":
                round(
                    player_zone[
                        "midfield"
                    ],
                    2
                ),

            "attacking":
                round(
                    player_zone[
                        "attacking"
                    ],
                    2
                ),

            "ball_interactions":
                get_ball_interactions(
                    player_id
                )
        }


comparison_player_ids = sorted(
    comparison_players.keys(),
    key=lambda x: int(x)
    if x.isdigit()
    else 999999
)


if len(comparison_player_ids) >= 2:

    comparison_col1, comparison_col2 = (
        st.columns(2)
    )

    with comparison_col1:

        player_a = st.selectbox(
            "Select Player A",
            comparison_player_ids,
            key="player_comparison_a"
        )

    with comparison_col2:

        default_index = 1

        if player_a == comparison_player_ids[1]:

            default_index = 0

        player_b = st.selectbox(
            "Select Player B",
            comparison_player_ids,
            index=default_index,
            key="player_comparison_b"
        )


    if player_a == player_b:

        st.warning(
            "Please select two different players."
        )

    else:

        data_a = comparison_players[
            player_a
        ]

        data_b = comparison_players[
            player_b
        ]


        st.subheader(
            f"Player {player_a} vs Player {player_b}"
        )


        comparison_table = pd.DataFrame(
            {
                "Metric": [

                    "Performance Score",
                    "Movement",
                    "Average Speed",
                    "Maximum Speed",
                    "Average Acceleration",
                    "Maximum Acceleration",
                    "Defensive %",
                    "Midfield %",
                    "Attacking %",
                    "Ball Interactions"

                ],

                f"Player {player_a}": [

                    data_a.get(
                        "performance_score",
                        0
                    ),

                    data_a.get(
                        "movement",
                        0
                    ),

                    data_a.get(
                        "average_speed",
                        0
                    ),

                    data_a.get(
                        "maximum_speed",
                        0
                    ),

                    data_a.get(
                        "average_acceleration",
                        0
                    ),

                    data_a.get(
                        "maximum_acceleration",
                        0
                    ),

                    data_a.get(
                        "defensive",
                        0
                    ),

                    data_a.get(
                        "midfield",
                        0
                    ),

                    data_a.get(
                        "attacking",
                        0
                    ),

                    data_a.get(
                        "ball_interactions",
                        0
                    )
                ],

                f"Player {player_b}": [

                    data_b.get(
                        "performance_score",
                        0
                    ),

                    data_b.get(
                        "movement",
                        0
                    ),

                    data_b.get(
                        "average_speed",
                        0
                    ),

                    data_b.get(
                        "maximum_speed",
                        0
                    ),

                    data_b.get(
                        "average_acceleration",
                        0
                    ),

                    data_b.get(
                        "maximum_acceleration",
                        0
                    ),

                    data_b.get(
                        "defensive",
                        0
                    ),

                    data_b.get(
                        "midfield",
                        0
                    ),

                    data_b.get(
                        "attacking",
                        0
                    ),

                    data_b.get(
                        "ball_interactions",
                        0
                    )
                ]
            }
        )


        st.dataframe(
            comparison_table,
            width="stretch",
            hide_index=True
        )


        st.subheader(
            "📊 Player Comparison Chart"
        )

        chart_data = pd.DataFrame(
            {
                f"Player {player_a}": [

                    data_a.get(
                        "performance_score",
                        0
                    ),

                    data_a.get(
                        "average_speed",
                        0
                    ),

                    data_a.get(
                        "average_acceleration",
                        0
                    ),

                    data_a.get(
                        "attacking",
                        0
                    ),

                    data_a.get(
                        "defensive",
                        0
                    ),

                    data_a.get(
                        "ball_interactions",
                        0
                    )
                ],

                f"Player {player_b}": [

                    data_b.get(
                        "performance_score",
                        0
                    ),

                    data_b.get(
                        "average_speed",
                        0
                    ),

                    data_b.get(
                        "average_acceleration",
                        0
                    ),

                    data_b.get(
                        "attacking",
                        0
                    ),

                    data_b.get(
                        "defensive",
                        0
                    ),

                    data_b.get(
                        "ball_interactions",
                        0
                    )
                ]
            },

            index=[

                "Performance",
                "Average Speed",
                "Average Acceleration",
                "Attacking",
                "Defensive",
                "Ball Interactions"

            ]
        )

        st.bar_chart(
            chart_data
        )


else:

    st.info(
        "At least two players are required for comparison."
    )


# ============================================================
# DATA STATUS
# ============================================================

st.markdown("---")

st.header(
    "📁 Analysis Data Status"
)

status_data = {

    "Performance":
        os.path.exists(PERFORMANCE_FILE),

    "Movement":
        os.path.exists(MOVEMENT_FILE),

    "Speed":
        os.path.exists(SPEED_FILE),

    "Acceleration":
        os.path.exists(ACCELERATION_FILE),

    "Field Zones":
        os.path.exists(ZONE_FILE),

    "Ball":
        os.path.exists(BALL_FILE),

    "AI Insights":
        os.path.exists(AI_FILE),

    "Nutrition":
        os.path.exists(NUTRITION_FILE),

    "Ranking":
        os.path.exists(RANKING_FILE),

    "Team Analysis":
        os.path.exists(TEAM_FILE)

}

status_rows = []

for name, available in status_data.items():

    status_rows.append(
        {
            "Module": name,
            "Status":
                "✅ Available"
                if available
                else "❌ Missing"
        }
    )

status_df = pd.DataFrame(
    status_rows
)

st.dataframe(
    status_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# PROJECT PIPELINE
# ============================================================

st.markdown("---")

st.header(
    "🚀 SPORTFLASH Project Pipeline"
)

pipeline = """

Video Input
    ↓
YOLO Player Detection & Tracking
    ↓
Movement Analysis
    ↓
Speed Analysis
    ↓
Speed Calibration
    ↓
Acceleration & Deceleration Analysis
    ↓
Heatmap
    ↓
Field Zone Analysis
    ↓
Ball Detection & Ball Speed
    ↓
Player-Ball Interaction
    ↓
Performance Score
    ↓
Player Ranking
    ↓
AI Performance Insights
    ↓
Nutrition Recommendations
    ↓
Team Analysis
    ↓
Player Comparison
    ↓
Streamlit Dashboard
"""

st.code(
    pipeline,
    language="text"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
### ⚽ SPORTFLASH

**AI-Based Football Performance Analytics**

Player Detection • Tracking • Movement • Speed •  
Acceleration • Deceleration • Heatmap • Field Zones •  
Ball Analysis • Performance Score • Ranking •  
AI Insights • Nutrition • Team Analysis • Player Comparison

---

*Prototype developed for AI Sports Performance Analytics.*
"""
)