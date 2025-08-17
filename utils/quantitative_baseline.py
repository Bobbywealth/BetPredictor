"""
Quantitative Baseline Models for Sports Predictions
Provides statistical foundation before AI analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import streamlit as st

class QuantitativeBaseline:
    """Calculate statistical baselines for game predictions"""
    
    def __init__(self):
        self.sport_factors = {
            'NFL': {
                'home_advantage': 0.57,  # Home teams win ~57% historically
                'key_stats': ['offensive_efficiency', 'defensive_efficiency', 'turnover_differential'],
                'scoring_variance': 0.15,
                'upset_frequency': 0.25
            },
            'NBA': {
                'home_advantage': 0.60,  # Stronger home advantage
                'key_stats': ['offensive_rating', 'defensive_rating', 'pace'],
                'scoring_variance': 0.12,
                'upset_frequency': 0.20
            },
            'MLB': {
                'home_advantage': 0.54,  # Weaker home advantage
                'key_stats': ['era', 'ops', 'fielding_pct'],
                'scoring_variance': 0.25,
                'upset_frequency': 0.35
            },
            'NHL': {
                'home_advantage': 0.55,
                'key_stats': ['goals_for', 'goals_against', 'power_play_pct'],
                'scoring_variance': 0.20,
                'upset_frequency': 0.30
            }
        }
    
    def calculate_baseline_probability(self, game_data: Dict, real_time_data: Dict = None) -> Dict:
        """Calculate baseline win probability using statistical models"""
        sport = game_data.get('sport', 'NFL')
        home_team = game_data.get('home_team', {}).get('name', 'Home')
        away_team = game_data.get('away_team', {}).get('name', 'Away')
        
        # Get sport-specific factors
        sport_config = self.sport_factors.get(sport, self.sport_factors['NFL'])
        
        # Step 1: Base home field advantage
        home_prob = sport_config['home_advantage']
        
        # Step 2: Adjust for team strength differential
        strength_adjustment = self._calculate_strength_differential(game_data, real_time_data)
        home_prob += strength_adjustment
        
        # Step 3: Adjust for recent form
        form_adjustment = self._calculate_form_adjustment(game_data, real_time_data)
        home_prob += form_adjustment
        
        # Step 4: Adjust for injuries
        injury_adjustment = self._calculate_injury_impact(game_data, real_time_data)
        home_prob += injury_adjustment
        
        # Step 5: Adjust for weather (outdoor sports only)
        weather_adjustment = self._calculate_weather_impact(game_data, real_time_data)
        home_prob += weather_adjustment
        
        # Step 6: Adjust for motivation/situation
        situation_adjustment = self._calculate_situational_factors(game_data)
        home_prob += situation_adjustment
        
        # Ensure probability stays within bounds
        home_prob = max(0.15, min(0.85, home_prob))
        away_prob = 1.0 - home_prob
        
        # Calculate spread and total estimates
        spread_estimate = self._estimate_spread(home_prob, sport)
        total_estimate = self._estimate_total(game_data, real_time_data, sport)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_baseline_confidence(game_data, real_time_data)
        
        return {
            'home_win_probability': home_prob,
            'away_win_probability': away_prob,
            'estimated_spread': spread_estimate,
            'estimated_total': total_estimate,
            'confidence': confidence,
            'key_factors': self._identify_key_factors(game_data, real_time_data),
            'statistical_edge': self._calculate_statistical_edge(home_prob, sport),
            'model_components': {
                'home_field': sport_config['home_advantage'],
                'strength_diff': strength_adjustment,
                'recent_form': form_adjustment,
                'injuries': injury_adjustment,
                'weather': weather_adjustment,
                'situation': situation_adjustment
            }
        }
    
    def _calculate_strength_differential(self, game_data: Dict, real_time_data: Dict = None) -> float:
        """Calculate team strength differential"""
        if not real_time_data or 'team_stats' not in real_time_data:
            return 0.0
        
        try:
            home_stats = real_time_data['team_stats'].get('home_team_stats', {})
            away_stats = real_time_data['team_stats'].get('away_team_stats', {})
            sport = game_data.get('sport', 'NFL')
            
            if sport == 'NFL':
                home_off = home_stats.get('offensive_efficiency', 0.5)
                home_def = home_stats.get('defensive_efficiency', 0.5)
                away_off = away_stats.get('offensive_efficiency', 0.5)
                away_def = away_stats.get('defensive_efficiency', 0.5)
                
                # Higher offensive efficiency and lower defensive efficiency is better
                home_strength = home_off + (1 - home_def)
                away_strength = away_off + (1 - away_def)
                
                # Convert to probability adjustment (-0.15 to +0.15)
                diff = (home_strength - away_strength) * 0.15
                return max(-0.15, min(0.15, diff))
            
            elif sport == 'NBA':
                home_net = home_stats.get('offensive_rating', 110) - home_stats.get('defensive_rating', 110)
                away_net = away_stats.get('offensive_rating', 110) - away_stats.get('defensive_rating', 110)
                
                # Net rating difference to probability
                diff = (home_net - away_net) / 20.0  # 20 point net rating = 100% win prob difference
                return max(-0.15, min(0.15, diff))
            
        except Exception:
            pass
        
        return 0.0
    
    def _calculate_form_adjustment(self, game_data: Dict, real_time_data: Dict = None) -> float:
        """Calculate recent form impact"""
        if not real_time_data or 'recent_form' not in real_time_data:
            return 0.0
        
        try:
            home_form = real_time_data['recent_form'].get('home_last_5', {})
            away_form = real_time_data['recent_form'].get('away_last_5', {})
            
            home_wins = home_form.get('wins', 2.5)
            away_wins = away_form.get('wins', 2.5)
            
            # Recent form difference (max impact ±0.08)
            form_diff = (home_wins - away_wins) / 5.0 * 0.08
            return max(-0.08, min(0.08, form_diff))
            
        except Exception:
            return 0.0
    
    def _calculate_injury_impact(self, game_data: Dict, real_time_data: Dict = None) -> float:
        """Calculate injury impact on probability"""
        if not real_time_data or 'injuries' not in real_time_data:
            return 0.0
        
        try:
            home_injuries = real_time_data['injuries'].get('home_team_injuries', [])
            away_injuries = real_time_data['injuries'].get('away_team_injuries', [])
            
            home_impact = sum(self._injury_severity(inj) for inj in home_injuries)
            away_impact = sum(self._injury_severity(inj) for inj in away_injuries)
            
            # Injuries hurt the team, so subtract from their probability
            net_impact = away_impact - home_impact  # Positive if away more injured
            return max(-0.10, min(0.10, net_impact))
            
        except Exception:
            return 0.0
    
    def _injury_severity(self, injury: Dict) -> float:
        """Calculate severity score for an injury"""
        if not isinstance(injury, dict):
            return 0.0
        
        status = injury.get('status', '').lower()
        impact = injury.get('impact', '').lower()
        
        severity = 0.0
        
        # Status impact
        if 'out' in status:
            severity += 0.04
        elif 'doubtful' in status:
            severity += 0.025
        elif 'questionable' in status:
            severity += 0.015
        
        # Impact multiplier
        if impact == 'high':
            severity *= 1.5
        elif impact == 'medium':
            severity *= 1.0
        elif impact == 'low':
            severity *= 0.5
        
        return severity
    
    def _calculate_weather_impact(self, game_data: Dict, real_time_data: Dict = None) -> float:
        """Calculate weather impact (outdoor sports only)"""
        sport = game_data.get('sport', 'NFL')
        
        if sport not in ['NFL', 'MLB']:  # Indoor sports
            return 0.0
        
        if not real_time_data or 'weather' not in real_time_data:
            return 0.0
        
        try:
            weather = real_time_data['weather']
            impact = weather.get('impact', 'Low').lower()
            
            # Weather generally favors home team (familiarity)
            if impact == 'high':
                return 0.03
            elif impact == 'medium':
                return 0.015
            
        except Exception:
            pass
        
        return 0.0
    
    def _calculate_situational_factors(self, game_data: Dict) -> float:
        """Calculate situational factors (rest, travel, etc.)"""
        # This would analyze rest days, travel distance, back-to-back games, etc.
        # For now, return neutral
        return 0.0
    
    def _estimate_spread(self, home_prob: float, sport: str) -> float:
        """Estimate point spread from win probability"""
        # Convert probability to spread using sport-specific factors
        sport_config = self.sport_factors.get(sport, self.sport_factors['NFL'])
        
        if sport == 'NFL':
            # NFL: 50% = pick'em, each 1% ≈ 0.5 points
            spread = (home_prob - 0.5) * 28  # Max spread around ±14
        elif sport == 'NBA':
            # NBA: Higher scoring, larger spreads
            spread = (home_prob - 0.5) * 40  # Max spread around ±20
        elif sport == 'MLB':
            # MLB: Run line typically ±1.5
            spread = (home_prob - 0.5) * 6  # Max around ±3 runs
        else:
            spread = (home_prob - 0.5) * 20
        
        return round(spread * 2) / 2  # Round to nearest 0.5
    
    def _estimate_total(self, game_data: Dict, real_time_data: Dict = None, sport: str = 'NFL') -> float:
        """Estimate game total points"""
        if not real_time_data or 'team_stats' not in real_time_data:
            # Return sport averages
            averages = {
                'NFL': 45.0,
                'NBA': 220.0,
                'MLB': 9.0,
                'NHL': 6.0
            }
            return averages.get(sport, 45.0)
        
        try:
            home_stats = real_time_data['team_stats'].get('home_team_stats', {})
            away_stats = real_time_data['team_stats'].get('away_team_stats', {})
            
            if sport == 'NFL':
                home_ppg = home_stats.get('points_per_game', 22.5)
                away_ppg = away_stats.get('points_per_game', 22.5)
                estimated_total = home_ppg + away_ppg
                
                # Adjust for weather
                if real_time_data.get('weather', {}).get('impact') == 'High':
                    estimated_total *= 0.9  # Reduce for bad weather
                
                return round(estimated_total * 2) / 2  # Round to nearest 0.5
            
        except Exception:
            pass
        
        # Fallback to sport averages
        averages = {
            'NFL': 45.0,
            'NBA': 220.0,
            'MLB': 9.0,
            'NHL': 6.0
        }
        return averages.get(sport, 45.0)
    
    def _calculate_baseline_confidence(self, game_data: Dict, real_time_data: Dict = None) -> float:
        """Calculate confidence in the baseline model"""
        confidence = 0.7  # Base confidence
        
        # Increase confidence based on data availability
        if real_time_data:
            if 'team_stats' in real_time_data:
                confidence += 0.1
            if 'injuries' in real_time_data:
                confidence += 0.05
            if 'recent_form' in real_time_data:
                confidence += 0.05
            if 'weather' in real_time_data:
                confidence += 0.02
        
        return min(0.9, confidence)  # Cap at 90%
    
    def _identify_key_factors(self, game_data: Dict, real_time_data: Dict = None) -> List[str]:
        """Identify the most important factors for this game"""
        factors = []
        
        sport = game_data.get('sport', 'NFL')
        factors.append(f"Home field advantage ({self.sport_factors[sport]['home_advantage']:.1%})")
        
        if real_time_data:
            if 'team_stats' in real_time_data:
                factors.append("Team strength differential analyzed")
            if 'injuries' in real_time_data:
                factors.append("Injury reports considered")
            if 'weather' in real_time_data and sport in ['NFL', 'MLB']:
                factors.append("Weather conditions factored")
        
        return factors
    
    def _calculate_statistical_edge(self, home_prob: float, sport: str) -> Dict:
        """Calculate if there's a statistical edge"""
        sport_config = self.sport_factors.get(sport, self.sport_factors['NFL'])
        base_advantage = sport_config['home_advantage']
        
        edge_strength = abs(home_prob - 0.5)
        
        if edge_strength > 0.15:
            return {
                'edge_type': 'Strong',
                'edge_value': edge_strength,
                'recommendation': 'High confidence bet'
            }
        elif edge_strength > 0.08:
            return {
                'edge_type': 'Moderate',
                'edge_value': edge_strength,
                'recommendation': 'Consider betting'
            }
        else:
            return {
                'edge_type': 'Weak',
                'edge_value': edge_strength,
                'recommendation': 'Pass or small bet'
            }
