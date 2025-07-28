import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import json
from utils.cache_manager import CacheManager
from utils.ai_analysis import AIGameAnalyzer

class DeepGameAnalyzer:
    """Comprehensive deep analysis for all games in the system"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.ai_analyzer = AIGameAnalyzer()
    
    def perform_comprehensive_analysis(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Perform comprehensive analysis on all games"""
        if len(games_df) == 0:
            return games_df
        
        # Create cache key for comprehensive analysis
        games_signature = self._create_games_signature(games_df)
        cache_key = f"comprehensive_analysis_{games_signature}"
        
        # Check cache first
        cached_analysis = self.cache.get_cached_data(cache_key, ttl_minutes=45)
        if cached_analysis is not None:
            return cached_analysis
        
        # Perform deep analysis
        analyzed_games = games_df.copy()
        
        with st.spinner("Performing comprehensive game analysis..."):
            # Add statistical analysis
            analyzed_games = self._add_statistical_analysis(analyzed_games)
            
            # Add market analysis (if odds available)
            analyzed_games = self._add_market_analysis(analyzed_games)
            
            # Add team form analysis
            analyzed_games = self._add_team_form_analysis(analyzed_games)
            
            # Add value assessment
            analyzed_games = self._add_value_assessment(analyzed_games)
            
            # Add recommendation scores
            analyzed_games = self._add_recommendation_scores(analyzed_games)
        
        # Cache the comprehensive analysis
        self.cache.set_cached_data(cache_key, analyzed_games)
        return analyzed_games
    
    def get_game_deep_insights(self, game_data: pd.Series) -> Dict[str, Any]:
        """Get deep insights for a specific game"""
        game_id = game_data.get('game_id', 'unknown')
        cache_key = f"deep_insights_{game_id}_{hash(str(game_data))}"
        
        # Check cache
        cached_insights = self.cache.get_cached_data(cache_key, ttl_minutes=30)
        if cached_insights is not None:
            return cached_insights
        
        # Generate deep insights
        insights = {
            'statistical_breakdown': self._get_statistical_breakdown(game_data),
            'market_sentiment': self._analyze_market_sentiment(game_data),
            'historical_context': self._get_historical_context(game_data),
            'key_factors': self._identify_key_factors(game_data),
            'risk_assessment': self._assess_risk_factors(game_data),
            'value_proposition': self._evaluate_value_proposition(game_data),
            'expert_consensus': self._simulate_expert_consensus(game_data),
            'betting_angles': self._identify_betting_angles(game_data)
        }
        
        # Cache insights
        self.cache.set_cached_data(cache_key, insights)
        return insights
    
    def batch_ai_analysis(self, games_df: pd.DataFrame, max_games: int = 10) -> pd.DataFrame:
        """Perform AI analysis on top games efficiently"""
        if len(games_df) == 0:
            return games_df
        
        # Select top games for AI analysis
        if 'interest_score' in games_df.columns:
            top_games = games_df.nlargest(max_games, 'interest_score')
        else:
            top_games = games_df.head(max_games)
        
        analyzed_games = games_df.copy()
        
        # Batch process AI analysis
        for idx in top_games.index:
            game = games_df.loc[idx]
            
            # Check if AI analysis already cached
            ai_cache_key = f"ai_analysis_batch_{game.get('game_id', idx)}"
            cached_ai = self.cache.get_cached_data(ai_cache_key, ttl_minutes=60)
            
            if cached_ai is not None:
                analyzed_games.loc[idx, 'ai_prediction'] = cached_ai.get('prediction', 'N/A')
                analyzed_games.loc[idx, 'ai_confidence'] = cached_ai.get('confidence', 0.5)
                analyzed_games.loc[idx, 'ai_analysis'] = cached_ai.get('analysis', 'Analysis available')
            else:
                # Generate new AI analysis
                try:
                    ai_result = self.ai_analyzer.analyze_game_with_openai(game.to_dict())
                    
                    if 'error' not in ai_result:
                        analyzed_games.loc[idx, 'ai_prediction'] = ai_result.get('predicted_winner', 'N/A')
                        analyzed_games.loc[idx, 'ai_confidence'] = ai_result.get('confidence', 0.5)
                        analyzed_games.loc[idx, 'ai_analysis'] = ai_result.get('analysis', 'Analysis complete')
                        
                        # Cache the result
                        self.cache.set_cached_data(ai_cache_key, ai_result)
                    else:
                        analyzed_games.loc[idx, 'ai_prediction'] = 'Error'
                        analyzed_games.loc[idx, 'ai_confidence'] = 0.0
                        analyzed_games.loc[idx, 'ai_analysis'] = 'Analysis failed'
                        
                except Exception as e:
                    analyzed_games.loc[idx, 'ai_prediction'] = 'Error'
                    analyzed_games.loc[idx, 'ai_confidence'] = 0.0
                    analyzed_games.loc[idx, 'ai_analysis'] = f'Error: {str(e)}'
        
        return analyzed_games
    
    def _create_games_signature(self, games_df: pd.DataFrame) -> str:
        """Create a unique signature for the games dataset"""
        # Use game IDs and dates to create signature
        signature_data = {
            'game_count': len(games_df),
            'date_range': f"{games_df['date'].min()}_{games_df['date'].max()}" if 'date' in games_df.columns else 'no_dates',
            'sports': sorted(games_df['sport'].unique().tolist()) if 'sport' in games_df.columns else []
        }
        
        signature_str = json.dumps(signature_data, sort_keys=True)
        return str(hash(signature_str))[:12]
    
    def _add_statistical_analysis(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical analysis metrics"""
        games_df = games_df.copy()
        
        # Interest score based on multiple factors
        games_df['interest_score'] = games_df.apply(self._calculate_interest_score, axis=1)
        
        # Competition level
        games_df['competition_level'] = games_df.apply(self._assess_competition_level, axis=1)
        
        # Viewing recommendation
        games_df['viewing_rec'] = games_df.apply(self._generate_viewing_recommendation, axis=1)
        
        return games_df
    
    def _add_market_analysis(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add betting market analysis"""
        games_df = games_df.copy()
        
        if 'home_odds' in games_df.columns and 'away_odds' in games_df.columns:
            games_df['market_efficiency'] = games_df.apply(self._assess_market_efficiency, axis=1)
            games_df['implied_probabilities'] = games_df.apply(self._calculate_implied_probabilities, axis=1)
            games_df['betting_value'] = games_df.apply(self._assess_betting_value, axis=1)
        else:
            games_df['market_efficiency'] = 'No odds data'
            games_df['implied_probabilities'] = 'N/A'
            games_df['betting_value'] = 'N/A'
        
        return games_df
    
    def _add_team_form_analysis(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add team form and momentum analysis"""
        games_df = games_df.copy()
        
        # Simulate team form analysis (would use real data in production)
        games_df['home_form'] = games_df.apply(lambda x: self._simulate_team_form(), axis=1)
        games_df['away_form'] = games_df.apply(lambda x: self._simulate_team_form(), axis=1)
        games_df['momentum_factor'] = games_df.apply(self._calculate_momentum_factor, axis=1)
        
        return games_df
    
    def _add_value_assessment(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add comprehensive value assessment"""
        games_df = games_df.copy()
        
        # Overall value score
        games_df['value_score'] = games_df.apply(self._calculate_value_score, axis=1)
        
        # Entertainment value
        games_df['entertainment_value'] = games_df.apply(self._assess_entertainment_value, axis=1)
        
        return games_df
    
    def _add_recommendation_scores(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add final recommendation scores"""
        games_df = games_df.copy()
        
        # Overall recommendation
        games_df['overall_rating'] = games_df.apply(self._calculate_overall_rating, axis=1)
        
        # Priority level
        games_df['priority_level'] = games_df.apply(self._assign_priority_level, axis=1)
        
        return games_df
    
    def _calculate_interest_score(self, game: pd.Series) -> float:
        """Calculate comprehensive interest score"""
        score = 5.0
        
        # League popularity boost
        league = str(game.get('league', '')).upper()
        league_multipliers = {
            'NFL': 2.0, 'NBA': 1.8, 'MLB': 1.5, 'NHL': 1.3, 'WNBA': 1.2
        }
        score *= league_multipliers.get(league, 1.0)
        
        # Time-based factors
        try:
            game_time = str(game.get('time', ''))
            if any(prime in game_time for prime in ['7:00', '8:00', '9:00']):
                score += 1.0
        except:
            pass
        
        # Date proximity
        try:
            game_date = game.get('date', '')
            if game_date:
                game_dt = datetime.strptime(game_date, '%Y-%m-%d')
                days_away = (game_dt.date() - datetime.now().date()).days
                if days_away == 0:
                    score += 2.0  # Today
                elif days_away == 1:
                    score += 1.5  # Tomorrow
                elif days_away <= 3:
                    score += 1.0  # This week
        except:
            pass
        
        return min(score, 10.0)
    
    def _assess_competition_level(self, game: pd.Series) -> str:
        """Assess the competition level of the game"""
        league = str(game.get('league', '')).upper()
        
        if league in ['NFL', 'NBA', 'MLB', 'NHL']:
            return 'Elite'
        elif league == 'WNBA':
            return 'Professional'
        else:
            return 'Standard'
    
    def _generate_viewing_recommendation(self, game: pd.Series) -> str:
        """Generate viewing recommendation"""
        interest_score = game.get('interest_score', 5.0)
        
        if interest_score >= 8.0:
            return 'Must Watch'
        elif interest_score >= 6.5:
            return 'Highly Recommended'
        elif interest_score >= 5.0:
            return 'Worth Watching'
        else:
            return 'Optional'
    
    def _assess_market_efficiency(self, game: pd.Series) -> str:
        """Assess betting market efficiency"""
        home_odds = game.get('home_odds', 'N/A')
        away_odds = game.get('away_odds', 'N/A')
        
        if home_odds == 'N/A' or away_odds == 'N/A':
            return 'No Market Data'
        
        try:
            # Calculate total implied probability
            home_prob = self._american_odds_to_probability(home_odds)
            away_prob = self._american_odds_to_probability(away_odds)
            total_prob = home_prob + away_prob
            
            # Market efficiency based on overround
            overround = total_prob - 100
            
            if overround < 5:
                return 'Highly Efficient'
            elif overround < 10:
                return 'Efficient'
            elif overround < 15:
                return 'Moderately Efficient'
            else:
                return 'Less Efficient'
        except:
            return 'Analysis Error'
    
    def _calculate_implied_probabilities(self, game: pd.Series) -> str:
        """Calculate implied probabilities from odds"""
        home_odds = game.get('home_odds', 'N/A')
        away_odds = game.get('away_odds', 'N/A')
        
        if home_odds == 'N/A' or away_odds == 'N/A':
            return 'No odds available'
        
        try:
            home_prob = self._american_odds_to_probability(home_odds)
            away_prob = self._american_odds_to_probability(away_odds)
            
            home_team = game.get('home_team', 'Home')
            away_team = game.get('away_team', 'Away')
            
            return f"{home_team}: {home_prob:.1f}%, {away_team}: {away_prob:.1f}%"
        except:
            return 'Calculation error'
    
    def _assess_betting_value(self, game: pd.Series) -> str:
        """Assess betting value for the game"""
        try:
            market_eff = game.get('market_efficiency', 'Unknown')
            
            if market_eff == 'Highly Efficient':
                return 'Limited Value'
            elif market_eff == 'Efficient':
                return 'Standard Value'
            elif market_eff == 'Moderately Efficient':
                return 'Good Value'
            elif market_eff == 'Less Efficient':
                return 'High Value'
            else:
                return 'Unknown'
        except:
            return 'Analysis Error'
    
    def _simulate_team_form(self) -> str:
        """Simulate team form (would use real data in production)"""
        import random
        forms = ['Excellent', 'Good', 'Average', 'Poor']
        weights = [0.2, 0.3, 0.4, 0.1]
        return random.choices(forms, weights=weights)[0]
    
    def _calculate_momentum_factor(self, game: pd.Series) -> str:
        """Calculate momentum factor based on team forms"""
        home_form = game.get('home_form', 'Average')
        away_form = game.get('away_form', 'Average')
        
        form_scores = {'Excellent': 4, 'Good': 3, 'Average': 2, 'Poor': 1}
        
        home_score = form_scores.get(home_form, 2)
        away_score = form_scores.get(away_form, 2)
        
        diff = abs(home_score - away_score)
        
        if diff >= 2:
            return 'High Momentum Gap'
        elif diff == 1:
            return 'Moderate Gap'
        else:
            return 'Balanced'
    
    def _calculate_value_score(self, game: pd.Series) -> float:
        """Calculate overall value score"""
        base_score = game.get('interest_score', 5.0)
        
        # Adjust based on betting value
        betting_value = game.get('betting_value', 'Unknown')
        value_adjustments = {
            'High Value': 1.5,
            'Good Value': 1.2,
            'Standard Value': 1.0,
            'Limited Value': 0.8
        }
        
        multiplier = value_adjustments.get(betting_value, 1.0)
        return min(base_score * multiplier, 10.0)
    
    def _assess_entertainment_value(self, game: pd.Series) -> str:
        """Assess entertainment value"""
        value_score = game.get('value_score', 5.0)
        competition_level = game.get('competition_level', 'Standard')
        
        if value_score >= 8.0 and competition_level == 'Elite':
            return 'Premium Entertainment'
        elif value_score >= 7.0:
            return 'High Entertainment'
        elif value_score >= 5.5:
            return 'Good Entertainment'
        else:
            return 'Standard Entertainment'
    
    def _calculate_overall_rating(self, game: pd.Series) -> float:
        """Calculate overall rating out of 10"""
        factors = [
            game.get('interest_score', 5.0),
            game.get('value_score', 5.0),
        ]
        
        # Weight the average
        weights = [0.6, 0.4]
        weighted_avg = sum(f * w for f, w in zip(factors, weights))
        
        return min(weighted_avg, 10.0)
    
    def _assign_priority_level(self, game: pd.Series) -> str:
        """Assign priority level based on overall rating"""
        rating = game.get('overall_rating', 5.0)
        
        if rating >= 8.5:
            return 'Must See'
        elif rating >= 7.5:
            return 'High Priority'
        elif rating >= 6.0:
            return 'Medium Priority'
        else:
            return 'Low Priority'
    
    def _american_odds_to_probability(self, odds_str: str) -> float:
        """Convert American odds to probability"""
        try:
            odds = int(str(odds_str).replace('+', ''))
            if odds > 0:
                return 100 / (odds + 100) * 100
            else:
                return abs(odds) / (abs(odds) + 100) * 100
        except:
            return 50.0
    
    # Deep insights methods
    def _get_statistical_breakdown(self, game_data: pd.Series) -> Dict:
        """Get statistical breakdown for the game"""
        return {
            'competition_level': game_data.get('competition_level', 'Unknown'),
            'interest_score': f"{game_data.get('interest_score', 5.0):.1f}/10",
            'market_efficiency': game_data.get('market_efficiency', 'Unknown'),
            'team_forms': {
                'home': game_data.get('home_form', 'Unknown'),
                'away': game_data.get('away_form', 'Unknown')
            }
        }
    
    def _analyze_market_sentiment(self, game_data: pd.Series) -> Dict:
        """Analyze market sentiment"""
        return {
            'betting_value': game_data.get('betting_value', 'Unknown'),
            'implied_probabilities': game_data.get('implied_probabilities', 'N/A'),
            'market_consensus': 'Balanced' if 'N/A' not in str(game_data.get('implied_probabilities', '')) else 'No data'
        }
    
    def _get_historical_context(self, game_data: pd.Series) -> Dict:
        """Get historical context (placeholder)"""
        return {
            'head_to_head': 'Historical data would be analyzed here',
            'venue_performance': 'Venue-specific performance trends',
            'seasonal_context': 'Current season context and implications'
        }
    
    def _identify_key_factors(self, game_data: pd.Series) -> List[str]:
        """Identify key factors for the game"""
        factors = []
        
        if game_data.get('competition_level') == 'Elite':
            factors.append('Elite-level competition')
        
        if game_data.get('momentum_factor') == 'High Momentum Gap':
            factors.append('Significant momentum difference')
        
        if game_data.get('betting_value') == 'High Value':
            factors.append('Potential betting value identified')
        
        if game_data.get('viewing_rec') == 'Must Watch':
            factors.append('Highly recommended viewing')
        
        return factors or ['Standard matchup factors']
    
    def _assess_risk_factors(self, game_data: pd.Series) -> Dict:
        """Assess risk factors"""
        return {
            'betting_risk': 'Medium' if game_data.get('betting_value') != 'High Value' else 'High',
            'prediction_confidence': 'Medium',
            'market_volatility': 'Standard'
        }
    
    def _evaluate_value_proposition(self, game_data: pd.Series) -> Dict:
        """Evaluate value proposition"""
        return {
            'entertainment_value': game_data.get('entertainment_value', 'Standard'),
            'educational_value': 'High' if game_data.get('competition_level') == 'Elite' else 'Medium',
            'analysis_depth': 'Comprehensive'
        }
    
    def _simulate_expert_consensus(self, game_data: pd.Series) -> Dict:
        """Simulate expert consensus"""
        return {
            'expert_pick': game_data.get('home_team', 'Unknown'),
            'confidence_level': 'Medium',
            'consensus_strength': '65%'
        }
    
    def _identify_betting_angles(self, game_data: pd.Series) -> List[str]:
        """Identify potential betting angles"""
        angles = []
        
        if game_data.get('betting_value') == 'High Value':
            angles.append('Value betting opportunity')
        
        if game_data.get('momentum_factor') == 'High Momentum Gap':
            angles.append('Momentum-based approach')
        
        if game_data.get('market_efficiency') == 'Less Efficient':
            angles.append('Market inefficiency exploitation')
        
        return angles or ['Standard betting considerations']