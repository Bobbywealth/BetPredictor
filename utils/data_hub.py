"""
Unified data hub for multi-sport features and baseline modeling.
Aggregates team ratings, form, and other structured features for AI analysis.
"""

from typing import Dict, Any
from datetime import datetime
import hashlib

def get_game_features(game: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate multi-sport features for baseline modeling.
    This is a lightweight hub designed to be extended. It returns a
    consistent feature dictionary used by the quant baseline and the LLM prompt.
    """
    home = _safe_team_name(game.get("home_team"))
    away = _safe_team_name(game.get("away_team"))
    sport = str(game.get("sport", "Unknown")).upper()
    
    # Parse game datetime
    try:
        game_dt = datetime.fromisoformat(str(game.get("date", datetime.now().isoformat())))
    except:
        game_dt = datetime.now()
    
    features: Dict[str, Any] = {
        "sport": sport,
        "home_team": home,
        "away_team": away,
        "game_time_utc": game_dt.isoformat(),
        
        # Team quality priors (placeholder Elo-like ratings 1400–1700, deterministic by name)
        "home_rating": _name_seed_rating(home),
        "away_rating": _name_seed_rating(away),
        
        # Home field advantage (sport-specific)
        "home_edge": _get_home_advantage(sport),
        
        # Injury placeholders (would be real data from ESPN APIs)
        "key_out_home": _simulated_injuries(home),
        "key_out_away": _simulated_injuries(away),
        
        # Form factors (placeholder - would be real recent performance)
        "home_form_l10": _simulate_form(home),
        "away_form_l10": _simulate_form(away),
        
        # Travel/rest (placeholder)
        "home_rest_days": 2,
        "away_rest_days": 1,
        "away_travel_distance": 500,  # miles
        
        # Data quality indicator
        "data_quality": 0.65,  # Would be calculated based on available real data
    }
    
    # Sport-specific feature tweaks
    if sport == "MLB":
        features["home_edge"] = 0.054  # Slightly higher for baseball
    elif sport == "NBA":
        features["home_edge"] = 0.036  # Lower for basketball
    elif sport == "NFL":
        features["home_edge"] = 0.057  # Higher for football
    elif sport == "NHL":
        features["home_edge"] = 0.055  # High for hockey
    
    return features

def _safe_team_name(team_obj) -> str:
    """Extract team name safely from various formats"""
    if isinstance(team_obj, dict):
        return team_obj.get("name", team_obj.get("displayName", "Unknown"))
    elif isinstance(team_obj, str):
        return team_obj
    else:
        return "Unknown"

def _name_seed_rating(team_name: str) -> float:
    """Generate deterministic rating based on team name (1400-1700 range)"""
    if not team_name or team_name == "Unknown":
        return 1500.0
    
    # Use hash for deterministic but varied ratings
    hash_val = int(hashlib.md5(team_name.encode()).hexdigest()[:8], 16)
    normalized = (hash_val % 300) + 1400  # Range 1400-1700
    return float(normalized)

def _get_home_advantage(sport: str) -> float:
    """Get sport-specific home field advantage"""
    advantages = {
        "NFL": 0.057,
        "NBA": 0.036, 
        "WNBA": 0.040,
        "MLB": 0.054,
        "NHL": 0.055,
        "NCAAF": 0.065,  # Higher for college
        "NCAAB": 0.042,
        "TENNIS": 0.000,  # Neutral courts mostly
    }
    return advantages.get(sport, 0.045)  # Default 4.5%

def _simulated_injuries(team_name: str) -> bool:
    """Simulate key player injury status (placeholder)"""
    # Use team name hash to create deterministic but varied injury status
    hash_val = int(hashlib.md5(f"injury_{team_name}".encode()).hexdigest()[:4], 16)
    return (hash_val % 10) == 0  # 10% chance of key injury

def _simulate_form(team_name: str) -> float:
    """Simulate recent form (0.0-1.0, where 0.5 is average)"""
    hash_val = int(hashlib.md5(f"form_{team_name}".encode()).hexdigest()[:6], 16)
    normalized = (hash_val % 100) / 100.0  # 0.0-1.0
    return normalized
