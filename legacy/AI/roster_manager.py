import os
import json

ROSTER_FILE = os.path.join("results", "roster_config.json")

# Clean initial roster configuration with no hardcoded fake players
DEFAULT_ROSTER_CONFIG = {
    "team_size": "5v5",  # Options: 5v5, 7v7, 11v11, Custom
    "players_per_team": 5,
    "team_a": {
        "name": "Team A",
        "primary_color": "#E63946",
        "secondary_color": "#FFFFFF",
        "formation": "2-2-1",
        "coach": ""
    },
    "team_b": {
        "name": "Team B",
        "primary_color": "#1D3557",
        "secondary_color": "#F1FAEE",
        "formation": "2-2-1",
        "coach": ""
    },
    "players": {}
}

# Instant 1-Click Match Demo Configuration (Portugal vs Spain)
PORTUGAL_SPAIN_DEMO_CONFIG = {
    "team_size": "5v5",
    "players_per_team": 5,
    "team_a": {
        "name": "Portugal",
        "primary_color": "#E63946",
        "secondary_color": "#FFFFFF",
        "formation": "4-3-3",
        "coach": "Roberto Martínez"
    },
    "team_b": {
        "name": "Selección Española de Fútbol",
        "primary_color": "#dedede",
        "secondary_color": "#1D3557",
        "formation": "4-3-3",
        "coach": "Luis de la Fuente"
    },
    "players": {
        "1": {"name": "Cristiano Ronaldo", "jersey_number": 7, "team": "Team A", "position": "Forward / Winger", "notes": "Captain & Top Finisher", "photo_path": ""},
        "2": {"name": "Bernardo Silva", "jersey_number": 10, "team": "Team A", "position": "Right Winger", "notes": "Agile Dribbler", "photo_path": ""},
        "3": {"name": "Bruno Fernandes", "jersey_number": 8, "team": "Team A", "position": "Attacking Midfielder", "notes": "Playmaker", "photo_path": ""},
        "4": {"name": "Diogo Costa", "jersey_number": 1, "team": "Team A", "position": "Goalkeeper", "notes": "Shot Stopper", "photo_path": ""},
        "5": {"name": "Rúben Dias", "jersey_number": 3, "team": "Team A", "position": "Center Back", "notes": "Defensive Anchor", "photo_path": ""},
        "6": {"name": "Aymeric Laporte", "jersey_number": 14, "team": "Team B", "position": "Center Back", "notes": "Ball Playing Defender", "photo_path": ""},
        "7": {"name": "Dani Olmo", "jersey_number": 10, "team": "Team B", "position": "Attacking Midfielder", "notes": "Chance Creator", "photo_path": ""},
        "8": {"name": "Rodri", "jersey_number": 16, "team": "Team B", "position": "Defensive Midfielder", "notes": "Tactical Pivot & Ball Winner", "photo_path": ""},
        "9": {"name": "Lamine Yamal", "jersey_number": 19, "team": "Team B", "position": "Forward / Winger", "notes": "Explosive Pace & 1v1", "photo_path": ""},
        "10": {"name": "Unai Simón", "jersey_number": 23, "team": "Team B", "position": "Goalkeeper", "notes": "Sweeper Keeper", "photo_path": ""}
    }
}

def load_roster_config():
    """Load roster configuration from results/roster_config.json."""
    if not os.path.exists(ROSTER_FILE):
        save_roster_config(DEFAULT_ROSTER_CONFIG)
        return DEFAULT_ROSTER_CONFIG
    try:
        with open(ROSTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "team_size" not in data:
                data["team_size"] = DEFAULT_ROSTER_CONFIG["team_size"]
            if "players_per_team" not in data:
                data["players_per_team"] = DEFAULT_ROSTER_CONFIG["players_per_team"]
            if "team_a" not in data:
                data["team_a"] = DEFAULT_ROSTER_CONFIG["team_a"]
            if "team_b" not in data:
                data["team_b"] = DEFAULT_ROSTER_CONFIG["team_b"]
            if "players" not in data:
                data["players"] = {}
            return data
    except Exception as e:
        print(f"Error loading roster config: {e}")
        return DEFAULT_ROSTER_CONFIG

def save_roster_config(config):
    """Save roster configuration to results/roster_config.json."""
    os.makedirs(os.path.dirname(ROSTER_FILE), exist_ok=True)
    try:
        with open(ROSTER_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving roster config: {e}")
        return False

def reset_roster_config():
    """Reset roster configuration to a completely clean state with no players."""
    save_roster_config(DEFAULT_ROSTER_CONFIG)
    return DEFAULT_ROSTER_CONFIG

def load_demo_roster_config():
    """Load instant Portugal vs Spain presentation match demo configuration."""
    save_roster_config(PORTUGAL_SPAIN_DEMO_CONFIG)
    return PORTUGAL_SPAIN_DEMO_CONFIG

def get_player_roster_info(player_id, roster_config=None):
    """Get player metadata (name, jersey_number, position, team, photo) for a given player_id."""
    if roster_config is None:
        roster_config = load_roster_config()
    
    str_id = str(player_id)
    players = roster_config.get("players", {})
    
    if str_id in players:
        p_info = players[str_id]
        return {
            "player_id": str_id,
            "name": p_info.get("name", f"Player #{str_id}"),
            "jersey_number": p_info.get("jersey_number", int(str_id) if str_id.isdigit() else 99),
            "team": p_info.get("team", "Team A"),
            "position": p_info.get("position", "Midfielder"),
            "photo_path": p_info.get("photo_path", ""),
            "notes": p_info.get("notes", "")
        }
    else:
        return {
            "player_id": str_id,
            "name": f"Player #{str_id}",
            "jersey_number": int(str_id) if str_id.isdigit() else 99,
            "team": "Team A" if (int(str_id) if str_id.isdigit() else 1) % 2 == 0 else "Team B",
            "position": "Field Player",
            "photo_path": "",
            "notes": "Unregistered"
        }
