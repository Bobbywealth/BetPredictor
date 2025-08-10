from __future__ import annotations

import random
import requests
from datetime import datetime, timedelta
from typing import Dict, Any


def _safe_team_name(team: Any) -> str:
    if isinstance(team, dict):
        return team.get("name", "Unknown")
    return str(team) if team else "Unknown"


def get_game_features(game: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate multi-sport features for baseline modeling.

    This is a lightweight hub designed to be extended. It returns a
    consistent feature dictionary used by the quant baseline and the LLM prompt.
    """
    home = _safe_team_name(game.get("home_team"))
    away = _safe_team_name(game.get("away_team"))
    sport = str(game.get("sport", "Unknown")).upper()

    commence_iso = game.get("commence_time") or game.get("date")
    try:
        game_dt = (
            datetime.fromisoformat(commence_iso.replace("Z", "+00:00"))
            if commence_iso
            else datetime.utcnow()
        )
    except Exception:
        game_dt = datetime.utcnow()

    features: Dict[str, Any] = {
        "sport": sport,
        "home_team": home,
        "away_team": away,
        "game_time_utc": game_dt.isoformat(),
        # Team quality priors (placeholder Elo-like ratings 1400–1700, deterministic by name)
        "home_rating": _name_seed_rating(home),
        "away_rating": _name_seed_rating(away),
        # Situational
        "home_edge": 0.045,  # 4.5% generic home advantage; sport-specific adjustments applied later
        "rest_days_home": 2,  # placeholders; wire real schedule later
        "rest_days_away": 2,
        # Injuries/news (string summaries for prompt; simple impact flags for quant)
        "injuries_home": _simulated_injuries(home),
        "injuries_away": _simulated_injuries(away),
        "key_out_home": False,
        "key_out_away": False,
        # Form (last-10 proxy, 0–1)
        "form_home": 0.5,
        "form_away": 0.5,
        # Weather model inputs (outdoor sports)
        "weather": "Unknown/Indoor",
        "wind_mph": 0.0,
        "temp_f": 70.0,
        # Data quality meter (0–1). As we integrate real APIs, raise this.
        "data_quality": 0.65,
    }

    # Sport-specific default tweaks
    if sport in {"NFL", "NCAAF", "MLB"}:
        features["data_quality"] = 0.7
    if sport in {"NBA", "WNBA", "NCAAB"}:
        features["home_edge"] = 0.035

    return features


def _name_seed_rating(name: str) -> float:
    """Deterministic pseudo-rating so the baseline behaves consistently before we wire real Elo."""
    seed = abs(hash(name)) % 300
    return 1400 + (seed / 300) * 300  # 1400–1700


def _simulated_injuries(team: str) -> str:
    scenarios = [
        f"{team}: No major injuries reported",
        f"{team}: Role player questionable",
        f"{team}: Starter questionable (game-time decision)",
        f"{team}: Key starter OUT",
    ]
    # Bias toward healthier states
    weights = [0.45, 0.30, 0.20, 0.05]
    return random.choices(scenarios, weights=weights, k=1)[0]


