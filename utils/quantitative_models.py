"""
Sport-specific quantitative models for baseline predictions
These models provide statistical foundation before LLM adjustments
"""

import math
import streamlit as st
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import hashlib
import json

class QuantitativeModelEngine:
    """
    Multi-sport quantitative modeling engine
    Provides statistical baselines for each sport with specific factors
    """
    
    def __init__(self):
        # Base Elo ratings (1500 = average)
        self.base_rating = 1500
        self.k_factor = 32  # Elo adjustment factor
        
        # Sport-specific parameters
        self.sport_configs = {
            'NFL': {
                'home_advantage': 57,  # Points in Elo
                'key_factors': ['rest_days', 'travel_distance', 'weather', 'injuries'],
                'pace_factor': 1.0,
                'variance': 0.15,
                'season_regression': 0.25  # Regression to mean each season
            },
            'NBA': {
                'home_advantage': 36,
                'key_factors': ['pace', 'back_to_back', 'altitude', 'rest_advantage'],
                'pace_factor': 1.2,
                'variance': 0.12,
                'season_regression': 0.20
            },
            'WNBA': {
                'home_advantage': 40,
                'key_factors': ['pace', 'back_to_back', 'travel'],
                'pace_factor': 1.1,
                'variance': 0.14,
                'season_regression': 0.22
            },
            'MLB': {
                'home_advantage': 54,
                'key_factors': ['pitcher_matchup', 'ballpark', 'weather', 'bullpen'],
                'pace_factor': 0.8,
                'variance': 0.18,
                'season_regression': 0.30
            },
            'NHL': {
                'home_advantage': 55,
                'key_factors': ['goalie', 'special_teams', 'rest', 'travel'],
                'pace_factor': 1.0,
                'variance': 0.16,
                'season_regression': 0.25
            },
            'NCAAF': {
                'home_advantage': 65,  # Higher for college
                'key_factors': ['talent_gap', 'motivation', 'weather', 'travel'],
                'pace_factor': 1.1,
                'variance': 0.20,
                'season_regression': 0.35
            },
            'NCAAB': {
                'home_advantage': 42,
                'key_factors': ['pace', 'experience', 'tournament_seeding'],
                'pace_factor': 1.3,
                'variance': 0.16,
                'season_regression': 0.30
            }
        }

    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def calculate_baseline_probability(self, game_data: Dict, real_time_data: Dict = None) -> Dict:
        """Calculate quantitative baseline probability for a game"""
        
        sport = game_data.get('sport', '').upper()
        home_team = self._safe_team_name(game_data.get('home_team'))
        away_team = self._safe_team_name(game_data.get('away_team'))
        
        if sport not in self.sport_configs:
            return self._default_baseline(home_team, away_team)
        
        try:
            # Step 1: Get team ratings
            home_rating = self._get_team_rating(home_team, sport)
            away_rating = self._get_team_rating(away_team, sport)
            
            # Step 2: Apply sport-specific adjustments
            if sport == 'NFL':
                baseline = self._calculate_nfl_baseline(home_team, away_team, home_rating, away_rating, game_data, real_time_data)
            elif sport == 'NBA':
                baseline = self._calculate_nba_baseline(home_team, away_team, home_rating, away_rating, game_data, real_time_data)
            elif sport == 'MLB':
                baseline = self._calculate_mlb_baseline(home_team, away_team, home_rating, away_rating, game_data, real_time_data)
            elif sport == 'NHL':
                baseline = self._calculate_nhl_baseline(home_team, away_team, home_rating, away_rating, game_data, real_time_data)
            elif sport in ['NCAAF', 'NCAAB']:
                baseline = self._calculate_college_baseline(home_team, away_team, home_rating, away_rating, game_data, real_time_data, sport)
            else:
                baseline = self._calculate_generic_baseline(home_team, away_team, home_rating, away_rating, sport)
            
            # Step 3: Add confidence metrics
            baseline['model_confidence'] = self._calculate_model_confidence(baseline, sport)
            baseline['key_factors_used'] = self.sport_configs[sport]['key_factors']
            baseline['sport'] = sport
            
            return baseline
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Quantitative model error for {sport}: {e}")
            return self._default_baseline(home_team, away_team)

    def _calculate_nfl_baseline(self, home_team: str, away_team: str, home_rating: float, 
                               away_rating: float, game_data: Dict, real_time_data: Dict = None) -> Dict:
        """NFL-specific baseline calculation"""
        
        config = self.sport_configs['NFL']
        
        # Base Elo calculation
        rating_diff = home_rating - away_rating + config['home_advantage']
        base_prob = self._elo_to_probability(rating_diff)
        
        adjustments = []
        adjusted_prob = base_prob
        
        # Rest advantage
        home_rest = self._get_rest_days(home_team, game_data)
        away_rest = self._get_rest_days(away_team, game_data)
        rest_advantage = home_rest - away_rest
        
        if abs(rest_advantage) >= 3:  # Significant rest difference
            rest_adj = min(rest_advantage * 0.02, 0.06)  # Max 6% adjustment
            adjusted_prob += rest_adj
            adjustments.append(f"Rest advantage: {rest_adj:+.1%}")
        
        # Weather impact (for outdoor games)
        if real_time_data and self._is_outdoor_venue(home_team):
            weather_adj = self._calculate_weather_adjustment(real_time_data.get('weather', {}))
            if abs(weather_adj) > 0.01:
                adjusted_prob += weather_adj
                adjustments.append(f"Weather impact: {weather_adj:+.1%}")
        
        # Injury impact
        if real_time_data:
            injury_adj = self._calculate_injury_adjustment(real_time_data.get('injuries', {}), 'NFL')
            if abs(injury_adj) > 0.01:
                adjusted_prob += injury_adj
                adjustments.append(f"Injury impact: {injury_adj:+.1%}")
        
        # Travel distance
        travel_adj = self._calculate_travel_adjustment(away_team, home_team)
        if abs(travel_adj) > 0.005:
            adjusted_prob += travel_adj
            adjustments.append(f"Travel factor: {travel_adj:+.1%}")
        
        # Bound probability
        adjusted_prob = max(0.15, min(0.85, adjusted_prob))
        
        return {
            'home_win_probability': adjusted_prob,
            'away_win_probability': 1 - adjusted_prob,
            'base_probability': base_prob,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_difference': rating_diff,
            'adjustments': adjustments,
            'model_type': 'NFL Quantitative',
            'factors_analyzed': len([adj for adj in adjustments if adj]),
            'confidence_level': min(0.9, 0.6 + len(adjustments) * 0.05)
        }

    def _calculate_nba_baseline(self, home_team: str, away_team: str, home_rating: float,
                               away_rating: float, game_data: Dict, real_time_data: Dict = None) -> Dict:
        """NBA-specific baseline calculation"""
        
        config = self.sport_configs['NBA']
        
        # Base calculation with pace adjustment
        rating_diff = home_rating - away_team + config['home_advantage']
        base_prob = self._elo_to_probability(rating_diff)
        
        adjustments = []
        adjusted_prob = base_prob
        
        # Back-to-back games
        home_b2b = self._is_back_to_back(home_team, game_data)
        away_b2b = self._is_back_to_back(away_team, game_data)
        
        if home_b2b and not away_b2b:
            b2b_adj = -0.04  # 4% penalty for home team
            adjusted_prob += b2b_adj
            adjustments.append(f"Home back-to-back: {b2b_adj:+.1%}")
        elif away_b2b and not home_b2b:
            b2b_adj = 0.04   # 4% boost for home team
            adjusted_prob += b2b_adj
            adjustments.append(f"Away back-to-back: {b2b_adj:+.1%}")
        
        # Rest advantage
        home_rest = self._get_rest_days(home_team, game_data)
        away_rest = self._get_rest_days(away_team, game_data)
        rest_diff = home_rest - away_rest
        
        if abs(rest_diff) >= 2:
            rest_adj = min(rest_diff * 0.015, 0.045)  # Max 4.5% adjustment
            adjusted_prob += rest_adj
            adjustments.append(f"Rest advantage: {rest_adj:+.1%}")
        
        # Pace matchup (high pace teams vs low pace)
        pace_adj = self._calculate_pace_adjustment(home_team, away_team, 'NBA')
        if abs(pace_adj) > 0.01:
            adjusted_prob += pace_adj
            adjustments.append(f"Pace matchup: {pace_adj:+.1%}")
        
        # Altitude adjustment (Denver, Utah)
        altitude_adj = self._calculate_altitude_adjustment(home_team, away_team)
        if abs(altitude_adj) > 0.005:
            adjusted_prob += altitude_adj
            adjustments.append(f"Altitude factor: {altitude_adj:+.1%}")
        
        # Injury impact
        if real_time_data:
            injury_adj = self._calculate_injury_adjustment(real_time_data.get('injuries', {}), 'NBA')
            if abs(injury_adj) > 0.01:
                adjusted_prob += injury_adj
                adjustments.append(f"Injury impact: {injury_adj:+.1%}")
        
        adjusted_prob = max(0.15, min(0.85, adjusted_prob))
        
        return {
            'home_win_probability': adjusted_prob,
            'away_win_probability': 1 - adjusted_prob,
            'base_probability': base_prob,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_difference': rating_diff,
            'adjustments': adjustments,
            'model_type': 'NBA Quantitative',
            'factors_analyzed': len(adjustments),
            'confidence_level': min(0.9, 0.6 + len(adjustments) * 0.05)
        }

    def _calculate_mlb_baseline(self, home_team: str, away_team: str, home_rating: float,
                               away_rating: float, game_data: Dict, real_time_data: Dict = None) -> Dict:
        """MLB-specific baseline calculation with pitcher emphasis"""
        
        config = self.sport_configs['MLB']
        
        # Base team calculation (reduced weight due to pitcher importance)
        team_rating_diff = (home_rating - away_rating) * 0.6  # 60% weight to team
        pitcher_diff = 0
        
        adjustments = []
        
        # Pitcher matchup (40% of the model)
        if real_time_data:
            pitcher_data = real_time_data.get('lineups', {}).get('lineup', {})
            if pitcher_data.get('type') == 'pitchers':
                pitcher_diff = self._calculate_pitcher_advantage(pitcher_data.get('probable_pitchers', {}))
                if abs(pitcher_diff) > 10:  # Significant pitcher advantage
                    adjustments.append(f"Pitcher matchup: {pitcher_diff:+.0f} rating points")
        
        # Combined rating difference
        total_rating_diff = team_rating_diff + pitcher_diff + config['home_advantage']
        base_prob = self._elo_to_probability(total_rating_diff)
        adjusted_prob = base_prob
        
        # Ballpark factors
        ballpark_adj = self._calculate_ballpark_adjustment(home_team)
        if abs(ballpark_adj) > 0.01:
            adjusted_prob += ballpark_adj
            adjustments.append(f"Ballpark factor: {ballpark_adj:+.1%}")
        
        # Weather impact
        if real_time_data:
            weather_adj = self._calculate_weather_adjustment(real_time_data.get('weather', {}), 'MLB')
            if abs(weather_adj) > 0.01:
                adjusted_prob += weather_adj
                adjustments.append(f"Weather impact: {weather_adj:+.1%}")
        
        # Bullpen strength differential
        bullpen_adj = self._calculate_bullpen_adjustment(home_team, away_team)
        if abs(bullpen_adj) > 0.01:
            adjusted_prob += bullpen_adj
            adjustments.append(f"Bullpen advantage: {bullpen_adj:+.1%}")
        
        adjusted_prob = max(0.15, min(0.85, adjusted_prob))
        
        return {
            'home_win_probability': adjusted_prob,
            'away_win_probability': 1 - adjusted_prob,
            'base_probability': base_prob,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'pitcher_advantage': pitcher_diff,
            'rating_difference': total_rating_diff,
            'adjustments': adjustments,
            'model_type': 'MLB Quantitative',
            'factors_analyzed': len(adjustments),
            'confidence_level': min(0.9, 0.7 + len(adjustments) * 0.04)  # Higher base for pitcher data
        }

    def _calculate_nhl_baseline(self, home_team: str, away_team: str, home_rating: float,
                               away_rating: float, game_data: Dict, real_time_data: Dict = None) -> Dict:
        """NHL-specific baseline calculation"""
        
        config = self.sport_configs['NHL']
        
        # Base calculation
        rating_diff = home_rating - away_rating + config['home_advantage']
        base_prob = self._elo_to_probability(rating_diff)
        
        adjustments = []
        adjusted_prob = base_prob
        
        # Goalie matchup
        goalie_adj = self._calculate_goalie_advantage(home_team, away_team)
        if abs(goalie_adj) > 0.02:
            adjusted_prob += goalie_adj
            adjustments.append(f"Goalie advantage: {goalie_adj:+.1%}")
        
        # Special teams differential
        st_adj = self._calculate_special_teams_adjustment(home_team, away_team)
        if abs(st_adj) > 0.01:
            adjusted_prob += st_adj
            adjustments.append(f"Special teams: {st_adj:+.1%}")
        
        # Rest and travel
        home_rest = self._get_rest_days(home_team, game_data)
        away_rest = self._get_rest_days(away_team, game_data)
        rest_diff = home_rest - away_rest
        
        if abs(rest_diff) >= 1:
            rest_adj = min(rest_diff * 0.02, 0.05)
            adjusted_prob += rest_adj
            adjustments.append(f"Rest advantage: {rest_adj:+.1%}")
        
        adjusted_prob = max(0.15, min(0.85, adjusted_prob))
        
        return {
            'home_win_probability': adjusted_prob,
            'away_win_probability': 1 - adjusted_prob,
            'base_probability': base_prob,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_difference': rating_diff,
            'adjustments': adjustments,
            'model_type': 'NHL Quantitative',
            'factors_analyzed': len(adjustments),
            'confidence_level': min(0.9, 0.65 + len(adjustments) * 0.05)
        }

    def _calculate_college_baseline(self, home_team: str, away_team: str, home_rating: float,
                                   away_rating: float, game_data: Dict, real_time_data: Dict = None, sport: str = 'NCAAF') -> Dict:
        """College sports baseline (NCAAF/NCAAB)"""
        
        config = self.sport_configs[sport]
        
        # Base calculation with higher home advantage
        rating_diff = home_rating - away_rating + config['home_advantage']
        base_prob = self._elo_to_probability(rating_diff)
        
        adjustments = []
        adjusted_prob = base_prob
        
        # Talent gap amplification (college has more variance)
        talent_gap = abs(home_rating - away_rating)
        if talent_gap > 100:  # Significant talent difference
            gap_multiplier = min(talent_gap / 200, 0.5)  # Up to 50% amplification
            if home_rating > away_rating:
                talent_adj = gap_multiplier * 0.1
            else:
                talent_adj = -gap_multiplier * 0.1
            
            adjusted_prob += talent_adj
            adjustments.append(f"Talent gap: {talent_adj:+.1%}")
        
        # Motivation factors (rivalry, bowl games, etc.)
        motivation_adj = self._calculate_motivation_adjustment(home_team, away_team, game_data)
        if abs(motivation_adj) > 0.01:
            adjusted_prob += motivation_adj
            adjustments.append(f"Motivation factor: {motivation_adj:+.1%}")
        
        # Conference strength
        conf_adj = self._calculate_conference_adjustment(home_team, away_team, sport)
        if abs(conf_adj) > 0.01:
            adjusted_prob += conf_adj
            adjustments.append(f"Conference factor: {conf_adj:+.1%}")
        
        adjusted_prob = max(0.10, min(0.90, adjusted_prob))  # Wider bounds for college
        
        return {
            'home_win_probability': adjusted_prob,
            'away_win_probability': 1 - adjusted_prob,
            'base_probability': base_prob,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_difference': rating_diff,
            'adjustments': adjustments,
            'model_type': f'{sport} Quantitative',
            'factors_analyzed': len(adjustments),
            'confidence_level': min(0.85, 0.55 + len(adjustments) * 0.06)  # Lower base confidence
        }

    def _calculate_generic_baseline(self, home_team: str, away_team: str, home_rating: float, 
                                   away_rating: float, sport: str) -> Dict:
        """Generic baseline for other sports"""
        
        config = self.sport_configs.get(sport, self.sport_configs['NBA'])  # Default to NBA config
        rating_diff = home_rating - away_rating + config['home_advantage']
        base_prob = self._elo_to_probability(rating_diff)
        
        return {
            'home_win_probability': base_prob,
            'away_win_probability': 1 - base_prob,
            'base_probability': base_prob,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_difference': rating_diff,
            'adjustments': [],
            'model_type': f'{sport} Generic',
            'factors_analyzed': 0,
            'confidence_level': 0.6
        }

    # Helper methods
    def _safe_team_name(self, team_data) -> str:
        """Extract team name safely"""
        if isinstance(team_data, dict):
            return team_data.get('name', team_data.get('displayName', 'Unknown'))
        elif isinstance(team_data, str):
            return team_data
        else:
            return 'Unknown'

    def _get_team_rating(self, team_name: str, sport: str) -> float:
        """Get team rating (Elo-style) - currently deterministic based on name"""
        if not team_name or team_name == 'Unknown':
            return self.base_rating
        
        # Use hash for deterministic but varied ratings
        hash_val = int(hashlib.md5(f"{team_name}_{sport}".encode()).hexdigest()[:8], 16)
        
        # Map to rating range based on sport variance
        config = self.sport_configs.get(sport, self.sport_configs['NBA'])
        variance = config.get('variance', 0.15)
        
        # Generate rating in range [base_rating * (1-variance), base_rating * (1+variance)]
        min_rating = self.base_rating * (1 - variance)
        max_rating = self.base_rating * (1 + variance)
        
        normalized = (hash_val % 1000) / 1000.0  # 0-1
        rating = min_rating + normalized * (max_rating - min_rating)
        
        return round(rating, 1)

    def _elo_to_probability(self, rating_difference: float) -> float:
        """Convert Elo rating difference to win probability"""
        return 1 / (1 + 10 ** (-rating_difference / 400))

    def _default_baseline(self, home_team: str, away_team: str) -> Dict:
        """Default baseline for unknown sports or errors"""
        return {
            'home_win_probability': 0.54,  # Slight home advantage
            'away_win_probability': 0.46,
            'base_probability': 0.54,
            'home_rating': self.base_rating,
            'away_rating': self.base_rating,
            'rating_difference': 0,
            'adjustments': [],
            'model_type': 'Default',
            'factors_analyzed': 0,
            'confidence_level': 0.5
        }

    def _calculate_model_confidence(self, baseline: Dict, sport: str) -> float:
        """Calculate how confident we are in this model prediction"""
        base_confidence = 0.7
        
        # More factors analyzed = higher confidence
        factors = baseline.get('factors_analyzed', 0)
        factor_bonus = min(factors * 0.05, 0.2)
        
        # Stronger rating differences = higher confidence
        rating_diff = abs(baseline.get('rating_difference', 0))
        if rating_diff > 100:
            rating_bonus = min((rating_diff - 100) / 1000, 0.1)
        else:
            rating_bonus = 0
        
        # Sport-specific confidence adjustments
        sport_multiplier = {
            'MLB': 0.9,    # Lower due to randomness
            'NHL': 0.85,   # Lower due to randomness
            'NFL': 1.0,    # Standard
            'NBA': 1.05,   # Higher due to more games
            'NCAAF': 0.8,  # Lower due to fewer games
            'NCAAB': 0.9   # Tournament randomness
        }.get(sport, 1.0)
        
        final_confidence = (base_confidence + factor_bonus + rating_bonus) * sport_multiplier
        return min(0.95, max(0.4, final_confidence))

    # Placeholder methods for specific adjustments (would be enhanced with real data)
    def _get_rest_days(self, team: str, game_data: Dict) -> int:
        """Get rest days for team (placeholder)"""
        # Would use real schedule data
        hash_val = int(hashlib.md5(f"rest_{team}".encode()).hexdigest()[:4], 16)
        return (hash_val % 4) + 1  # 1-4 days rest

    def _is_back_to_back(self, team: str, game_data: Dict) -> bool:
        """Check if team played yesterday (placeholder)"""
        hash_val = int(hashlib.md5(f"b2b_{team}".encode()).hexdigest()[:4], 16)
        return (hash_val % 10) == 0  # 10% chance

    def _is_outdoor_venue(self, home_team: str) -> bool:
        """Check if venue is outdoor (placeholder)"""
        outdoor_teams = ['Green Bay Packers', 'Chicago Bears', 'Denver Broncos', 'Kansas City Chiefs']
        return home_team in outdoor_teams

    def _calculate_weather_adjustment(self, weather_data: Dict, sport: str = 'NFL') -> float:
        """Calculate weather impact adjustment"""
        if not weather_data or weather_data.get('error'):
            return 0.0
        
        impact = weather_data.get('impact', 'favorable')
        
        if sport == 'NFL':
            adjustments = {
                'high_wind': -0.02,      # Favors defense/running
                'heavy_rain': -0.01,     # Favors home team familiarity
                'freezing': 0.01,        # Favors home team
                'extreme_heat': -0.01,   # Neutral impact
                'favorable': 0.0
            }
        elif sport == 'MLB':
            adjustments = {
                'high_wind': 0.0,        # Complex impact on offense
                'heavy_rain': 0.0,       # Games usually postponed
                'favorable': 0.0
            }
        else:
            return 0.0
        
        return adjustments.get(impact, 0.0)

    def _calculate_injury_adjustment(self, injury_data: Dict, sport: str) -> float:
        """Calculate injury impact on win probability"""
        if not injury_data or injury_data.get('error'):
            return 0.0
        
        injuries = injury_data.get('injuries', {})
        home_injuries = injuries.get('home_team', [])
        away_injuries = injuries.get('away_team', [])
        
        home_impact = sum(0.03 if inj.get('impact') == 'High' else 
                         0.015 if inj.get('impact') == 'Medium' else 0.005 
                         for inj in home_injuries)
        
        away_impact = sum(0.03 if inj.get('impact') == 'High' else 
                         0.015 if inj.get('impact') == 'Medium' else 0.005 
                         for inj in away_injuries)
        
        # Net impact (positive favors away team, negative favors home)
        return away_impact - home_impact

    def _calculate_travel_adjustment(self, away_team: str, home_team: str) -> float:
        """Calculate travel distance impact (placeholder)"""
        # Would use real geographic data
        hash_val = int(hashlib.md5(f"travel_{away_team}_{home_team}".encode()).hexdigest()[:4], 16)
        distance = (hash_val % 3000) + 500  # 500-3500 miles
        
        if distance > 2500:  # Cross-country
            return -0.015  # 1.5% penalty for away team
        elif distance > 1500:  # Long distance
            return -0.008  # 0.8% penalty
        else:
            return 0.0

    def _calculate_pace_adjustment(self, home_team: str, away_team: str, sport: str) -> float:
        """Calculate pace matchup adjustment (placeholder)"""
        # Would use real pace data
        return 0.0  # Placeholder

    def _calculate_altitude_adjustment(self, home_team: str, away_team: str) -> float:
        """Calculate altitude advantage"""
        high_altitude_teams = ['Denver Nuggets', 'Utah Jazz', 'Denver Broncos']
        if home_team in high_altitude_teams:
            return 0.02  # 2% boost for altitude
        return 0.0

    def _calculate_pitcher_advantage(self, pitcher_data: Dict) -> float:
        """Calculate pitcher matchup advantage in rating points"""
        home_pitcher = pitcher_data.get('home_pitcher', {})
        away_pitcher = pitcher_data.get('away_pitcher', {})
        
        try:
            home_era = float(home_pitcher.get('era', 4.0)) if home_pitcher.get('era') != 'N/A' else 4.0
            away_era = float(away_pitcher.get('era', 4.0)) if away_pitcher.get('era') != 'N/A' else 4.0
            
            # ERA difference to rating points (lower ERA = better)
            era_diff = away_era - home_era  # Positive if home pitcher is better
            rating_diff = era_diff * 30  # Scale ERA to rating points
            
            return max(-60, min(60, rating_diff))  # Cap at +/- 60 rating points
            
        except (ValueError, TypeError):
            return 0.0

    def _calculate_ballpark_adjustment(self, home_team: str) -> float:
        """Calculate ballpark factor adjustment (placeholder)"""
        # Would use real ballpark factors
        hitter_friendly = ['Colorado Rockies', 'Boston Red Sox']
        pitcher_friendly = ['San Francisco Giants', 'Seattle Mariners']
        
        if home_team in hitter_friendly:
            return 0.01  # Slight boost for home hitters
        elif home_team in pitcher_friendly:
            return -0.01  # Slight penalty for home hitters
        return 0.0

    def _calculate_bullpen_adjustment(self, home_team: str, away_team: str) -> float:
        """Calculate bullpen strength differential (placeholder)"""
        # Would use real bullpen ERA/WHIP data
        return 0.0  # Placeholder

    def _calculate_goalie_advantage(self, home_team: str, away_team: str) -> float:
        """Calculate goalie matchup advantage (placeholder)"""
        # Would use real goalie save percentage, GAA data
        return 0.0  # Placeholder

    def _calculate_special_teams_adjustment(self, home_team: str, away_team: str) -> float:
        """Calculate special teams differential (placeholder)"""
        # Would use real PP%, PK% data
        return 0.0  # Placeholder

    def _calculate_motivation_adjustment(self, home_team: str, away_team: str, game_data: Dict) -> float:
        """Calculate motivation factors for college (placeholder)"""
        # Would consider rivalry games, bowl games, conference championships
        return 0.0  # Placeholder

    def _calculate_conference_adjustment(self, home_team: str, away_team: str, sport: str) -> float:
        """Calculate conference strength differential (placeholder)"""
        # Would use real conference RPI/NET rankings
        return 0.0  # Placeholder
