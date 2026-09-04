import streamlit as st
import json
import os
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SPORTFLASH",
    page_icon="⚽",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("⚽ SPORTFLASH")
st.subheader("AI-Based Football Performance Analytics Dashboard")

st.markdown(
    """
    **Analyze player performance, movement, speed, field zones,
    ball interaction, AI insights, nutrition and team performance.**
    """
)

st.divider()


# ============================================================
# FILE PATHS
# ============================================================

RESULTS_DIR = "results"

PERFORMANCE_FILE = os.path.join(
    RESULTS_DIR,
    "performance_scores.json"
)

RANKING_FILE = os.path.join(
    RESULTS_DIR,
    "player_ranking.json"
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

AI_INSIGHTS_FILE = os.path.join(
    RESULTS_DIR,
    "ai_insights.json"
)

NUTRITION_FILE = os.path.join(
    RESULTS_DIR,
    "nutrition_recommendations.json"
)

TEAM_FILE = os.path.join(
    RESULTS_DIR,
    "team_analysis.json"
)


# ============================================================
# JSON LOADER
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
# LOAD DATA
# ============================================================

performance_data = load_json(
    PERFORMANCE_FILE
)

ranking_data = load_json(
    RANKING_FILE
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

ai_data = load_json(
    AI_INSIGHTS_FILE
)

nutrition_data = load_json(
    NUTRITION_FILE
)

team_data = load_json(
    TEAM_FILE
)


# ============================================================
# CHECK PERFORMANCE DATA
# ============================================================

if not performance_data:

    st.error(
        "Performance data not found."
    )

    st.info(
        "Run the analysis Python files first."
    )

    st.stop()


# ============================================================
# GET PLAYER IDs
# ============================================================

player_ids = list(
    performance_data.keys()
)


# Sort numerically where possible

try:

    player_ids = sorted(
        player_ids,
        key=lambda x: int(x)
    )

except:

    player_ids = sorted(
        player_ids
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚽ SPORTFLASH")

st.sidebar.markdown(
    "### Player Selection"
)

selected_player = st.sidebar.selectbox(
    "Select Player",
    player_ids
)


st.sidebar.divider()

st.sidebar.markdown(
    """
    ### Analysis Modules

    ✅ Player Detection  
    ✅ Player Tracking  
    ✅ Movement Analysis  
    ✅ Speed Analysis  
    ✅ Speed Calibration  
    ✅ Heatmap  
    ✅ Zone Analysis  
    ✅ Ball Analysis  
    ✅ Performance Score  
    ✅ Player Ranking  
    ✅ AI Insights  
    ✅ Nutrition  
    ✅ Team Analysis
    """
)


# ============================================================
# PLAYER DATA
# ============================================================

selected_performance = performance_data.get(
    selected_player,
    {}
)

selected_movement = movement_data.get(
    selected_player,
    0
)

selected_speed = speed_data.get(
    selected_player,
    {}
)

selected_zone = zone_data.get(
    selected_player,
    {}
)

selected_ai = ai_data.get(
    selected_player,
    {}
)

selected_nutrition = nutrition_data.get(
    selected_player,
    {}
)


# ============================================================
# PERFORMANCE SCORE
# ============================================================

if isinstance(
    selected_performance,
    dict
):

    performance_score = float(
        selected_performance.get(
            "performance_score",
            selected_performance.get(
                "score",
                0
            )
        )
    )

else:

    performance_score = float(
        selected_performance
    )


# ============================================================
# MOVEMENT
# ============================================================

if isinstance(
    selected_movement,
    dict
):

    movement_value = float(
        selected_movement.get(
            "total_distance",
            selected_movement.get(
                "movement",
                selected_movement.get(
                    "distance",
                    0
                )
            )
        )
    )

else:

    try:

        movement_value = float(
            selected_movement
        )

    except:

        movement_value = 0


# ============================================================
# SPEED
# ============================================================

if isinstance(
    selected_speed,
    dict
):

    average_speed = float(
        selected_speed.get(
            "average_speed",
            0
        )
    )

    maximum_speed = float(
        selected_speed.get(
            "maximum_speed",
            0
        )
    )

else:

    average_speed = 0
    maximum_speed = 0


# ============================================================
# ZONE
# ============================================================

if isinstance(
    selected_zone,
    dict
):

    defensive = float(
        selected_zone.get(
            "defensive",
            0
        )
    )

    midfield = float(
        selected_zone.get(
            "midfield",
            0
        )
    )

    attacking = float(
        selected_zone.get(
            "attacking",
            0
        )
    )

else:

    defensive = 0
    midfield = 0
    attacking = 0


# ============================================================
# DOMINANT ZONE
# ============================================================

zone_values = {

    "Defensive": defensive,

    "Midfield": midfield,

    "Attacking": attacking

}

dominant_zone = max(
    zone_values,
    key=zone_values.get
)


# ============================================================
# PLAYER PERFORMANCE HEADER
# ============================================================

st.header(
    f"👤 Player {selected_player} Performance"
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Performance Score",
        f"{performance_score:.2f}/100"
    )


with col2:

    st.metric(
        "Movement",
        f"{movement_value:.2f}"
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


# ============================================================
# PERFORMANCE LEVEL
# ============================================================

if performance_score >= 80:

    performance_level = "Excellent 🟢"

elif performance_score >= 60:

    performance_level = "Good 🟢"

elif performance_score >= 40:

    performance_level = "Average 🟡"

else:

    performance_level = "Needs Improvement 🔴"


st.info(
    f"**Performance Level:** {performance_level}"
)


# ============================================================
# PLAYER RANK
# ============================================================

st.subheader("🏆 Player Ranking")


player_rank = "N/A"


if ranking_data:

    # Handle different possible ranking formats

    if isinstance(
        ranking_data,
        list
    ):

        for index, item in enumerate(
            ranking_data,
            start=1
        ):

            if isinstance(
                item,
                dict
            ):

                pid = str(
                    item.get(
                        "player_id",
                        ""
                    )
                )

                if pid == str(
                    selected_player
                ):

                    player_rank = index

                    break

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

            for index, item in enumerate(
                ranking_list,
                start=1
            ):

                if isinstance(
                    item,
                    dict
                ):

                    pid = str(
                        item.get(
                            "player_id",
                            ""
                        )
                    )

                    if pid == str(
                        selected_player
                    ):

                        player_rank = index

                        break


st.metric(
    "Player Rank",
    player_rank
)


# ============================================================
# PERFORMANCE CHART
# ============================================================

st.subheader(
    "📊 Player Performance Metrics"
)


chart_data = pd.DataFrame(
    {
        "Metric": [
            "Performance Score",
            "Movement",
            "Average Speed",
            "Maximum Speed"
        ],

        "Value": [
            performance_score,
            movement_value,
            average_speed,
            maximum_speed
        ]
    }
)


st.bar_chart(
    chart_data.set_index(
        "Metric"
    )
)


# ============================================================
# ZONE ANALYSIS
# ============================================================

st.divider()

st.header(
    "🗺️ Field Zone Analysis"
)


zone_col1, zone_col2, zone_col3 = st.columns(3)


with zone_col1:

    st.metric(
        "Defensive",
        f"{defensive:.1f}%"
    )


with zone_col2:

    st.metric(
        "Midfield",
        f"{midfield:.1f}%"
    )


with zone_col3:

    st.metric(
        "Attacking",
        f"{attacking:.1f}%"
    )


st.info(
    f"**Dominant Zone:** {dominant_zone}"
)


zone_chart = pd.DataFrame(
    {
        "Zone": [
            "Defensive",
            "Midfield",
            "Attacking"
        ],

        "Percentage": [
            defensive,
            midfield,
            attacking
        ]
    }
)


st.bar_chart(
    zone_chart.set_index(
        "Zone"
    )
)


# ============================================================
# HEATMAP
# ============================================================

st.divider()

st.header(
    "🔥 Player Movement Heatmap"
)


heatmap_file = os.path.join(
    RESULTS_DIR,
    "heatmaps",
    f"player_{selected_player}_heatmap.png"
)


if os.path.exists(
    heatmap_file
):

    st.image(
        heatmap_file,
        caption=
        f"Player {selected_player} Movement Heatmap",
        use_container_width=True
    )

else:

    st.warning(
        "Heatmap not available for this player."
    )


# ============================================================
# BALL ANALYSIS
# ============================================================

st.divider()

st.header(
    "⚽ Ball Analysis"
)


total_ball_interactions = ball_data.get(
    "total_player_ball_interactions",
    0
)

interaction_counts = ball_data.get(
    "interaction_counts",
    {}
)

player_ball_interactions = interaction_counts.get(
    selected_player,
    0
)

average_ball_speed = ball_data.get(
    "average_ball_speed_pixels_per_second",
    0
)

maximum_ball_speed = ball_data.get(
    "maximum_ball_speed_pixels_per_second",
    0
)


ball_col1, ball_col2, ball_col3 = st.columns(3)


with ball_col1:

    st.metric(
        "Player Ball Interactions",
        player_ball_interactions
    )


with ball_col2:

    st.metric(
        "Average Ball Speed",
        f"{average_ball_speed:.2f} px/s"
    )


with ball_col3:

    st.metric(
        "Maximum Ball Speed",
        f"{maximum_ball_speed:.2f} px/s"
    )


st.caption(
    "Ball speed is displayed in pixels/second unless "
    "field calibration is applied."
)


# ============================================================
# AI PERFORMANCE INSIGHTS
# ============================================================

st.divider()

st.header(
    "🤖 AI Performance Insights"
)


if selected_ai:

    if isinstance(
        selected_ai,
        dict
    ):

        ai_level = selected_ai.get(
            "performance_level",
            performance_level
        )

        st.subheader(
            "Performance Assessment"
        )

        st.write(
            ai_level
        )


        movement_analysis = selected_ai.get(
            "movement_analysis",
            ""
        )

        if movement_analysis:

            st.subheader(
                "🏃 Movement Analysis"
            )

            st.write(
                movement_analysis
            )


        speed_analysis = selected_ai.get(
            "speed_analysis",
            ""
        )

        if speed_analysis:

            st.subheader(
                "⚡ Speed Analysis"
            )

            st.write(
                speed_analysis
            )


        dominant_zone_ai = selected_ai.get(
            "dominant_zone",
            dominant_zone
        )

        st.subheader(
            "🗺️ Playing Area"
        )

        st.write(
            f"Player mainly operates in the **{dominant_zone_ai}** zone."
        )


        ball_analysis = selected_ai.get(
            "ball_interaction_analysis",
            ""
        )

        if ball_analysis:

            st.subheader(
                "⚽ Ball Interaction"
            )

            st.write(
                ball_analysis
            )


        recommendations = selected_ai.get(
            "recommendations",
            []
        )

        if recommendations:

            st.subheader(
                "💡 AI Recommendations"
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

    st.warning(
        "AI insights are not available."
    )


# ============================================================
# NUTRITION & RECOVERY
# ============================================================

st.divider()

st.header(
    "🥗 Nutrition & Recovery Recommendations"
)


if selected_nutrition:

    activity_level = selected_nutrition.get(
        "activity_level",
        "Not available"
    )

    nutrition_col1, nutrition_col2 = st.columns(2)


    with nutrition_col1:

        st.subheader(
            "Activity Profile"
        )

        st.write(
            f"**Activity Level:** {activity_level}"
        )

        st.write(
            f"**Performance Score:** "
            f"{performance_score:.2f}/100"
        )

        st.write(
            f"**Dominant Zone:** "
            f"{dominant_zone}"
        )


    with nutrition_col2:

        st.subheader(
            "Performance Data"
        )

        st.write(
            f"**Movement:** "
            f"{movement_value:.2f}"
        )

        st.write(
            f"**Average Speed:** "
            f"{average_speed:.2f}"
        )

        st.write(
            f"**Maximum Speed:** "
            f"{maximum_speed:.2f}"
        )


    # Food Suggestions

    food_suggestions = selected_nutrition.get(
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


    # Recovery Foods

    recovery_foods = selected_nutrition.get(
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


    # Hydration

    hydration = selected_nutrition.get(
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


    # Recommendations

    nutrition_recommendations = selected_nutrition.get(
        "recommendations",
        []
    )

    if nutrition_recommendations:

        st.subheader(
            "📋 Nutrition Recommendations"
        )

        if isinstance(
            nutrition_recommendations,
            list
        ):

            for recommendation in nutrition_recommendations:

                st.write(
                    f"• {recommendation}"
                )

        else:

            st.write(
                nutrition_recommendations
            )


    # Position Note

    position_note = selected_nutrition.get(
        "position_note",
        ""
    )

    if position_note:

        st.subheader(
            "⚽ Position Note"
        )

        st.write(
            position_note
        )


    st.caption(
        "Nutrition suggestions are general sports-nutrition "
        "guidance and are not medical advice."
    )

else:

    st.warning(
        "Nutrition recommendations are not available."
    )


# ============================================================
# TOP 5 PLAYERS
# ============================================================

st.divider()

st.header(
    "🏆 Top 5 Players"
)


top_players = []


for player_id, data in performance_data.items():

    if isinstance(
        data,
        dict
    ):

        score = float(
            data.get(
                "performance_score",
                data.get(
                    "score",
                    0
                )
            )
        )

    else:

        score = float(
            data
        )

    top_players.append(
        {
            "Player": f"Player {player_id}",
            "Performance Score": round(
                score,
                2
            )
        }
    )


top_players = sorted(
    top_players,
    key=lambda x:
        x["Performance Score"],
    reverse=True
)[:5]


top_df = pd.DataFrame(
    top_players
)


st.dataframe(
    top_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TEAM ANALYSIS
# ============================================================

st.divider()

st.header(
    "👥 Team Analysis"
)


if team_data:

    team_summary = team_data.get(
        "team_summary",
        {}
    )

    team_zone = team_data.get(
        "team_zone_distribution",
        {}
    )

    key_players = team_data.get(
        "key_players",
        {}
    )

    team_strengths = team_data.get(
        "team_strengths",
        []
    )

    team_weaknesses = team_data.get(
        "team_weaknesses",
        []
    )


    # --------------------------------------------------------
    # TEAM KPI CARDS
    # --------------------------------------------------------

    team_col1, team_col2, team_col3, team_col4 = st.columns(4)


    with team_col1:

        st.metric(
            "Players",
            team_summary.get(
                "number_of_players",
                0
            )
        )


    with team_col2:

        st.metric(
            "Average Performance",
            f"{team_summary.get(
                'average_performance_score',
                0
            ):.2f}/100"
        )


    with team_col3:

        st.metric(
            "Average Speed",
            f"{team_summary.get(
                'average_speed',
                0
            ):.2f}"
        )


    with team_col4:

        st.metric(
            "Ball Interactions",
            team_summary.get(
                "total_ball_interactions",
                0
            )
        )


    # --------------------------------------------------------
    # TEAM PERFORMANCE LEVEL
    # --------------------------------------------------------

    team_level = team_summary.get(
        "performance_level",
        "Not available"
    )

    st.info(
        f"**Team Performance Level:** {team_level}"
    )


    # --------------------------------------------------------
    # TEAM ZONE DISTRIBUTION
    # --------------------------------------------------------

    st.subheader(
        "🗺️ Team Zone Distribution"
    )


    team_defensive = float(
        team_zone.get(
            "defensive",
            0
        )
    )

    team_midfield = float(
        team_zone.get(
            "midfield",
            0
        )
    )

    team_attacking = float(
        team_zone.get(
            "attacking",
            0
        )
    )


    team_zone_col1, team_zone_col2, team_zone_col3 = st.columns(3)


    with team_zone_col1:

        st.metric(
            "Defensive",
            f"{team_defensive:.1f}%"
        )


    with team_zone_col2:

        st.metric(
            "Midfield",
            f"{team_midfield:.1f}%"
        )


    with team_zone_col3:

        st.metric(
            "Attacking",
            f"{team_attacking:.1f}%"
        )


    team_dominant_zone = team_zone.get(
        "dominant_zone",
        "Unknown"
    )


    st.write(
        f"**Dominant Team Zone:** "
        f"{str(team_dominant_zone).upper()}"
    )


    team_zone_chart = pd.DataFrame(
        {
            "Zone": [
                "Defensive",
                "Midfield",
                "Attacking"
            ],

            "Percentage": [
                team_defensive,
                team_midfield,
                team_attacking
            ]
        }
    )


    st.bar_chart(
        team_zone_chart.set_index(
            "Zone"
        )
    )


    # --------------------------------------------------------
    # KEY PLAYERS
    # --------------------------------------------------------

    st.subheader(
        "⭐ Key Team Players"
    )


    key_col1, key_col2 = st.columns(2)


    with key_col1:

        best = key_players.get(
            "best_performer",
            {}
        )

        st.write(
            f"🏆 **Best Performer:** "
            f"Player {best.get('player_id', 'N/A')}"
        )

        st.write(
            f"Score: "
            f"{best.get('performance_score', 0):.2f}/100"
        )


        active = key_players.get(
            "most_active_player",
            {}
        )

        st.write(
            f"🏃 **Most Active:** "
            f"Player {active.get('player_id', 'N/A')}"
        )

        st.write(
            f"Movement: "
            f"{active.get('movement', 0):.2f}"
        )


        fastest = key_players.get(
            "fastest_average_speed",
            {}
        )

        st.write(
            f"⚡ **Fastest Average Speed:** "
            f"Player {fastest.get('player_id', 'N/A')}"
        )

        st.write(
            f"Speed: "
            f"{fastest.get('average_speed', 0):.2f}"
        )


        max_speed = key_players.get(
            "highest_maximum_speed",
            {}
        )

        st.write(
            f"🚀 **Highest Maximum Speed:** "
            f"Player {max_speed.get('player_id', 'N/A')}"
        )

        st.write(
            f"Maximum: "
            f"{max_speed.get('maximum_speed', 0):.2f}"
        )


    with key_col2:

        defensive_player = key_players.get(
            "best_defensive_player",
            {}
        )

        st.write(
            f"🛡️ **Best Defensive:** "
            f"Player {defensive_player.get('player_id', 'N/A')}"
        )

        st.write(
            f"Presence: "
            f"{defensive_player.get('defensive_percentage', 0):.1f}%"
        )


        midfield_player = key_players.get(
            "best_midfield_player",
            {}
        )

        st.write(
            f"🎯 **Best Midfield:** "
            f"Player {midfield_player.get('player_id', 'N/A')}"
        )

        st.write(
            f"Presence: "
            f"{midfield_player.get('midfield_percentage', 0):.1f}%"
        )


        attacking_player = key_players.get(
            "best_attacking_player",
            {}
        )

        st.write(
            f"⚽ **Best Attacking:** "
            f"Player {attacking_player.get('player_id', 'N/A')}"
        )

        st.write(
            f"Presence: "
            f"{attacking_player.get('attacking_percentage', 0):.1f}%"
        )


        ball_player = key_players.get(
            "most_ball_involved_player",
            {}
        )

        st.write(
            f"⚽ **Most Ball Involved:** "
            f"Player {ball_player.get('player_id', 'N/A')}"
        )

        st.write(
            f"Interactions: "
            f"{ball_player.get('ball_interactions', 0)}"
        )


    # --------------------------------------------------------
    # TEAM STRENGTHS
    # --------------------------------------------------------

    st.subheader(
        "💪 Team Strengths"
    )


    if team_strengths:

        for strength in team_strengths:

            st.success(
                f"✓ {strength}"
            )

    else:

        st.write(
            "No team strengths available."
        )


    # --------------------------------------------------------
    # TEAM WEAKNESSES
    # --------------------------------------------------------

    st.subheader(
        "⚠️ Team Weaknesses"
    )


    if team_weaknesses:

        for weakness in team_weaknesses:

            st.warning(
                f"• {weakness}"
            )

    else:

        st.write(
            "No major weaknesses detected."
        )


    # --------------------------------------------------------
    # TEAM PLAYER TABLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Team Player Performance"
    )


    team_players = team_data.get(
        "players",
        {}
    )


    team_table = []


    for player_id, data in team_players.items():

        team_table.append(
            {
                "Player":
                    f"Player {player_id}",

                "Performance":
                    data.get(
                        "performance_score",
                        0
                    ),

                "Movement":
                    data.get(
                        "movement",
                        0
                    ),

                "Avg Speed":
                    data.get(
                        "average_speed",
                        0
                    ),

                "Max Speed":
                    data.get(
                        "maximum_speed",
                        0
                    ),

                "Dominant Zone":
                    data.get(
                        "dominant_zone",
                        "Unknown"
                    ),

                "Ball Interactions":
                    data.get(
                        "ball_interactions",
                        0
                    )
            }
        )


    if team_table:

        team_df = pd.DataFrame(
            team_table
        )

        team_df = team_df.sort_values(
            "Performance",
            ascending=False
        )

        st.dataframe(
            team_df,
            use_container_width=True,
            hide_index=True
        )


else:

    st.warning(
        "Team analysis data not found."
    )

    st.info(
        "Run this command first:\n\n"
        "`python ai\\team_analysis.py`"
    )


# ============================================================
# DETAILED PLAYER DATA
# ============================================================

st.divider()

st.header(
    "📄 Detailed Player Data"
)


detailed_data = {

    "Player":
        f"Player {selected_player}",

    "Performance Score":
        performance_score,

    "Movement":
        movement_value,

    "Average Speed":
        average_speed,

    "Maximum Speed":
        maximum_speed,

    "Defensive %":
        defensive,

    "Midfield %":
        midfield,

    "Attacking %":
        attacking,

    "Dominant Zone":
        dominant_zone,

    "Ball Interactions":
        player_ball_interactions

}


st.json(
    detailed_data
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    ### ⚽ SPORTFLASH

    **AI-Based Football Performance Analytics**

    Player Detection • Tracking • Movement • Speed • Heatmap •
    Zones • Ball Analysis • Performance Score • Ranking •
    AI Insights • Nutrition • Team Analysis

    ---
    
    *Prototype developed for AI Sports Performance Analytics.*
    """
)