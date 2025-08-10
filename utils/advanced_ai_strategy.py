import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import json
import time

class AdvancedAIStrategy:
    """
    Advanced AI Strategy for High-Accuracy Sports Predictions
    
    This system combines multiple data sources and AI techniques:
    1. Real-time data integration (injuries, weather, line movements)
    2. Historical performance analysis
    3. Advanced statistical modeling
    4. Market sentiment analysis
    5. Multi-model consensus with confidence weighting
    """
    
    def __init__(self):
        self.data_sources = {
            'injuries': 'https://api.sportsdata.io/v3',  # Injury reports
            'weather': 'https://api.openweathermap.org/data/2.5',  # Weather data
            'stats': 'https://api.mysportsfeeds.com/v2.1',  # Advanced stats
            'news': 'https://newsapi.org/v2'  # Sports news sentiment
        }
        
        # Confidence thresholds for different prediction types
        self.confidence_thresholds = {
            'high_confidence': 0.85,  # Only bet when very confident
            'medium_confidence': 0.70,  # Consider with smaller stakes
            'low_confidence': 0.55,   # Monitor only
        }
        
        # Historical accuracy tracking
        self.model_performance = {
            'spread_accuracy': 0.0,
            'total_accuracy': 0.0,
            'moneyline_accuracy': 0.0,
            'games_analyzed': 0
        }

    def generate_enhanced_prompt(self, game_data: Dict, real_time_data: Dict = None) -> str:
        """Generate a comprehensive prompt with all available data"""
        
        home_team = game_data.get('home_team', {}).get('name', 'Unknown')
        away_team = game_data.get('away_team', {}).get('name', 'Unknown')
        sport = game_data.get('sport', 'Unknown')
        
        # Base prompt with enhanced instructions
        prompt = f"""
        You are an elite sports analyst with access to comprehensive data. Analyze this {sport} game with extreme precision:
        
        **GAME DETAILS:**
        - Matchup: {away_team} @ {home_team}
        - Sport: {sport}
        - Date: {game_data.get('date', 'Unknown')}
        - Time: {game_data.get('time', 'Unknown')}
        - Venue: {game_data.get('venue', 'Unknown')}
        
        **ANALYSIS REQUIREMENTS:**
        1. **Team Form Analysis**: Recent performance trends (last 10 games)
        2. **Head-to-Head**: Historical matchup patterns and trends
        3. **Key Player Impact**: Star players, injuries, suspensions
        4. **Situational Factors**: Rest days, travel, motivation levels
        5. **Statistical Edges**: Advanced metrics, efficiency ratings
        6. **Market Analysis**: Line value, public vs sharp money
        """
        
        # Add real-time data if available
        if real_time_data:
            if real_time_data.get('injuries'):
                prompt += f"\n**INJURY REPORT:**\n{real_time_data['injuries']}"
            
            if real_time_data.get('weather'):
                prompt += f"\n**WEATHER CONDITIONS:**\n{real_time_data['weather']}"
            
            if real_time_data.get('line_movement'):
                prompt += f"\n**LINE MOVEMENT:**\n{real_time_data['line_movement']}"
            
            if real_time_data.get('news_sentiment'):
                prompt += f"\n**NEWS SENTIMENT:**\n{real_time_data['news_sentiment']}"
        
        # Enhanced output format
        prompt += """
        
        **REQUIRED JSON OUTPUT FORMAT:**
        {
            "analysis": "comprehensive 200-word analysis",
            "predicted_winner": "exact team name",
            "confidence": 0.85,
            "spread_prediction": {
                "pick": "Team Name -3.5",
                "confidence": 0.80,
                "reasoning": "why this spread has value"
            },
            "total_prediction": {
                "pick": "Over 45.5",
                "confidence": 0.75,
                "reasoning": "factors affecting scoring"
            },
            "moneyline_value": {
                "pick": "Team Name",
                "confidence": 0.85,
                "odds_value": "strong/medium/weak"
            },
            "key_factors": [
                "Most important factor",
                "Second most important",
                "Third factor"
            ],
            "risk_factors": [
                "Main risk to prediction",
                "Secondary concern"
            ],
            "statistical_edge": {
                "metric": "specific stat advantage",
                "value": "quantified edge",
                "significance": "high/medium/low"
            },
            "betting_recommendation": {
                "primary_bet": "strongest recommendation",
                "unit_size": 1-5,
                "alternative_bet": "secondary option",
                "avoid": "what to avoid betting"
            },
            "confidence_breakdown": {
                "data_quality": 0.90,
                "matchup_clarity": 0.85,
                "injury_impact": 0.80,
                "weather_factor": 0.95,
                "motivation_level": 0.75
            }
        }
        
        **CRITICAL INSTRUCTIONS:**
        - Only recommend bets with 70%+ confidence
        - Consider injury reports heavily (reduce confidence by 15-25% for key injuries)
        - Weather impacts outdoor sports significantly
        - Line movement indicates sharp money - factor this in
        - Be conservative with confidence - better to pass than lose
        - Focus on value, not just picking winners
        """
        
        return prompt

    def fetch_real_time_data(self, game_data: Dict) -> Dict:
        """Fetch real-time data to enhance predictions"""
        real_time_data = {}
        
        try:
            # Injury reports (simulated - would use real API)
            real_time_data['injuries'] = self._get_injury_reports(game_data)
            
            # Weather data (simulated)
            real_time_data['weather'] = self._get_weather_data(game_data)
            
            # Line movement (simulated)
            real_time_data['line_movement'] = self._get_line_movement(game_data)
            
            # News sentiment (simulated)
            real_time_data['news_sentiment'] = self._get_news_sentiment(game_data)
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"⚠️ Real-time data fetch error: {e}")
        
        return real_time_data

    def _get_injury_reports(self, game_data: Dict) -> str:
        """Get current injury reports (simulated)"""
        home_team = game_data.get('home_team', {}).get('name', 'Home')
        away_team = game_data.get('away_team', {}).get('name', 'Away')
        
        # Simulated injury data - would connect to real API
        injury_scenarios = [
            f"✅ {home_team}: No significant injuries reported",
            f"⚠️ {home_team}: Star player questionable with minor injury",
            f"❌ {home_team}: Key starter ruled OUT for game",
            f"✅ {away_team}: Full roster available",
            f"⚠️ {away_team}: Role player day-to-day"
        ]
        
        import random
        return f"{random.choice(injury_scenarios[:3])}\n{random.choice(injury_scenarios[3:])}"

    def _get_weather_data(self, game_data: Dict) -> str:
        """Get weather conditions for outdoor games"""
        sport = game_data.get('sport', 'Unknown')
        venue = game_data.get('venue', 'Unknown')
        
        if sport in ['NFL', 'MLB', 'NCAAF'] and 'Dome' not in venue:
            # Outdoor game - weather matters
            weather_conditions = [
                "Clear, 72°F, Wind: 5mph - Ideal conditions",
                "Overcast, 65°F, Wind: 12mph - Moderate conditions", 
                "Rain expected, 58°F, Wind: 18mph - Challenging conditions",
                "Snow possible, 35°F, Wind: 22mph - Difficult conditions"
            ]
            import random
            return random.choice(weather_conditions)
        else:
            return "Indoor venue - Weather not a factor"

    def _get_line_movement(self, game_data: Dict) -> str:
        """Track betting line movements"""
        import random
        
        movements = [
            "Line moved 1.5 points toward home team - Sharp money detected",
            "Total moved from 45.5 to 47 - Public hammering Over",
            "Moneyline tightened - Respected money on underdog",
            "No significant line movement - Market consensus",
            "Reverse line movement - Fade the public opportunity"
        ]
        
        return random.choice(movements)

    def _get_news_sentiment(self, game_data: Dict) -> str:
        """Analyze recent news sentiment"""
        home_team = game_data.get('home_team', {}).get('name', 'Home')
        away_team = game_data.get('away_team', {}).get('name', 'Away')
        
        sentiments = [
            f"Positive momentum for {home_team} - Recent wins building confidence",
            f"Pressure on {away_team} - Must-win situation developing",
            f"Neutral sentiment - Both teams in similar situations",
            f"Negative news surrounding {home_team} - Distraction concerns",
            f"Motivational edge to {away_team} - Revenge game narrative"
        ]
        
        import random
        return random.choice(sentiments)

    def calculate_consensus_confidence(self, predictions: List[Dict]) -> float:
        """Calculate weighted confidence from multiple AI predictions"""
        if not predictions:
            return 0.0
        
        # Weight predictions by their individual confidence and data quality
        weighted_scores = []
        total_weight = 0
        
        for pred in predictions:
            confidence = pred.get('confidence', 0.5)
            data_quality = pred.get('confidence_breakdown', {}).get('data_quality', 0.8)
            
            # Weight = confidence * data_quality
            weight = confidence * data_quality
            weighted_scores.append(confidence * weight)
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return sum(weighted_scores) / total_weight

    def apply_kelly_criterion(self, prediction: Dict, odds: float = None) -> Dict:
        """Apply Kelly Criterion for optimal bet sizing"""
        confidence = prediction.get('confidence', 0.5)
        
        if not odds:
            # Estimate odds based on confidence
            if confidence >= 0.8:
                implied_odds = 1.25  # -400 (80% implied probability)
            elif confidence >= 0.7:
                implied_odds = 1.43  # -233 (70% implied probability)
            else:
                implied_odds = 2.0   # +100 (50% implied probability)
        else:
            implied_odds = odds
        
        # Kelly formula: f = (bp - q) / b
        # f = fraction of bankroll to bet
        # b = odds received on the wager
        # p = probability of winning
        # q = probability of losing (1 - p)
        
        p = confidence
        q = 1 - p
        b = implied_odds - 1
        
        kelly_fraction = (b * p - q) / b
        
        # Cap at 5% of bankroll for safety
        kelly_fraction = max(0, min(kelly_fraction, 0.05))
        
        return {
            'kelly_fraction': kelly_fraction,
            'recommended_units': min(kelly_fraction * 20, 5),  # Convert to unit scale (1-5)
            'bankroll_percentage': kelly_fraction * 100
        }

    def generate_performance_metrics(self, historical_predictions: List[Dict]) -> Dict:
        """Generate performance metrics for strategy refinement"""
        if not historical_predictions:
            return {'error': 'No historical data available'}
        
        correct_predictions = sum(1 for p in historical_predictions if p.get('result') == 'win')
        total_predictions = len(historical_predictions)
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # ROI calculation
        total_staked = sum(p.get('stake', 1) for p in historical_predictions)
        total_returned = sum(p.get('return', 0) for p in historical_predictions)
        roi = ((total_returned - total_staked) / total_staked * 100) if total_staked > 0 else 0
        
        # Confidence calibration
        high_conf_predictions = [p for p in historical_predictions if p.get('confidence', 0) >= 0.8]
        high_conf_accuracy = (
            sum(1 for p in high_conf_predictions if p.get('result') == 'win') / len(high_conf_predictions)
            if high_conf_predictions else 0
        )
        
        return {
            'overall_accuracy': accuracy,
            'total_predictions': total_predictions,
            'roi_percentage': roi,
            'high_confidence_accuracy': high_conf_accuracy,
            'high_confidence_count': len(high_conf_predictions),
            'avg_confidence': sum(p.get('confidence', 0) for p in historical_predictions) / total_predictions,
            'recommendation': self._get_strategy_recommendation(accuracy, roi, high_conf_accuracy)
        }

    def _get_strategy_recommendation(self, accuracy: float, roi: float, high_conf_accuracy: float) -> str:
        """Provide strategy recommendations based on performance"""
        if accuracy >= 0.6 and roi > 5:
            return "Strategy performing well - maintain current approach"
        elif accuracy >= 0.55 and high_conf_accuracy >= 0.7:
            return "Focus on high-confidence picks only - reduce volume"
        elif roi < 0:
            return "Strategy needs adjustment - review confidence calibration"
        else:
            return "Collect more data before making strategy changes"
