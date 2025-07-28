import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import requests
from utils.cache_manager import CacheManager
from utils.live_games import LiveGamesManager
from utils.odds_api import OddsAPIManager

class GameResultTracker:
    """Track game results and analyze prediction accuracy"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.games_manager = LiveGamesManager()
        self.odds_manager = OddsAPIManager()
        
        # Initialize result storage in session state
        if 'tracked_predictions' not in st.session_state:
            st.session_state.tracked_predictions = {}
        
        if 'game_results' not in st.session_state:
            st.session_state.game_results = {}
    
    def track_prediction(self, prediction_data: Dict) -> str:
        """Track a new prediction for result monitoring"""
        
        # Generate unique tracking ID
        game_id = prediction_data.get('game_id', 'unknown')
        timestamp = datetime.now().isoformat()
        tracking_id = f"{game_id}_{timestamp}"
        
        # Store prediction data
        tracking_record = {
            'tracking_id': tracking_id,
            'game_id': game_id,
            'prediction_date': timestamp,
            'home_team': prediction_data.get('home_team', 'Unknown'),
            'away_team': prediction_data.get('away_team', 'Unknown'), 
            'sport': prediction_data.get('sport', 'Unknown'),
            'game_date': prediction_data.get('date', 'Unknown'),
            'game_time': prediction_data.get('time', 'Unknown'),
            'consensus_pick': prediction_data.get('consensus_pick', 'NO_PICK'),
            'confidence': prediction_data.get('confidence', 0.0),
            'edge_score': prediction_data.get('edge_score', 0.0),
            'success_probability': prediction_data.get('success_probability', 0.0),
            'recommendation_strength': prediction_data.get('recommendation_strength', 'WEAK'),
            'ai_agreement': prediction_data.get('agreement_status', 'UNKNOWN'),
            'full_analysis': prediction_data.get('full_analysis', {}),
            'status': 'PENDING',  # PENDING, WIN, LOSS, PUSH, NO_RESULT
            'actual_winner': None,
            'final_score': None,
            'result_date': None,
            'accuracy_analysis': None
        }
        
        # Store in session state
        st.session_state.tracked_predictions[tracking_id] = tracking_record
        
        return tracking_id
    
    def check_game_results(self, max_days_back: int = 7) -> Dict[str, Any]:
        """Check for completed games and update results"""
        
        updated_count = 0
        results_summary = {
            'total_checked': 0,
            'results_found': 0,
            'wins': 0,
            'losses': 0,
            'pushes': 0,
            'no_results': 0
        }
        
        # Get all pending predictions
        pending_predictions = {
            tid: pred for tid, pred in st.session_state.tracked_predictions.items()
            if pred.get('status') == 'PENDING' and self._is_within_check_period(pred, max_days_back)
        }
        
        results_summary['total_checked'] = len(pending_predictions)
        
        # Check each pending prediction
        for tracking_id, prediction in pending_predictions.items():
            try:
                # Get game result
                game_result = self._fetch_game_result(prediction)
                
                if game_result:
                    # Update prediction with result
                    updated_prediction = self._analyze_prediction_result(prediction, game_result)
                    st.session_state.tracked_predictions[tracking_id] = updated_prediction
                    
                    # Update summary
                    results_summary['results_found'] += 1
                    status = updated_prediction.get('status', 'NO_RESULT')
                    
                    if status == 'WIN':
                        results_summary['wins'] += 1
                    elif status == 'LOSS':
                        results_summary['losses'] += 1
                    elif status == 'PUSH':
                        results_summary['pushes'] += 1
                    else:
                        results_summary['no_results'] += 1
                    
                    updated_count += 1
                    
            except Exception as e:
                continue
        
        # Cache the results summary
        cache_key = f"results_summary_{datetime.now().strftime('%Y%m%d')}"
        self.cache.set_cached_data(cache_key, results_summary)
        
        return results_summary
    
    def _is_within_check_period(self, prediction: Dict, max_days: int) -> bool:
        """Check if prediction is within the checking period"""
        try:
            game_date_str = prediction.get('game_date', '')
            if game_date_str and game_date_str != 'Unknown':
                game_date = datetime.strptime(game_date_str, '%Y-%m-%d').date()
                days_since = (date.today() - game_date).days
                return 0 <= days_since <= max_days
        except:
            pass
        return False
    
    def _fetch_game_result(self, prediction: Dict) -> Optional[Dict]:
        """Fetch the actual game result"""
        
        # Create cache key for game result
        game_key = f"{prediction.get('away_team', '')}_{prediction.get('home_team', '')}_{prediction.get('game_date', '')}"
        cache_key = f"game_result_{hash(game_key)}"
        
        # Check cache first
        cached_result = self.cache.get_cached_data(cache_key, ttl_minutes=60)
        if cached_result is not None:
            return cached_result
        
        # Try multiple sources for game results
        result = None
        
        # Method 1: ESPN API
        result = self._fetch_from_espn(prediction)
        
        # Method 2: TheSportsDB (fallback)
        if not result:
            result = self._fetch_from_sportsdb(prediction)
        
        # Method 3: Simple web scraping (fallback)
        if not result:
            result = self._fetch_from_web_search(prediction)
        
        # Cache the result if found
        if result:
            self.cache.set_cached_data(cache_key, result)
        
        return result
    
    def _fetch_from_espn(self, prediction: Dict) -> Optional[Dict]:
        """Fetch result from ESPN API"""
        try:
            sport = prediction.get('sport', '').lower()
            
            # ESPN sport mappings
            espn_sports = {
                'nfl': 'football/nfl',
                'nba': 'basketball/nba', 
                'mlb': 'baseball/mlb',
                'nhl': 'hockey/nhl',
                'wnba': 'basketball/wnba'
            }
            
            if sport not in espn_sports:
                return None
            
            # Get recent games
            game_date = prediction.get('game_date', '')
            if not game_date or game_date == 'Unknown':
                return None
            
            url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_sports[sport]}/scoreboard"
            params = {'dates': game_date.replace('-', '')}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                games = data.get('events', [])
                
                # Find matching game
                home_team = prediction.get('home_team', '').lower()
                away_team = prediction.get('away_team', '').lower()
                
                for game in games:
                    competitors = game.get('competitions', [{}])[0].get('competitors', [])
                    
                    if len(competitors) >= 2:
                        team1 = competitors[0].get('team', {}).get('displayName', '').lower()
                        team2 = competitors[1].get('team', {}).get('displayName', '').lower()
                        
                        # Check if teams match
                        if ((home_team in team1 or home_team in team2) and 
                            (away_team in team1 or away_team in team2)):
                            
                            # Check if game is completed
                            status = game.get('status', {}).get('type', {}).get('state', '')
                            
                            if status == 'post':
                                # Game completed, extract result
                                home_competitor = competitors[0] if competitors[0].get('homeAway') == 'home' else competitors[1]
                                away_competitor = competitors[1] if competitors[0].get('homeAway') == 'home' else competitors[0]
                                
                                home_score = int(home_competitor.get('score', 0))
                                away_score = int(away_competitor.get('score', 0))
                                
                                return {
                                    'home_team': home_competitor.get('team', {}).get('displayName', ''),
                                    'away_team': away_competitor.get('team', {}).get('displayName', ''),
                                    'home_score': home_score,
                                    'away_score': away_score,
                                    'winner': home_competitor.get('team', {}).get('displayName', '') if home_score > away_score else away_competitor.get('team', {}).get('displayName', ''),
                                    'final_score': f"{away_score}-{home_score}",
                                    'source': 'ESPN',
                                    'game_completed': True
                                }
                            
                            return None  # Game not completed yet
                
        except Exception:
            pass
        
        return None
    
    def _fetch_from_sportsdb(self, prediction: Dict) -> Optional[Dict]:
        """Fetch result from TheSportsDB"""
        try:
            # TheSportsDB implementation would go here
            # This is a placeholder for the actual implementation
            return None
        except:
            return None
    
    def _fetch_from_web_search(self, prediction: Dict) -> Optional[Dict]:
        """Fetch result from web search as last resort"""
        try:
            # Web search implementation would go here
            # This is a placeholder for the actual implementation
            return None
        except:
            return None
    
    def _analyze_prediction_result(self, prediction: Dict, game_result: Dict) -> Dict:
        """Analyze if our prediction was correct"""
        
        updated_prediction = prediction.copy()
        
        # Extract prediction and actual result
        our_pick = prediction.get('consensus_pick', '').lower().strip()
        actual_winner = game_result.get('winner', '').lower().strip()
        home_team = prediction.get('home_team', '').lower().strip()
        away_team = prediction.get('away_team', '').lower().strip()
        
        # Determine if prediction was correct
        prediction_correct = False
        
        if our_pick and actual_winner:
            # Check if our pick matches the actual winner
            if (our_pick in actual_winner or actual_winner in our_pick or
                (our_pick in home_team and home_team in actual_winner) or
                (our_pick in away_team and away_team in actual_winner)):
                prediction_correct = True
        
        # Update prediction record
        updated_prediction.update({
            'status': 'WIN' if prediction_correct else 'LOSS',
            'actual_winner': game_result.get('winner', 'Unknown'),
            'final_score': game_result.get('final_score', 'Unknown'),
            'result_date': datetime.now().isoformat(),
            'accuracy_analysis': self._generate_accuracy_analysis(prediction, game_result, prediction_correct)
        })
        
        return updated_prediction
    
    def _generate_accuracy_analysis(self, prediction: Dict, game_result: Dict, correct: bool) -> Dict:
        """Generate detailed accuracy analysis"""
        
        confidence = prediction.get('confidence', 0.0)
        edge_score = prediction.get('edge_score', 0.0)
        success_prob = prediction.get('success_probability', 0.0)
        
        analysis = {
            'prediction_correct': correct,
            'confidence_level': 'High' if confidence >= 0.75 else 'Medium' if confidence >= 0.6 else 'Low',
            'edge_assessment': 'Strong' if edge_score >= 0.4 else 'Moderate' if edge_score >= 0.25 else 'Weak',
            'model_performance': 'Excellent' if correct and confidence >= 0.75 else 'Good' if correct else 'Poor',
            'accuracy_score': 1.0 if correct else 0.0,
            'confidence_calibration': abs(success_prob - (1.0 if correct else 0.0)),
            'notes': []
        }
        
        # Add performance notes
        if correct:
            if confidence >= 0.8:
                analysis['notes'].append('High confidence prediction proved correct')
            elif confidence >= 0.6:
                analysis['notes'].append('Medium confidence prediction succeeded')
            else:
                analysis['notes'].append('Low confidence prediction got lucky')
        else:
            if confidence >= 0.8:
                analysis['notes'].append('High confidence prediction failed - review methodology')
            elif confidence >= 0.6:
                analysis['notes'].append('Medium confidence prediction missed')
            else:
                analysis['notes'].append('Low confidence prediction failed as expected')
        
        # Assess AI agreement performance
        ai_agreement = prediction.get('ai_agreement', 'UNKNOWN')
        if ai_agreement == 'STRONG_CONSENSUS':
            if correct:
                analysis['notes'].append('Strong AI consensus was validated')
            else:
                analysis['notes'].append('Strong AI consensus failed - investigate model issues')
        
        return analysis
    
    def get_performance_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        # Filter predictions by date range
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        relevant_predictions = {
            tid: pred for tid, pred in st.session_state.tracked_predictions.items()
            if datetime.fromisoformat(pred.get('prediction_date', '')) >= cutoff_date
        }
        
        if not relevant_predictions:
            return {
                'total_predictions': 0,
                'message': 'No predictions found in the specified period'
            }
        
        # Calculate summary statistics
        total_predictions = len(relevant_predictions)
        completed_predictions = [p for p in relevant_predictions.values() if p.get('status') in ['WIN', 'LOSS', 'PUSH']]
        
        wins = len([p for p in completed_predictions if p.get('status') == 'WIN'])
        losses = len([p for p in completed_predictions if p.get('status') == 'LOSS'])
        pushes = len([p for p in completed_predictions if p.get('status') == 'PUSH'])
        
        win_rate = wins / len(completed_predictions) if completed_predictions else 0.0
        
        # Performance by confidence level
        high_conf_preds = [p for p in completed_predictions if p.get('confidence', 0) >= 0.75]
        high_conf_wins = len([p for p in high_conf_preds if p.get('status') == 'WIN'])
        high_conf_win_rate = high_conf_wins / len(high_conf_preds) if high_conf_preds else 0.0
        
        # Performance by AI agreement
        consensus_preds = [p for p in completed_predictions if p.get('ai_agreement') == 'STRONG_CONSENSUS']
        consensus_wins = len([p for p in consensus_preds if p.get('status') == 'WIN'])
        consensus_win_rate = consensus_wins / len(consensus_preds) if consensus_preds else 0.0
        
        # Performance by sport
        sport_performance = {}
        for pred in completed_predictions:
            sport = pred.get('sport', 'Unknown')
            if sport not in sport_performance:
                sport_performance[sport] = {'total': 0, 'wins': 0}
            
            sport_performance[sport]['total'] += 1
            if pred.get('status') == 'WIN':
                sport_performance[sport]['wins'] += 1
        
        # Add win rates to sport performance
        for sport in sport_performance:
            total = sport_performance[sport]['total']
            wins = sport_performance[sport]['wins']
            sport_performance[sport]['win_rate'] = wins / total if total > 0 else 0.0
        
        summary = {
            'analysis_period': f'{days_back} days',
            'total_predictions': total_predictions,
            'completed_predictions': len(completed_predictions),
            'pending_predictions': total_predictions - len(completed_predictions),
            'overall_performance': {
                'wins': wins,
                'losses': losses,
                'pushes': pushes,
                'win_rate': win_rate,
                'total_completed': len(completed_predictions)
            },
            'high_confidence_performance': {
                'total': len(high_conf_preds),
                'wins': high_conf_wins,
                'win_rate': high_conf_win_rate
            },
            'ai_consensus_performance': {
                'total': len(consensus_preds),
                'wins': consensus_wins,
                'win_rate': consensus_win_rate
            },
            'sport_breakdown': sport_performance,
            'model_calibration': self._calculate_model_calibration(completed_predictions),
            'recent_trend': self._calculate_recent_trend(completed_predictions)
        }
        
        return summary
    
    def _calculate_model_calibration(self, predictions: List[Dict]) -> Dict[str, float]:
        """Calculate how well our confidence estimates match actual results"""
        
        if not predictions:
            return {'calibration_score': 0.0, 'note': 'No data available'}
        
        # Group predictions by confidence ranges
        confidence_buckets = {
            'high': [],  # 75%+
            'medium': [], # 60-75%
            'low': []    # <60%
        }
        
        for pred in predictions:
            confidence = pred.get('confidence', 0.0)
            actual_result = 1.0 if pred.get('status') == 'WIN' else 0.0
            
            if confidence >= 0.75:
                confidence_buckets['high'].append((confidence, actual_result))
            elif confidence >= 0.6:
                confidence_buckets['medium'].append((confidence, actual_result))
            else:
                confidence_buckets['low'].append((confidence, actual_result))
        
        # Calculate calibration for each bucket
        calibration_results = {}
        
        for bucket_name, bucket_data in confidence_buckets.items():
            if bucket_data:
                avg_confidence = sum(conf for conf, _ in bucket_data) / len(bucket_data)
                avg_accuracy = sum(result for _, result in bucket_data) / len(bucket_data)
                calibration_error = abs(avg_confidence - avg_accuracy)
                
                calibration_results[bucket_name] = {
                    'count': len(bucket_data),
                    'avg_confidence': avg_confidence,
                    'actual_accuracy': avg_accuracy,
                    'calibration_error': calibration_error
                }
        
        # Overall calibration score (lower is better)
        all_errors = [data['calibration_error'] for data in calibration_results.values()]
        overall_calibration = sum(all_errors) / len(all_errors) if all_errors else 0.0
        
        return {
            'overall_calibration_error': overall_calibration,
            'by_confidence_level': calibration_results,
            'interpretation': 'Excellent' if overall_calibration < 0.1 else 'Good' if overall_calibration < 0.2 else 'Needs Improvement'
        }
    
    def _calculate_recent_trend(self, predictions: List[Dict], days: int = 7) -> Dict[str, Any]:
        """Calculate recent performance trend"""
        
        if not predictions:
            return {'trend': 'No data', 'recent_win_rate': 0.0}
        
        # Get recent predictions
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_preds = [
            p for p in predictions 
            if datetime.fromisoformat(p.get('result_date', '')) >= cutoff_date
        ]
        
        if not recent_preds:
            return {'trend': 'No recent data', 'recent_win_rate': 0.0}
        
        recent_wins = len([p for p in recent_preds if p.get('status') == 'WIN'])
        recent_win_rate = recent_wins / len(recent_preds)
        
        # Compare to overall performance
        overall_wins = len([p for p in predictions if p.get('status') == 'WIN'])
        overall_win_rate = overall_wins / len(predictions)
        
        trend_direction = 'Improving' if recent_win_rate > overall_win_rate + 0.05 else 'Declining' if recent_win_rate < overall_win_rate - 0.05 else 'Stable'
        
        return {
            'recent_predictions': len(recent_preds),
            'recent_wins': recent_wins,
            'recent_win_rate': recent_win_rate,
            'trend': trend_direction,
            'trend_magnitude': abs(recent_win_rate - overall_win_rate)
        }
    
    def export_tracking_data(self) -> pd.DataFrame:
        """Export all tracking data to DataFrame"""
        
        if not st.session_state.tracked_predictions:
            return pd.DataFrame()
        
        # Convert tracking data to DataFrame
        records = []
        
        for tracking_id, prediction in st.session_state.tracked_predictions.items():
            record = {
                'tracking_id': tracking_id,
                'prediction_date': prediction.get('prediction_date'),
                'game_date': prediction.get('game_date'),
                'sport': prediction.get('sport'),
                'away_team': prediction.get('away_team'),
                'home_team': prediction.get('home_team'),
                'our_pick': prediction.get('consensus_pick'),
                'confidence': prediction.get('confidence'),
                'edge_score': prediction.get('edge_score'),
                'success_probability': prediction.get('success_probability'),
                'ai_agreement': prediction.get('ai_agreement'),
                'recommendation_strength': prediction.get('recommendation_strength'),
                'status': prediction.get('status'),
                'actual_winner': prediction.get('actual_winner'),
                'final_score': prediction.get('final_score'),
                'result_date': prediction.get('result_date'),
                'prediction_correct': prediction.get('accuracy_analysis', {}).get('prediction_correct'),
                'model_performance': prediction.get('accuracy_analysis', {}).get('model_performance')
            }
            records.append(record)
        
        return pd.DataFrame(records)