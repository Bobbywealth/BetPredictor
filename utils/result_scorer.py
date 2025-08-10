"""
Result Scorer - Fetches final scores and determines win/loss for predictions
"""
import streamlit as st
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class ResultScorer:
    """Fetches game results and scores predictions"""
    
    def __init__(self):
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports"
    
    def get_final_scores_for_date(self, date_str: str, sports: List[str]) -> Dict[str, List[Dict]]:
        """Fetch final scores for all games on a given date"""
        results = {}
        
        for sport in sports:
            try:
                sport_results = self._fetch_sport_results(sport, date_str)
                if sport_results:
                    results[sport] = sport_results
            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.write(f"⚠️ Failed to fetch {sport} results: {e}")
        
        return results
    
    def _fetch_sport_results(self, sport: str, date_str: str) -> List[Dict]:
        """Fetch results for a specific sport and date"""
        sport_map = {
            'NFL': 'football/nfl',
            'NBA': 'basketball/nba', 
            'WNBA': 'basketball/wnba',
            'MLB': 'baseball/mlb',
            'NHL': 'hockey/nhl',
            'NCAAF': 'football/college-football',
            'NCAAB': 'basketball/mens-college-basketball',
            'Tennis': 'tennis'
        }
        
        if sport not in sport_map:
            return []
        
        # Try multiple date formats for ESPN API
        date_formats = [
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d'),
            date_str.replace('-', ''),
            date_str
        ]
        
        for date_format in date_formats:
            try:
                url = f"{self.espn_base_url}/{sport_map[sport]}/scoreboard"
                params = {'dates': date_format}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    games = self._parse_espn_results(data, sport)
                    if games:  # Found games for this date format
                        return games
                        
            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.write(f"Debug: ESPN API error for {sport} on {date_format}: {e}")
                continue
        
        return []
    
    def _parse_espn_results(self, data: Dict, sport: str) -> List[Dict]:
        """Parse ESPN API response to extract game results"""
        games = []
        
        try:
            events = data.get('events', [])
            
            for event in events:
                # Only process completed games
                status = event.get('status', {})
                if status.get('type', {}).get('name') != 'STATUS_FINAL':
                    continue
                
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) != 2:
                    continue
                
                # Extract team info and scores
                home_team = None
                away_team = None
                
                for competitor in competitors:
                    team_info = {
                        'name': competitor.get('team', {}).get('displayName', 'Unknown'),
                        'score': int(competitor.get('score', 0))
                    }
                    
                    if competitor.get('homeAway') == 'home':
                        home_team = team_info
                    else:
                        away_team = team_info
                
                if home_team and away_team:
                    game_result = {
                        'sport': sport,
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': home_team['score'],
                        'away_score': away_team['score'],
                        'winner': 'home' if home_team['score'] > away_team['score'] else 'away',
                        'game_id': event.get('id'),
                        'date': event.get('date', ''),
                        'status': 'final'
                    }
                    games.append(game_result)
                    
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Error parsing ESPN results: {e}")
        
        return games
    
    def score_predictions(self, predictions: List[Dict], final_results: Dict[str, List[Dict]]) -> List[Dict]:
        """Score predictions against final results"""
        scored_predictions = []
        
        for prediction in predictions:
            scored_pred = prediction.copy()
            scored_pred['result'] = 'no_result'  # Default
            scored_pred['actual_winner'] = None
            scored_pred['home_score'] = None
            scored_pred['away_score'] = None
            
            # Find matching game result
            game_result = self._find_matching_result(prediction, final_results)
            
            if game_result:
                scored_pred['result'] = self._determine_prediction_result(prediction, game_result)
                scored_pred['actual_winner'] = game_result['winner']
                scored_pred['home_score'] = game_result['home_score']
                scored_pred['away_score'] = game_result['away_score']
            
            scored_predictions.append(scored_pred)
        
        return scored_predictions
    
    def _find_matching_result(self, prediction: Dict, final_results: Dict[str, List[Dict]]) -> Optional[Dict]:
        """Find the game result that matches a prediction"""
        pred_sport = prediction.get('sport', '').upper()
        pred_home = self._normalize_team_name(prediction.get('home_team', ''))
        pred_away = self._normalize_team_name(prediction.get('away_team', ''))
        
        if pred_sport not in final_results:
            return None
        
        for result in final_results[pred_sport]:
            result_home = self._normalize_team_name(result['home_team']['name'])
            result_away = self._normalize_team_name(result['away_team']['name'])
            
            # Match by team names
            if (pred_home == result_home and pred_away == result_away):
                return result
        
        return None
    
    def _normalize_team_name(self, name: str) -> str:
        """Normalize team names for matching"""
        if isinstance(name, dict):
            name = name.get('name', '')
        
        # Basic normalization
        name = str(name).strip().lower()
        
        # Remove common prefixes/suffixes
        replacements = {
            ' fc': '',
            ' cf': '',
            'the ': '',
            ' united': '',
            ' city': '',
            ' town': '',
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
        
        return name
    
    def _determine_prediction_result(self, prediction: Dict, game_result: Dict) -> str:
        """Determine if prediction was correct"""
        predicted_winner = prediction.get('predicted_winner', '').lower()
        actual_winner = game_result.get('winner', '').lower()
        
        if predicted_winner == actual_winner:
            return 'win'
        elif predicted_winner in ['home', 'away'] and actual_winner in ['home', 'away']:
            return 'loss'
        else:
            return 'no_result'
    
    def calculate_accuracy_metrics(self, scored_predictions: List[Dict]) -> Dict:
        """Calculate accuracy and performance metrics"""
        if not scored_predictions:
            return {
                'total_predictions': 0,
                'wins': 0,
                'losses': 0,
                'no_results': 0,
                'accuracy': 0.0,
                'high_confidence_accuracy': 0.0,
                'roi_estimate': 0.0
            }
        
        wins = sum(1 for p in scored_predictions if p.get('result') == 'win')
        losses = sum(1 for p in scored_predictions if p.get('result') == 'loss')
        no_results = sum(1 for p in scored_predictions if p.get('result') == 'no_result')
        
        total_with_results = wins + losses
        accuracy = (wins / total_with_results * 100) if total_with_results > 0 else 0
        
        # High confidence accuracy (80%+ confidence)
        high_conf_preds = [p for p in scored_predictions if p.get('confidence', 0) >= 0.8]
        high_conf_wins = sum(1 for p in high_conf_preds if p.get('result') == 'win')
        high_conf_total = sum(1 for p in high_conf_preds if p.get('result') in ['win', 'loss'])
        high_conf_accuracy = (high_conf_wins / high_conf_total * 100) if high_conf_total > 0 else 0
        
        # Simple ROI estimate (assuming -110 odds)
        roi_estimate = ((wins * 0.91) - (losses * 1.0)) / max(total_with_results, 1) * 100
        
        return {
            'total_predictions': len(scored_predictions),
            'wins': wins,
            'losses': losses,
            'no_results': no_results,
            'accuracy': accuracy,
            'high_confidence_accuracy': high_conf_accuracy,
            'roi_estimate': roi_estimate,
            'total_with_results': total_with_results
        }
