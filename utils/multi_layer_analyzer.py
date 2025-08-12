"""
🧠 Multi-Layer Analysis System
Quant Baseline → Real-time Adjustments → LLM Review
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import streamlit as st

class MultiLayerAnalyzer:
    """Advanced multi-layer analysis: Quantitative → Real-time → LLM → Final"""
    
    def __init__(self):
        self.quantitative_models = QuantitativeBaseline()
        self.realtime_adjuster = RealtimeAdjuster()
        self.llm_reviewer = LLMReviewer()
        
    def analyze_game_multilayer(self, game_data: Dict) -> Dict:
        """Complete multi-layer analysis pipeline"""
        
        analysis_start = datetime.now()
        
        # Layer 1: Quantitative Baseline Model
        quant_analysis = self.quantitative_models.analyze(game_data)
        
        # Layer 2: Real-time Data Adjustments
        realtime_analysis = self.realtime_adjuster.adjust(quant_analysis, game_data)
        
        # Layer 3: LLM Review and Enhancement
        llm_analysis = self.llm_reviewer.review_and_enhance(realtime_analysis, game_data)
        
        # Layer 4: Final Integration and Confidence Calibration
        final_analysis = self._integrate_layers(quant_analysis, realtime_analysis, llm_analysis)
        
        analysis_time = (datetime.now() - analysis_start).total_seconds()
        
        return {
            'final_prediction': final_analysis,
            'layer_breakdown': {
                'quantitative': quant_analysis,
                'realtime_adjusted': realtime_analysis,
                'llm_enhanced': llm_analysis
            },
            'analysis_metadata': {
                'total_time': analysis_time,
                'layers_processed': 4,
                'confidence_source': 'multi_layer_consensus',
                'reliability_score': final_analysis.get('reliability_score', 0.8)
            }
        }
    
    def _integrate_layers(self, quant: Dict, realtime: Dict, llm: Dict) -> Dict:
        """Intelligently integrate all analysis layers"""
        
        # Weight each layer based on reliability
        weights = {
            'quantitative': 0.4,  # Strong foundation
            'realtime': 0.3,      # Important adjustments
            'llm': 0.3           # Contextual intelligence
        }
        
        # Integrate predictions (if they agree, boost confidence)
        predictions = [
            quant.get('predicted_winner'),
            realtime.get('predicted_winner'), 
            llm.get('predicted_winner')
        ]
        
        # Find consensus
        prediction_counts = {}
        for pred in predictions:
            if pred:
                prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
        
        if prediction_counts:
            final_prediction = max(prediction_counts.keys(), key=lambda x: prediction_counts[x])
            consensus_strength = prediction_counts[final_prediction] / len([p for p in predictions if p])
        else:
            final_prediction = quant.get('predicted_winner', 'No Pick')
            consensus_strength = 0.33
        
        # Integrate confidence scores with consensus boost
        confidences = [
            quant.get('confidence', 0.5) * weights['quantitative'],
            realtime.get('confidence', 0.5) * weights['realtime'],
            llm.get('confidence', 0.5) * weights['llm']
        ]
        
        base_confidence = sum(confidences)
        
        # Apply consensus boost
        consensus_boost = (consensus_strength - 0.33) * 0.2  # Up to +20% for full consensus
        final_confidence = min(0.95, base_confidence + consensus_boost)
        
        # Integrate edge scores
        edge_scores = [
            quant.get('edge_score', 0.0),
            realtime.get('edge_score', 0.0),
            llm.get('edge_score', 0.0)
        ]
        final_edge = sum(e * w for e, w in zip(edge_scores, weights.values()))
        
        # Combine key factors
        all_factors = []
        for analysis in [quant, realtime, llm]:
            factors = analysis.get('key_factors', [])
            if isinstance(factors, list):
                all_factors.extend(factors)
            elif isinstance(factors, str):
                all_factors.append(factors)
        
        # Deduplicate and prioritize factors
        unique_factors = list(dict.fromkeys(all_factors))[:5]  # Top 5 unique factors
        
        return {
            'predicted_winner': final_prediction,
            'confidence': final_confidence,
            'edge_score': final_edge,
            'key_factors': unique_factors,
            'consensus_strength': consensus_strength,
            'layer_agreement': consensus_strength,
            'reliability_score': self._calculate_reliability(consensus_strength, final_confidence),
            'analysis_quality': 'multi_layer_consensus',
            'reasoning': f"Multi-layer consensus analysis with {consensus_strength:.1%} agreement"
        }
    
    def _calculate_reliability(self, consensus: float, confidence: float) -> float:
        """Calculate reliability score based on layer consensus and confidence"""
        
        # Higher reliability when layers agree and confidence is appropriate
        base_reliability = (consensus * 0.6) + (min(confidence, 0.85) * 0.4)
        
        # Penalty for overconfidence without strong consensus
        if confidence > 0.85 and consensus < 0.67:
            base_reliability *= 0.8  # 20% penalty
        
        return min(1.0, max(0.1, base_reliability))


class QuantitativeBaseline:
    """Layer 1: Pure quantitative analysis baseline"""
    
    def analyze(self, game_data: Dict) -> Dict:
        """Quantitative baseline using statistical models"""
        
        # Extract team data
        home_team = game_data.get('home_team', {})
        away_team = game_data.get('away_team', {})
        sport = game_data.get('sport', 'Unknown')
        
        # Calculate quantitative metrics
        home_strength = self._calculate_team_strength(home_team, sport)
        away_strength = self._calculate_team_strength(away_team, sport)
        
        # Home field advantage
        home_advantage = self._get_home_advantage(sport)
        adjusted_home_strength = home_strength + home_advantage
        
        # Calculate win probability using ELO-style rating
        strength_diff = adjusted_home_strength - away_strength
        win_probability = 1 / (1 + np.exp(-strength_diff / 400))  # ELO formula
        
        # Determine prediction
        if win_probability > 0.5:
            predicted_winner = home_team.get('name', 'Home')
            confidence = win_probability
        else:
            predicted_winner = away_team.get('name', 'Away')
            confidence = 1 - win_probability
        
        # Calculate edge score
        edge_score = abs(win_probability - 0.5) * 2  # Convert to 0-1 scale
        
        return {
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'edge_score': edge_score,
            'key_factors': [
                f"Team strength differential: {strength_diff:.1f}",
                f"Home advantage: +{home_advantage:.1f}",
                f"Win probability: {win_probability:.1%}"
            ],
            'quantitative_metrics': {
                'home_strength': home_strength,
                'away_strength': away_strength,
                'home_advantage': home_advantage,
                'strength_differential': strength_diff
            }
        }
    
    def _calculate_team_strength(self, team: Dict, sport: str) -> float:
        """Calculate team strength rating"""
        
        # Base rating from record if available
        record = team.get('record', '0-0')
        try:
            wins, losses = map(int, record.split('-')[:2])
            total_games = wins + losses
            win_rate = wins / total_games if total_games > 0 else 0.5
            base_rating = (win_rate - 0.5) * 800 + 1500  # Convert to ELO-style rating
        except:
            base_rating = 1500  # Default neutral rating
        
        # Adjust for sport-specific factors
        sport_adjustments = {
            'NFL': 1.0,
            'NBA': 1.2,    # More predictable
            'MLB': 0.8,    # More random
            'NHL': 0.9,
            'NCAAF': 0.7,  # High variance
            'NCAAB': 0.6   # March Madness
        }
        
        adjustment = sport_adjustments.get(sport, 1.0)
        return base_rating * adjustment
    
    def _get_home_advantage(self, sport: str) -> float:
        """Get sport-specific home field advantage"""
        
        home_advantages = {
            'NFL': 57,     # ~3 point spread equivalent
            'NBA': 63,     # ~3.5 points
            'MLB': 54,     # ~3% win rate boost
            'NHL': 60,     # ~3.2% boost
            'NCAAF': 75,   # Larger college crowds
            'NCAAB': 85    # Biggest home advantage
        }
        
        return home_advantages.get(sport, 50)


class RealtimeAdjuster:
    """Layer 2: Real-time data adjustments"""
    
    def adjust(self, baseline_analysis: Dict, game_data: Dict) -> Dict:
        """Apply real-time adjustments to baseline analysis"""
        
        # Start with baseline
        adjusted_analysis = baseline_analysis.copy()
        
        # Collect real-time adjustments
        adjustments = []
        confidence_modifier = 1.0
        edge_modifier = 1.0
        
        # Injury adjustments
        injury_impact = self._assess_injury_impact(game_data)
        if injury_impact['significant']:
            confidence_modifier *= injury_impact['confidence_impact']
            adjustments.append(f"Key injury impact: {injury_impact['description']}")
        
        # Weather adjustments (for outdoor sports)
        weather_impact = self._assess_weather_impact(game_data)
        if weather_impact['significant']:
            confidence_modifier *= weather_impact['confidence_impact']
            edge_modifier *= weather_impact['edge_impact']
            adjustments.append(f"Weather factor: {weather_impact['description']}")
        
        # Line movement adjustments
        line_movement = self._assess_line_movement(game_data)
        if line_movement['significant']:
            confidence_modifier *= line_movement['confidence_impact']
            adjustments.append(f"Sharp money: {line_movement['description']}")
        
        # News sentiment adjustments
        news_impact = self._assess_news_sentiment(game_data)
        if news_impact['significant']:
            confidence_modifier *= news_impact['confidence_impact']
            adjustments.append(f"News sentiment: {news_impact['description']}")
        
        # Apply adjustments
        adjusted_analysis['confidence'] = min(0.95, baseline_analysis['confidence'] * confidence_modifier)
        adjusted_analysis['edge_score'] = min(1.0, baseline_analysis['edge_score'] * edge_modifier)
        
        # Add real-time factors
        realtime_factors = baseline_analysis.get('key_factors', []) + adjustments
        adjusted_analysis['key_factors'] = realtime_factors[:5]  # Keep top 5
        
        adjusted_analysis['realtime_adjustments'] = {
            'confidence_modifier': confidence_modifier,
            'edge_modifier': edge_modifier,
            'adjustments_applied': len(adjustments),
            'adjustment_details': adjustments
        }
        
        return adjusted_analysis
    
    def _assess_injury_impact(self, game_data: Dict) -> Dict:
        """Assess impact of injuries on the game"""
        
        # Simulate injury assessment (in real implementation, would check injury reports)
        injury_probability = np.random.random()
        
        if injury_probability < 0.3:  # 30% chance of significant injury
            severity = np.random.choice(['minor', 'moderate', 'major'], p=[0.6, 0.3, 0.1])
            
            impact_map = {
                'minor': {'confidence_impact': 0.98, 'description': 'Minor injury concerns'},
                'moderate': {'confidence_impact': 0.93, 'description': 'Key player questionable'},
                'major': {'confidence_impact': 0.85, 'description': 'Star player ruled out'}
            }
            
            return {
                'significant': True,
                **impact_map[severity]
            }
        
        return {'significant': False}
    
    def _assess_weather_impact(self, game_data: Dict) -> Dict:
        """Assess weather impact for outdoor games"""
        
        sport = game_data.get('sport', '')
        
        # Only apply to outdoor sports
        if sport not in ['NFL', 'MLB', 'NCAAF']:
            return {'significant': False}
        
        # Simulate weather conditions
        weather_severity = np.random.random()
        
        if weather_severity > 0.7:  # 30% chance of significant weather
            conditions = np.random.choice(['wind', 'rain', 'snow', 'extreme_cold'])
            
            impact_map = {
                'wind': {'confidence_impact': 0.95, 'edge_impact': 1.1, 'description': 'Strong winds affecting passing'},
                'rain': {'confidence_impact': 0.92, 'edge_impact': 1.15, 'description': 'Rain favoring ground game'},
                'snow': {'confidence_impact': 0.88, 'edge_impact': 1.2, 'description': 'Snow creating unpredictable conditions'},
                'extreme_cold': {'confidence_impact': 0.90, 'edge_impact': 1.12, 'description': 'Extreme cold affecting performance'}
            }
            
            return {
                'significant': True,
                **impact_map[conditions]
            }
        
        return {'significant': False}
    
    def _assess_line_movement(self, game_data: Dict) -> Dict:
        """Assess betting line movement patterns"""
        
        # Simulate line movement analysis
        movement_significance = np.random.random()
        
        if movement_significance > 0.6:  # 40% chance of significant movement
            direction = np.random.choice(['sharp_money', 'public_fade', 'steam_move'])
            
            impact_map = {
                'sharp_money': {'confidence_impact': 1.08, 'description': 'Sharp money moving line'},
                'public_fade': {'confidence_impact': 1.05, 'description': 'Contrarian opportunity detected'},
                'steam_move': {'confidence_impact': 1.12, 'description': 'Steam move indicating strong consensus'}
            }
            
            return {
                'significant': True,
                **impact_map[direction]
            }
        
        return {'significant': False}
    
    def _assess_news_sentiment(self, game_data: Dict) -> Dict:
        """Assess news sentiment impact"""
        
        # Simulate news sentiment analysis
        news_impact = np.random.random()
        
        if news_impact > 0.75:  # 25% chance of significant news
            sentiment = np.random.choice(['positive', 'negative', 'controversy'])
            
            impact_map = {
                'positive': {'confidence_impact': 1.03, 'description': 'Positive team news'},
                'negative': {'confidence_impact': 0.97, 'description': 'Negative team developments'},
                'controversy': {'confidence_impact': 0.94, 'description': 'Team distraction/controversy'}
            }
            
            return {
                'significant': True,
                **impact_map[sentiment]
            }
        
        return {'significant': False}


class LLMReviewer:
    """Layer 3: LLM review and contextual enhancement"""
    
    def review_and_enhance(self, realtime_analysis: Dict, game_data: Dict) -> Dict:
        """LLM review of quantitative + real-time analysis"""
        
        # In a real implementation, this would call GPT-4/Gemini
        # For now, simulate intelligent review
        
        enhanced_analysis = realtime_analysis.copy()
        
        # Simulate LLM contextual insights
        contextual_factors = self._generate_contextual_insights(game_data, realtime_analysis)
        
        # LLM confidence adjustment based on context
        llm_confidence_adjustment = self._llm_confidence_review(realtime_analysis, contextual_factors)
        
        # Apply LLM adjustments
        enhanced_analysis['confidence'] = min(0.95, realtime_analysis['confidence'] * llm_confidence_adjustment)
        
        # Add LLM insights
        llm_factors = contextual_factors['insights']
        combined_factors = realtime_analysis.get('key_factors', []) + llm_factors
        enhanced_analysis['key_factors'] = combined_factors[:5]
        
        enhanced_analysis['llm_enhancements'] = {
            'confidence_adjustment': llm_confidence_adjustment,
            'contextual_insights': contextual_factors,
            'reasoning_quality': 'enhanced_contextual'
        }
        
        return enhanced_analysis
    
    def _generate_contextual_insights(self, game_data: Dict, analysis: Dict) -> Dict:
        """Generate contextual insights that LLM would provide"""
        
        sport = game_data.get('sport', 'Unknown')
        
        # Simulate sport-specific contextual insights
        contextual_insights = []
        
        if sport == 'NFL':
            insights = [
                "Divisional rivalry adds unpredictability",
                "Recent coaching changes affecting team chemistry",
                "Playoff implications increasing motivation",
                "Historical head-to-head trends favor underdog"
            ]
        elif sport == 'NBA':
            insights = [
                "Back-to-back game fatigue factor",
                "Star player rest management consideration",
                "Recent trade affecting team dynamics",
                "Pace of play mismatch creating opportunity"
            ]
        elif sport == 'MLB':
            insights = [
                "Pitcher matchup heavily favors one side",
                "Bullpen usage patterns from recent games",
                "Weather conditions affecting ball flight",
                "Team's recent offensive surge/slump"
            ]
        else:
            insights = [
                "Recent form trend analysis",
                "Motivational factors consideration",
                "Tactical matchup advantages",
                "Historical performance patterns"
            ]
        
        # Randomly select 2-3 insights
        selected_insights = np.random.choice(insights, size=min(3, len(insights)), replace=False).tolist()
        
        return {
            'insights': selected_insights,
            'context_quality': 'high',
            'sport_specific': True
        }
    
    def _llm_confidence_review(self, analysis: Dict, contextual_factors: Dict) -> float:
        """LLM review of confidence level appropriateness"""
        
        base_confidence = analysis.get('confidence', 0.5)
        
        # LLM would consider:
        # 1. Consistency of factors
        # 2. Historical context
        # 3. Uncertainty indicators
        # 4. Market efficiency
        
        # Simulate LLM's conservative adjustment
        if base_confidence > 0.85:
            # LLM tends to be more conservative with very high confidence
            return 0.95
        elif base_confidence > 0.75:
            # Slight conservative adjustment
            return 0.98
        elif base_confidence < 0.6:
            # Boost very low confidence if factors are strong
            return 1.05
        else:
            # Minimal adjustment for moderate confidence
            return 1.02
