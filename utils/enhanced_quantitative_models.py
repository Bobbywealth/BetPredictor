"""
Enhanced Quantitative Models for Sports Prediction
Provides statistical baselines before AI analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

class EnhancedQuantitativeEngine:
    """Enhanced quantitative modeling for sports predictions"""
    
    def __init__(self):
        self.sport_factors = {
            'NFL': {
                'home_advantage': 0.57,  # Historical home win rate
                'key_stats': ['points_for', 'points_against', 'total_yards', 'turnovers', 'sacks'],
                'weights': [0.35, 0.30, 0.15, 0.10, 0.10]
            },
            'NBA': {
                'home_advantage': 0.60,
                'key_stats': ['points_per_game', 'field_goal_pct', 'rebounds_per_game', 'assists_per_game', 'turnovers'],
                'weights': [0.25, 0.25, 0.20, 0.15, 0.15]
            },
            'MLB': {
                'home_advantage': 0.54,
                'key_stats': ['runs_per_game', 'era', 'batting_avg', 'on_base_pct', 'fielding_pct'],
                'weights': [0.25, 0.30, 0.20, 0.15, 0.10]
            },
            'NHL': {
                'home_advantage': 0.55,
                'key_stats': ['goals_per_game', 'goals_against', 'power_play_pct', 'penalty_kill_pct', 'shots_per_game'],
                'weights': [0.30, 0.30, 0.15, 0.15, 0.10]
            }
        }
    
    def calculate_enhanced_baseline(self, game_data: Dict, real_time_data: Dict) -> Dict:
        """Calculate enhanced quantitative baseline with real-time data"""
        
        sport = game_data.get('sport', 'NFL')
        home_team = self._extract_team_name(game_data.get('home_team', {}))
        away_team = self._extract_team_name(game_data.get('away_team', {}))
        
        baseline = {
            'model_type': 'Enhanced Quantitative',
            'sport': sport,
            'home_team': home_team,
            'away_team': away_team,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 1. Base probability from sport-specific home advantage
            sport_config = self.sport_factors.get(sport, self.sport_factors['NFL'])
            base_home_prob = sport_config['home_advantage']
            
            # 2. Adjust for team strength differential
            strength_adjustment = self._calculate_team_strength_differential(
                game_data, real_time_data, sport_config
            )
            
            # 3. Apply situational adjustments
            situational_adjustment = self._calculate_situational_adjustments(
                game_data, real_time_data, sport
            )
            
            # 4. Weather adjustments for outdoor sports
            weather_adjustment = self._calculate_weather_adjustment(
                real_time_data, sport
            )
            
            # 5. Injury adjustments
            injury_adjustment = self._calculate_injury_adjustment(
                real_time_data
            )
            
            # Combine all adjustments
            total_adjustment = (
                strength_adjustment + 
                situational_adjustment + 
                weather_adjustment + 
                injury_adjustment
            )
            
            # Calculate final probability (bounded between 0.15 and 0.85)
            home_win_prob = np.clip(
                base_home_prob + total_adjustment,
                0.15, 0.85
            )
            
            baseline.update({
                'home_win_probability': home_win_prob,
                'away_win_probability': 1.0 - home_win_prob,
                'base_home_advantage': base_home_prob,
                'strength_differential': strength_adjustment,
                'situational_factor': situational_adjustment,
                'weather_factor': weather_adjustment,
                'injury_factor': injury_adjustment,
                'confidence_score': self._calculate_model_confidence(
                    real_time_data, total_adjustment
                ),
                'key_insights': self._generate_quantitative_insights(
                    strength_adjustment, situational_adjustment, 
                    weather_adjustment, injury_adjustment
                )
            })
            
        except Exception as e:
            logging.error(f"Quantitative baseline error: {e}")
            baseline.update({
                'home_win_probability': 0.50,
                'away_win_probability': 0.50,
                'error': str(e),
                'confidence_score': 0.3
            })
        
        return baseline
    
    def _extract_team_name(self, team_data) -> str:
        """Extract team name from various formats"""
        if isinstance(team_data, dict):
            return team_data.get('name', team_data.get('displayName', 'Unknown'))
        return str(team_data) if team_data else 'Unknown'
    
    def _calculate_team_strength_differential(self, game_data: Dict, real_time_data: Dict, sport_config: Dict) -> float:
        """Calculate team strength differential from statistics"""
        
        team_stats = real_time_data.get('team_stats', {})
        home_stats = team_stats.get('home_stats', {})
        away_stats = team_stats.get('away_stats', {})
        
        if not home_stats or not away_stats:
            return 0.0  # No data available
        
        key_stats = sport_config['key_stats']
        weights = sport_config['weights']
        
        total_differential = 0.0
        
        for stat, weight in zip(key_stats, weights):
            home_val = home_stats.get(stat, 0)
            away_val = away_stats.get(stat, 0)
            
            if home_val == 0 and away_val == 0:
                continue
            
            # Normalize the differential (some stats are better when lower, like ERA)
            if stat in ['points_against', 'era', 'goals_against', 'turnovers']:
                # Lower is better
                differential = (away_val - home_val) / max(away_val + home_val, 1)
            else:
                # Higher is better
                differential = (home_val - away_val) / max(home_val + away_val, 1)
            
            total_differential += differential * weight
        
        # Scale to reasonable adjustment range (-0.15 to +0.15)
        return np.clip(total_differential * 0.3, -0.15, 0.15)
    
    def _calculate_situational_adjustments(self, game_data: Dict, real_time_data: Dict, sport: str) -> float:
        """Calculate situational adjustments (rest, travel, etc.)"""
        
        adjustment = 0.0
        
        # Day of week adjustments (some teams perform better on certain days)
        game_date = game_data.get('date')
        if game_date:
            try:
                date_obj = datetime.fromisoformat(game_date)
                day_of_week = date_obj.weekday()
                
                # Thursday/Monday games in NFL (short rest)
                if sport == 'NFL' and day_of_week in [0, 3]:  # Monday=0, Thursday=3
                    adjustment -= 0.02  # Slight disadvantage for short rest
                    
            except Exception:
                pass
        
        # Recent form adjustments (would require historical data)
        recent_form = real_time_data.get('recent_form', {})
        if recent_form.get('home_form', {}).get('trend') == 'positive':
            adjustment += 0.03
        elif recent_form.get('home_form', {}).get('trend') == 'negative':
            adjustment -= 0.03
            
        if recent_form.get('away_form', {}).get('trend') == 'positive':
            adjustment -= 0.03
        elif recent_form.get('away_form', {}).get('trend') == 'negative':
            adjustment += 0.03
        
        return np.clip(adjustment, -0.08, 0.08)
    
    def _calculate_weather_adjustment(self, real_time_data: Dict, sport: str) -> float:
        """Calculate weather-based adjustments for outdoor sports"""
        
        if sport not in ['NFL', 'MLB']:
            return 0.0  # Indoor sports not affected
        
        weather = real_time_data.get('weather', {})
        if not weather or weather.get('source') == 'Fallback':
            return 0.0
        
        adjustment = 0.0
        
        try:
            temp = weather.get('temperature')
            wind_speed = weather.get('wind_speed', 0)
            conditions = weather.get('conditions', '').lower()
            
            if temp and isinstance(temp, (int, float)):
                if sport == 'NFL':
                    # Extreme cold affects passing games
                    if temp < 20:
                        adjustment -= 0.02  # Favors defensive/running teams
                    elif temp > 95:
                        adjustment -= 0.01  # Heat affects performance
                
                elif sport == 'MLB':
                    # Temperature affects ball carry
                    if temp > 80:
                        adjustment += 0.01  # Favors offense (ball travels farther)
                    elif temp < 50:
                        adjustment -= 0.01  # Favors pitching
            
            # Wind effects
            if wind_speed and isinstance(wind_speed, (int, float)):
                if sport == 'NFL' and wind_speed > 15:
                    adjustment -= 0.03  # High wind hurts passing
                elif sport == 'MLB' and wind_speed > 12:
                    adjustment -= 0.02  # Wind affects hitting
            
            # Precipitation effects
            if any(condition in conditions for condition in ['rain', 'snow', 'storm']):
                if sport == 'NFL':
                    adjustment -= 0.02  # Favors running/defense
                elif sport == 'MLB':
                    adjustment -= 0.05  # Significantly affects play
            
        except Exception as e:
            logging.error(f"Weather adjustment error: {e}")
        
        return np.clip(adjustment, -0.08, 0.08)
    
    def _calculate_injury_adjustment(self, real_time_data: Dict) -> float:
        """Calculate injury-based adjustments"""
        
        injuries = real_time_data.get('injuries', {})
        reports = injuries.get('reports', [])
        
        if not reports:
            return 0.0
        
        adjustment = 0.0
        
        for report in reports:
            impact = report.get('impact', 'minimal').lower()
            team = report.get('team', '')
            
            # Determine if this affects home or away team
            # (This would need proper team matching in real implementation)
            team_adjustment = 0.0
            
            if impact == 'major':
                team_adjustment = -0.05
            elif impact == 'moderate':
                team_adjustment = -0.03
            elif impact == 'minor':
                team_adjustment = -0.01
            
            # Apply to appropriate team (simplified for now)
            adjustment += team_adjustment
        
        return np.clip(adjustment, -0.10, 0.10)
    
    def _calculate_model_confidence(self, real_time_data: Dict, total_adjustment: float) -> float:
        """Calculate confidence in the quantitative model"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data quality
        data_quality = real_time_data.get('data_quality_score', 0.0)
        confidence += data_quality * 0.3
        
        # Increase confidence for moderate adjustments (extreme adjustments are less reliable)
        adj_magnitude = abs(total_adjustment)
        if 0.02 <= adj_magnitude <= 0.08:
            confidence += 0.1
        elif adj_magnitude > 0.12:
            confidence -= 0.1
        
        return np.clip(confidence, 0.2, 0.9)
    
    def _generate_quantitative_insights(self, strength_adj: float, situational_adj: float, 
                                      weather_adj: float, injury_adj: float) -> List[str]:
        """Generate insights from quantitative analysis"""
        
        insights = []
        
        # Strength differential insights
        if abs(strength_adj) > 0.05:
            team = "Home team" if strength_adj > 0 else "Away team"
            insights.append(f"{team} has significant statistical advantage ({abs(strength_adj):.2f})")
        
        # Weather insights
        if abs(weather_adj) > 0.02:
            direction = "favors" if weather_adj > 0 else "hurts"
            insights.append(f"Weather conditions {direction} home team ({weather_adj:+.2f})")
        
        # Injury insights
        if abs(injury_adj) > 0.02:
            insights.append(f"Injury reports impact probability by {injury_adj:+.2f}")
        
        # Situational insights
        if abs(situational_adj) > 0.02:
            insights.append(f"Situational factors provide {situational_adj:+.2f} adjustment")
        
        if not insights:
            insights.append("Teams appear evenly matched statistically")
        
        return insights[:3]  # Return top 3 insights
    
    def get_spread_prediction(self, baseline: Dict, sport: str) -> Dict:
        """Convert win probability to spread prediction"""
        
        home_prob = baseline.get('home_win_probability', 0.5)
        
        # Sport-specific spread calculations (simplified)
        if sport == 'NFL':
            # NFL spreads typically range from -14 to +14
            spread = (home_prob - 0.5) * 28  # Scale to spread range
        elif sport == 'NBA':
            # NBA spreads typically range from -12 to +12
            spread = (home_prob - 0.5) * 24
        elif sport == 'MLB':
            # MLB run lines typically -1.5 to +1.5
            spread = (home_prob - 0.5) * 3
        else:
            spread = (home_prob - 0.5) * 20
        
        return {
            'predicted_spread': round(spread, 1),
            'confidence': baseline.get('confidence_score', 0.5),
            'reasoning': f"Based on {home_prob:.1%} home win probability from quantitative model"
        }
