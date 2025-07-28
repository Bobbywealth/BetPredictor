import os
import requests
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional
import streamlit as st
from utils.performance_cache import performance_cache

class OddsAPIManager:
    """Manager for The Odds API integration"""
    
    def __init__(self):
        self.api_key = "ffb7d086c82de331b0191d11a3386eac"
        self.base_url = "https://api.the-odds-api.com/v4"
        self.sports_mapping = {
            'americanfootball_nfl': 'NFL',
            'basketball_nba': 'NBA',
            'basketball_wnba': 'WNBA',
            'baseball_mlb': 'MLB',
            'icehockey_nhl': 'NHL',
            'soccer_epl': 'Premier League',
            'soccer_uefa_champs_league': 'Champions League'
        }
    
    def get_available_sports(self) -> List[Dict]:
        """Get all available sports from The Odds API"""
        try:
            url = f"{self.base_url}/sports/"
            params = {
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                sports_data = response.json()
                return sports_data
            else:
                return []
                
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"⚠️ Sports API error: {str(e)}")
            return []
    
    @performance_cache.cached_function(max_age=300)  # Cache for 5 minutes
    def get_odds_for_sport(self, sport_key: str, regions: str = "us", markets: str = "h2h") -> List[Dict]:
        """Get odds for a specific sport"""
        try:
            url = f"{self.base_url}/sports/{sport_key}/odds/"
            params = {
                'apiKey': self.api_key,
                'regions': regions,
                'markets': markets,
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                odds_data = response.json()
                return odds_data
            else:
                if st.session_state.get('debug_mode', False):
                    st.write(f"⚠️ Odds API error for {sport_key}: {response.status_code}")
                return []
                
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"⚠️ Odds fetch error for {sport_key}: {str(e)}")
            return []
    
    def get_comprehensive_odds(self) -> pd.DataFrame:
        """Get odds for all major sports"""
        all_odds = []
        
        # Major sports to fetch
        sports_to_fetch = [
            'americanfootball_nfl',
            'basketball_nba', 
            'basketball_wnba',
            'baseball_mlb',
            'icehockey_nhl'
        ]
        
        for sport_key in sports_to_fetch:
            try:
                odds_data = self.get_odds_for_sport(sport_key)
                
                for game in odds_data:
                    # Parse game data
                    home_team = game.get('home_team', 'Unknown')
                    away_team = game.get('away_team', 'Unknown')
                    commence_time = game.get('commence_time', '')
                    
                    # Parse commence time
                    game_date = 'TBD'
                    game_time = 'TBD'
                    
                    if commence_time:
                        try:
                            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                            game_date = dt.strftime('%Y-%m-%d')
                            game_time = dt.strftime('%I:%M %p ET')
                        except:
                            pass
                    
                    # Get best odds from bookmakers
                    best_odds = self.extract_best_odds(game.get('bookmakers', []))
                    
                    game_odds = {
                        'game_id': game.get('id', ''),
                        'sport': self.sports_mapping.get(sport_key, sport_key),
                        'home_team': home_team,
                        'away_team': away_team,
                        'game_name': f"{away_team} @ {home_team}",
                        'date': game_date,
                        'time': game_time,
                        'commence_time': commence_time,
                        'home_odds': best_odds.get('home_odds', 'N/A'),
                        'away_odds': best_odds.get('away_odds', 'N/A'),
                        'best_bookmaker': best_odds.get('bookmaker', 'N/A'),
                        'source': 'The Odds API'
                    }
                    
                    all_odds.append(game_odds)
                    
            except Exception as e:
                continue
        
        if all_odds:
            return pd.DataFrame(all_odds)
        else:
            return pd.DataFrame()
    
    def extract_best_odds(self, bookmakers: List[Dict]) -> Dict:
        """Extract best odds from bookmakers"""
        if not bookmakers:
            return {'home_odds': 'N/A', 'away_odds': 'N/A', 'bookmaker': 'N/A'}
        
        best_home = None
        best_away = None
        best_bookmaker = 'N/A'
        
        for bookmaker in bookmakers:
            bookmaker_name = bookmaker.get('title', 'Unknown')
            markets = bookmaker.get('markets', [])
            
            for market in markets:
                if market.get('key') == 'h2h':
                    outcomes = market.get('outcomes', [])
                    
                    for outcome in outcomes:
                        team_name = outcome.get('name', '')
                        odds = outcome.get('price', 0)
                        
                        # Convert to American odds if needed
                        if isinstance(odds, (int, float)) and odds > 0:
                            if odds >= 2.0:
                                american_odds = f"+{int((odds - 1) * 100)}"
                            else:
                                american_odds = f"-{int(100 / (odds - 1))}"
                        else:
                            american_odds = str(odds)
                        
                        # Track best odds (highest positive, lowest negative)
                        if team_name and odds:
                            if not best_home:
                                best_home = american_odds
                                best_bookmaker = bookmaker_name
                            if not best_away:
                                best_away = american_odds
        
        return {
            'home_odds': best_home or 'N/A',
            'away_odds': best_away or 'N/A', 
            'bookmaker': best_bookmaker
        }
    
    def get_odds_for_game(self, home_team: str, away_team: str, sport_key: str) -> Dict:
        """Get specific odds for a particular game"""
        try:
            odds_data = self.get_odds_for_sport(sport_key)
            
            for game in odds_data:
                if (game.get('home_team', '').lower() == home_team.lower() and 
                    game.get('away_team', '').lower() == away_team.lower()):
                    
                    # Return detailed odds information
                    bookmakers_info = []
                    for bookmaker in game.get('bookmakers', []):
                        bookmaker_name = bookmaker.get('title', 'Unknown')
                        
                        for market in bookmaker.get('markets', []):
                            if market.get('key') == 'h2h':
                                outcomes = {}
                                for outcome in market.get('outcomes', []):
                                    team = outcome.get('name', '')
                                    price = outcome.get('price', 0)
                                    outcomes[team] = price
                                
                                bookmakers_info.append({
                                    'bookmaker': bookmaker_name,
                                    'odds': outcomes
                                })
                    
                    return {
                        'game_found': True,
                        'home_team': game.get('home_team', ''),
                        'away_team': game.get('away_team', ''),
                        'commence_time': game.get('commence_time', ''),
                        'bookmakers': bookmakers_info
                    }
            
            return {'game_found': False, 'message': 'Game not found in odds data'}
            
        except Exception as e:
            return {'game_found': False, 'error': str(e)}
    
    def get_api_usage(self) -> Dict:
        """Check API usage and remaining requests"""
        try:
            # Make a simple request to check usage
            url = f"{self.base_url}/sports/"
            params = {'apiKey': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                remaining_requests = response.headers.get('x-requests-remaining', 'Unknown')
                used_requests = response.headers.get('x-requests-used', 'Unknown')
                
                return {
                    'status': 'active',
                    'remaining_requests': remaining_requests,
                    'used_requests': used_requests,
                    'response_code': response.status_code
                }
            else:
                return {
                    'status': 'error',
                    'response_code': response.status_code,
                    'message': 'API key may be invalid'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

class OddsAnalyzer:
    """Analyze odds data and provide insights"""
    
    def __init__(self):
        self.odds_manager = OddsAPIManager()
    
    def analyze_game_value(self, odds_data: Dict) -> Dict:
        """Analyze betting value for a game"""
        if not odds_data.get('game_found', False):
            return {'error': 'No odds data available'}
        
        try:
            bookmakers = odds_data.get('bookmakers', [])
            if not bookmakers:
                return {'error': 'No bookmaker data available'}
            
            # Calculate average odds and find best value
            home_odds = []
            away_odds = []
            
            for bookmaker in bookmakers:
                odds = bookmaker.get('odds', {})
                home_team = odds_data.get('home_team', '')
                away_team = odds_data.get('away_team', '')
                
                if home_team in odds:
                    home_odds.append(odds[home_team])
                if away_team in odds:
                    away_odds.append(odds[away_team])
            
            analysis = {
                'home_team': odds_data.get('home_team', ''),
                'away_team': odds_data.get('away_team', ''),
                'total_bookmakers': len(bookmakers),
                'best_home_odds': max(home_odds) if home_odds else None,
                'best_away_odds': max(away_odds) if away_odds else None,
                'avg_home_odds': sum(home_odds) / len(home_odds) if home_odds else None,
                'avg_away_odds': sum(away_odds) / len(away_odds) if away_odds else None,
                'odds_variance': self.calculate_odds_variance(home_odds, away_odds)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def calculate_odds_variance(self, home_odds: List[float], away_odds: List[float]) -> str:
        """Calculate variance in odds across bookmakers"""
        try:
            if not home_odds or not away_odds:
                return "Insufficient data"
            
            home_range = max(home_odds) - min(home_odds) if len(home_odds) > 1 else 0
            away_range = max(away_odds) - min(away_odds) if len(away_odds) > 1 else 0
            
            avg_range = (home_range + away_range) / 2
            
            if avg_range < 0.1:
                return "Low variance - consistent odds"
            elif avg_range < 0.3:
                return "Medium variance - some differences"
            else:
                return "High variance - shop around for best odds"
                
        except Exception:
            return "Unable to calculate variance"
    
    def find_best_value_bets(self, odds_df: pd.DataFrame) -> List[Dict]:
        """Find games with potentially good betting value"""
        if len(odds_df) == 0:
            return []
        
        value_bets = []
        
        for idx, game in odds_df.iterrows():
            home_odds = game.get('home_odds', 'N/A')
            away_odds = game.get('away_odds', 'N/A')
            
            # Simple value analysis (this would be more sophisticated in production)
            if home_odds != 'N/A' and away_odds != 'N/A':
                try:
                    # Convert American odds to implied probability
                    home_prob = self.american_odds_to_probability(home_odds)
                    away_prob = self.american_odds_to_probability(away_odds)
                    
                    total_prob = home_prob + away_prob
                    margin = max(0, total_prob - 100)  # Bookmaker margin
                    
                    value_bet = {
                        'game': game.get('game_name', ''),
                        'sport': game.get('sport', ''),
                        'date': game.get('date', ''),
                        'bookmaker_margin': f"{margin:.1f}%",
                        'value_rating': 'Low' if margin > 10 else 'Medium' if margin > 5 else 'High'
                    }
                    
                    value_bets.append(value_bet)
                    
                except Exception:
                    continue
        
        # Sort by margin (lower is better)
        return sorted(value_bets, key=lambda x: float(x['bookmaker_margin'].replace('%', '')))[:5]
    
    def american_odds_to_probability(self, odds_str: str) -> float:
        """Convert American odds to implied probability"""
        try:
            if isinstance(odds_str, str):
                odds = int(odds_str.replace('+', ''))
            else:
                odds = int(odds_str)
            
            if odds > 0:
                return 100 / (odds + 100) * 100
            else:
                return abs(odds) / (abs(odds) + 100) * 100
                
        except Exception:
            return 50.0  # Default 50% if conversion fails