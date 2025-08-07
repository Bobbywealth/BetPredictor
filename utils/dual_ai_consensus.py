import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np
from utils.ai_analysis import AIGameAnalyzer
from utils.cache_manager import CacheManager

class DualAIConsensusEngine:
    """Advanced system combining ChatGPT and Gemini analyses for high-confidence picks"""
    
    def __init__(self):
        self.ai_analyzer = AIGameAnalyzer()
        self.cache = CacheManager()
        
        # Success algorithm weights
        self.weights = {
            'ai_consensus': 0.35,      # Both AIs agree
            'confidence_score': 0.25,  # Average confidence
            'market_odds': 0.20,       # Odds-based value
            'statistical_edge': 0.20   # Statistical advantages
        }
    
    def analyze_game_dual_ai(self, game_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive dual AI analysis"""
        game_id = game_data.get('game_id', 'unknown')
        cache_key = f"dual_ai_analysis_{game_id}_{hash(str(game_data))}"
        
        # Check cache first
        cached_result = self.cache.get_cached_data(cache_key, ttl_minutes=45)
        if cached_result is not None:
            return cached_result
        
        # Get both AI analyses
        with st.spinner("Getting ChatGPT analysis..."):
            openai_analysis = self.ai_analyzer.analyze_game_with_openai(game_data)
        
        with st.spinner("Getting Gemini analysis..."):
            try:
                gemini_analysis = self.ai_analyzer.analyze_game_with_gemini(game_data)
            except Exception:
                gemini_analysis = {"error": "Gemini unavailable"}
        
        # Generate consensus analysis
        consensus_result = self._generate_consensus(
            game_data, openai_analysis, gemini_analysis
        )
        
        # Cache the result
        self.cache.set_cached_data(cache_key, consensus_result)
        return consensus_result
    
    def _generate_consensus(self, game_data: Dict, openai_result: Dict, gemini_result: Dict) -> Dict[str, Any]:
        """Generate consensus analysis from both AI results"""
        
        # Extract predictions from both AIs
        openai_valid = 'error' not in openai_result
        gemini_valid = 'error' not in gemini_result
        
        if not openai_valid and not gemini_valid:
            return {
                'error': 'Both AI analyses failed',
                'recommendation': 'SKIP',
                'confidence': 0.0
            }
        
        # Initialize consensus data
        consensus = {
            'game_info': {
                'home_team': game_data.get('home_team', {}).get('name', 'Unknown') if isinstance(game_data.get('home_team'), dict) else game_data.get('home_team', 'Unknown'),
                'away_team': game_data.get('away_team', {}).get('name', 'Unknown') if isinstance(game_data.get('away_team'), dict) else game_data.get('away_team', 'Unknown'),
                'sport': game_data.get('sport', 'Unknown'),
                'date': game_data.get('date', 'Unknown'),
                'time': game_data.get('time', 'Unknown')
            },
            'ai_analyses': {
                'openai': openai_result if openai_valid else {'error': 'Analysis failed'},
                'gemini': gemini_result if gemini_valid else {'error': 'Analysis failed'}
            }
        }
        
        # Generate consensus pick
        pick_analysis = self._calculate_consensus_pick(openai_result, gemini_result, game_data)
        consensus.update(pick_analysis)
        
        return consensus
    
    def _calculate_consensus_pick(self, openai_result: Dict, gemini_result: Dict, game_data: Dict) -> Dict[str, Any]:
        """Calculate consensus pick using advanced algorithms"""
        
        # Extract predictions
        openai_pick = openai_result.get('predicted_winner', '') if 'error' not in openai_result else ''
        gemini_pick = gemini_result.get('prediction', '') if 'error' not in gemini_result else ''
        
        openai_confidence = openai_result.get('confidence', 0.5) if 'error' not in openai_result else 0.0
        gemini_confidence = gemini_result.get('confidence_score', 0.5) if 'error' not in gemini_result else 0.0
        
        # Consensus agreement check
        picks_agree = self._picks_agree(openai_pick, gemini_pick, game_data)
        
        # Calculate composite confidence
        if picks_agree and openai_pick and gemini_pick:
            # Both AIs agree - high confidence boost
            base_confidence = (openai_confidence + gemini_confidence) / 2
            consensus_bonus = 0.15  # 15% bonus for agreement
            final_confidence = min(base_confidence + consensus_bonus, 1.0)
            consensus_pick = openai_pick
            agreement_status = 'STRONG_CONSENSUS'
            
        elif openai_pick and gemini_pick and not picks_agree:
            # AIs disagree - use higher confidence pick
            if openai_confidence > gemini_confidence:
                consensus_pick = openai_pick
                final_confidence = openai_confidence * 0.8  # Reduce confidence due to disagreement
            else:
                consensus_pick = gemini_pick
                final_confidence = gemini_confidence * 0.8
            agreement_status = 'DISAGREEMENT'
            
        elif openai_pick and not gemini_pick:
            # Only OpenAI has pick
            consensus_pick = openai_pick
            final_confidence = openai_confidence * 0.7  # Reduce for single AI
            agreement_status = 'SINGLE_AI_OPENAI'
            
        elif gemini_pick and not openai_pick:
            # Only Gemini has pick
            consensus_pick = gemini_pick
            final_confidence = gemini_confidence * 0.7
            agreement_status = 'SINGLE_AI_GEMINI'
            
        else:
            # No valid picks
            consensus_pick = 'NO_PICK'
            final_confidence = 0.0
            agreement_status = 'NO_CONSENSUS'
        
        # Apply Python success algorithm
        success_metrics = self._calculate_success_metrics(
            openai_result, gemini_result, game_data, final_confidence
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            consensus_pick, final_confidence, agreement_status, success_metrics
        )
        
        return {
            'consensus_pick': consensus_pick,
            'consensus_confidence': final_confidence,
            'agreement_status': agreement_status,
            'success_metrics': success_metrics,
            'recommendation': recommendation,
            'pick_reasoning': self._generate_pick_reasoning(
                openai_result, gemini_result, agreement_status
            )
        }
    
    def _picks_agree(self, openai_pick: str, gemini_pick: str, game_data: Dict) -> bool:
        """Check if both AI picks agree"""
        if not openai_pick or not gemini_pick:
            return False
        
        home_team = game_data.get('home_team', {}).get('name', '') if isinstance(game_data.get('home_team'), dict) else game_data.get('home_team', '')
        away_team = game_data.get('away_team', {}).get('name', '') if isinstance(game_data.get('away_team'), dict) else game_data.get('away_team', '')
        
        # Normalize team names for comparison
        openai_norm = openai_pick.lower().strip()
        gemini_norm = gemini_pick.lower().strip()
        home_norm = home_team.lower().strip()
        away_norm = away_team.lower().strip()
        
        # Check if both pick the same team
        openai_picks_home = home_norm in openai_norm
        openai_picks_away = away_norm in openai_norm
        gemini_picks_home = home_norm in gemini_norm
        gemini_picks_away = away_norm in gemini_norm
        
        return (openai_picks_home and gemini_picks_home) or (openai_picks_away and gemini_picks_away)
    
    def _calculate_success_metrics(self, openai_result: Dict, gemini_result: Dict, game_data: Dict, confidence: float) -> Dict[str, Any]:
        """Calculate Python-based success metrics for winning picks"""
        
        metrics = {
            'edge_score': 0.0,
            'value_rating': 'LOW',
            'risk_level': 'HIGH',
            'success_probability': 0.0,
            'kelly_criterion': 0.0,
            'expected_value': 0.0
        }
        
        try:
            # Edge Score Calculation
            edge_factors = []
            
            # AI confidence edge
            if confidence > 0.75:
                edge_factors.append(0.3)
            elif confidence > 0.65:
                edge_factors.append(0.2)
            elif confidence > 0.55:
                edge_factors.append(0.1)
            
            # Key factors analysis
            openai_factors = openai_result.get('key_factors', []) if 'error' not in openai_result else []
            gemini_factors = gemini_result.get('critical_factors', []) if 'error' not in gemini_result else []
            
            total_factors = len(openai_factors) + len(gemini_factors)
            if total_factors >= 5:
                edge_factors.append(0.2)
            elif total_factors >= 3:
                edge_factors.append(0.1)
            
            # Risk assessment
            openai_risk = openai_result.get('risk_level', 'MEDIUM') if 'error' not in openai_result else 'HIGH'
            if openai_risk == 'LOW':
                edge_factors.append(0.15)
                metrics['risk_level'] = 'LOW'
            elif openai_risk == 'MEDIUM':
                edge_factors.append(0.05)
                metrics['risk_level'] = 'MEDIUM'
            
            # Calculate final edge score
            metrics['edge_score'] = min(sum(edge_factors), 1.0)
            
            # Value Rating
            if metrics['edge_score'] >= 0.6:
                metrics['value_rating'] = 'EXCELLENT'
            elif metrics['edge_score'] >= 0.4:
                metrics['value_rating'] = 'GOOD'
            elif metrics['edge_score'] >= 0.25:
                metrics['value_rating'] = 'FAIR'
            else:
                metrics['value_rating'] = 'POOR'
            
            # Success Probability (Bayesian-inspired)
            base_prob = confidence
            edge_adjustment = metrics['edge_score'] * 0.15
            metrics['success_probability'] = min(base_prob + edge_adjustment, 0.95)
            
            # Kelly Criterion calculation (if odds available)
            home_odds = game_data.get('home_odds', 'N/A')
            away_odds = game_data.get('away_odds', 'N/A')
            
            if home_odds != 'N/A' and away_odds != 'N/A':
                try:
                    # Convert American odds to decimal for Kelly calculation
                    prob_win = metrics['success_probability']
                    
                    # Simplified Kelly - would need actual odds matching in production
                    if prob_win > 0.5:
                        kelly_fraction = (prob_win * 2 - 1) / 1  # Simplified
                        metrics['kelly_criterion'] = min(kelly_fraction, 0.25)  # Cap at 25%
                        
                        # Expected value calculation
                        metrics['expected_value'] = (prob_win * 1.0) - ((1 - prob_win) * 1.0)
                except:
                    pass
            
        except Exception as e:
            # Fallback metrics
            metrics['edge_score'] = confidence * 0.5
            metrics['success_probability'] = confidence
        
        return metrics
    
    def _generate_recommendation(self, pick: str, confidence: float, agreement: str, metrics: Dict) -> Dict[str, Any]:
        """Generate final recommendation with confidence levels"""
        
        # Recommendation levels
        rec_data = {
            'action': 'SKIP',
            'strength': 'WEAK',
            'reasoning': [],
            'risk_warning': True
        }
        
        # Decision algorithm
        edge_score = metrics.get('edge_score', 0.0)
        success_prob = metrics.get('success_probability', 0.0)
        value_rating = metrics.get('value_rating', 'POOR')
        
        # High confidence criteria
        if (confidence >= 0.8 and agreement == 'STRONG_CONSENSUS' and 
            edge_score >= 0.5 and success_prob >= 0.7):
            rec_data['action'] = 'STRONG_BET'
            rec_data['strength'] = 'VERY_HIGH'
            rec_data['reasoning'] = [
                'Both AIs strongly agree',
                f'High confidence: {confidence:.1%}',
                f'Strong edge score: {edge_score:.2f}',
                f'Success probability: {success_prob:.1%}'
            ]
            rec_data['risk_warning'] = False
            
        elif (confidence >= 0.7 and agreement in ['STRONG_CONSENSUS', 'SINGLE_AI_OPENAI', 'SINGLE_AI_GEMINI'] and
              edge_score >= 0.35):
            rec_data['action'] = 'MODERATE_BET'
            rec_data['strength'] = 'HIGH'
            rec_data['reasoning'] = [
                'Good AI consensus or single strong pick',
                f'Solid confidence: {confidence:.1%}',
                f'Edge score: {edge_score:.2f}',
                f'Value rating: {value_rating}'
            ]
            
        elif confidence >= 0.6 and edge_score >= 0.25:
            rec_data['action'] = 'SMALL_BET'
            rec_data['strength'] = 'MEDIUM'
            rec_data['reasoning'] = [
                'Decent analysis support',
                f'Moderate confidence: {confidence:.1%}',
                f'Some edge identified: {edge_score:.2f}'
            ]
            
        elif confidence >= 0.5:
            rec_data['action'] = 'LEAN'
            rec_data['strength'] = 'LOW'
            rec_data['reasoning'] = [
                'Weak signal detected',
                f'Low confidence: {confidence:.1%}',
                'Consider for entertainment only'
            ]
        
        # Add specific warnings
        if agreement == 'DISAGREEMENT':
            rec_data['reasoning'].append('⚠️ AIs disagree - proceed with caution')
        
        if metrics.get('risk_level') == 'HIGH':
            rec_data['reasoning'].append('⚠️ High risk factors identified')
        
        return rec_data
    
    def _generate_pick_reasoning(self, openai_result: Dict, gemini_result: Dict, agreement_status: str) -> List[str]:
        """Generate detailed reasoning for the pick"""
        reasoning = []
        
        if agreement_status == 'STRONG_CONSENSUS':
            reasoning.append("🎯 Both ChatGPT and Gemini agree on this pick")
            
            # Combine key factors from both
            openai_factors = openai_result.get('key_factors', []) if 'error' not in openai_result else []
            gemini_factors = gemini_result.get('critical_factors', []) if 'error' not in gemini_result else []
            
            all_factors = openai_factors + gemini_factors
            if all_factors:
                reasoning.append("📊 Combined analysis factors:")
                for factor in all_factors[:5]:  # Limit to top 5
                    reasoning.append(f"  • {factor}")
        
        elif agreement_status == 'DISAGREEMENT':
            reasoning.append("⚠️ AI models disagree - using higher confidence pick")
            
            openai_conf = openai_result.get('confidence', 0) if 'error' not in openai_result else 0
            gemini_conf = gemini_result.get('confidence_score', 0) if 'error' not in gemini_result else 0
            
            if openai_conf > gemini_conf:
                reasoning.append(f"📈 ChatGPT shows higher confidence ({openai_conf:.1%})")
            else:
                reasoning.append(f"📈 Gemini shows higher confidence ({gemini_conf:.1%})")
        
        elif agreement_status.startswith('SINGLE_AI'):
            ai_name = 'ChatGPT' if 'OPENAI' in agreement_status else 'Gemini'
            reasoning.append(f"🤖 Based on {ai_name} analysis only")
        
        else:
            reasoning.append("❌ No clear AI consensus - recommend skipping")
        
        return reasoning

class WinningPicksGenerator:
    """Generate high-confidence winning picks using dual AI consensus"""
    
    def __init__(self):
        self.consensus_engine = DualAIConsensusEngine()
        self.cache = CacheManager()
    
    def generate_daily_picks(self, games_df: pd.DataFrame, max_picks: int = 5) -> pd.DataFrame:
        """Generate top winning picks for the day"""
        
        if len(games_df) == 0:
            return pd.DataFrame()
        
        # Cache key for daily picks
        date_str = games_df['date'].iloc[0] if 'date' in games_df.columns else 'unknown'
        cache_key = f"daily_picks_{date_str}_{len(games_df)}_{max_picks}"
        
        # Check cache
        cached_picks = self.cache.get_cached_data(cache_key, ttl_minutes=30)
        if cached_picks is not None:
            return cached_picks
        
        picks_data = []
        
        # Analyze each game
        with st.spinner(f"Analyzing {len(games_df)} games for winning picks..."):
            for idx, game in games_df.iterrows():
                try:
                    # Convert game data to dict
                    game_dict = game.to_dict()
                    
                    # Get dual AI analysis
                    analysis = self.consensus_engine.analyze_game_dual_ai(game_dict)
                    
                    if 'error' not in analysis:
                        # Extract pick data
                        pick_data = {
                            'game_id': game.get('game_id', f'game_{idx}'),
                            'home_team': analysis['game_info']['home_team'],
                            'away_team': analysis['game_info']['away_team'],
                            'sport': analysis['game_info']['sport'],
                            'date': analysis['game_info']['date'],
                            'time': analysis['game_info']['time'],
                            'consensus_pick': analysis.get('consensus_pick', 'NO_PICK'),
                            'confidence': analysis.get('consensus_confidence', 0.0),
                            'agreement_status': analysis.get('agreement_status', 'UNKNOWN'),
                            'edge_score': analysis.get('success_metrics', {}).get('edge_score', 0.0),
                            'success_probability': analysis.get('success_metrics', {}).get('success_probability', 0.0),
                            'value_rating': analysis.get('success_metrics', {}).get('value_rating', 'POOR'),
                            'recommendation_action': analysis.get('recommendation', {}).get('action', 'SKIP'),
                            'recommendation_strength': analysis.get('recommendation', {}).get('strength', 'WEAK'),
                            'pick_reasoning': analysis.get('pick_reasoning', []),
                            'full_analysis': analysis
                        }
                        
                        # Only include actionable picks
                        if pick_data['recommendation_action'] != 'SKIP':
                            picks_data.append(pick_data)
                
                except Exception as e:
                    continue
        
        # Convert to DataFrame and sort by confidence and edge score
        if picks_data:
            picks_df = pd.DataFrame(picks_data)
            
            # Create composite score for ranking
            picks_df['composite_score'] = (
                picks_df['confidence'] * 0.4 +
                picks_df['edge_score'] * 0.4 +
                picks_df['success_probability'] * 0.2
            )
            
            # Sort by composite score
            picks_df = picks_df.sort_values('composite_score', ascending=False)
            
            # Limit to max picks
            final_picks = picks_df.head(max_picks)
            
            # Cache the results
            self.cache.set_cached_data(cache_key, final_picks)
            
            return final_picks
        
        return pd.DataFrame()
    
    def get_pick_summary(self, picks_df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for the picks"""
        
        if len(picks_df) == 0:
            return {'total_picks': 0, 'message': 'No qualifying picks found'}
        
        summary = {
            'total_picks': len(picks_df),
            'avg_confidence': picks_df['confidence'].mean(),
            'avg_edge_score': picks_df['edge_score'].mean(),
            'avg_success_prob': picks_df['success_probability'].mean(),
            'strong_picks': len(picks_df[picks_df['recommendation_strength'].isin(['VERY_HIGH', 'HIGH'])]),
            'sports_breakdown': picks_df['sport'].value_counts().to_dict(),
            'recommendation_breakdown': picks_df['recommendation_action'].value_counts().to_dict(),
            'consensus_breakdown': picks_df['agreement_status'].value_counts().to_dict()
        }
        
        return summary