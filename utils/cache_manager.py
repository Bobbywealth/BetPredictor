import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
from typing import Dict, List, Optional, Any

class CacheManager:
    """Efficient caching system to reduce API calls and improve performance"""
    
    def __init__(self):
        # Initialize cache in session state if not present
        if 'cache_store' not in st.session_state:
            st.session_state.cache_store = {}
        
        if 'cache_timestamps' not in st.session_state:
            st.session_state.cache_timestamps = {}
    
    def get_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key"""
        params_str = json.dumps(params, sort_keys=True, default=str)
        hash_obj = hashlib.md5(params_str.encode())
        return f"{prefix}_{hash_obj.hexdigest()[:12]}"
    
    def is_cache_valid(self, cache_key: str, ttl_minutes: int = 15) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in st.session_state.cache_timestamps:
            return False
        
        cache_time = st.session_state.cache_timestamps[cache_key]
        now = datetime.now()
        
        return (now - cache_time).total_seconds() < (ttl_minutes * 60)
    
    def preload_data(self, cache_key: str, data: Any, ttl_minutes: int = 30) -> None:
        """Preload data for faster access"""
        self._preload_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now(),
            'ttl': ttl_minutes
        }
    
    def get_preloaded_data(self, cache_key: str) -> Optional[Any]:
        """Get preloaded data if available and valid"""
        if cache_key not in self._preload_cache:
            return None
        
        cached_item = self._preload_cache[cache_key]
        age_minutes = (datetime.now() - cached_item['timestamp']).total_seconds() / 60
        
        if age_minutes < cached_item['ttl']:
            return cached_item['data']
        else:
            # Clean up expired preload cache
            del self._preload_cache[cache_key]
            return None
    
    def get_cached_data(self, cache_key: str, ttl_minutes: int = 15) -> Optional[Any]:
        """Retrieve cached data if valid"""
        if not self.is_cache_valid(cache_key, ttl_minutes):
            return None
        
        return st.session_state.cache_store.get(cache_key)
    
    def set_cached_data(self, cache_key: str, data: Any) -> None:
        """Store data in cache with timestamp"""
        st.session_state.cache_store[cache_key] = data
        st.session_state.cache_timestamps[cache_key] = datetime.now()
    
    def clear_cache(self, prefix: Optional[str] = None) -> None:
        """Clear cache by prefix or all cache"""
        if prefix:
            keys_to_remove = [k for k in st.session_state.cache_store.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                del st.session_state.cache_store[key]
                if key in st.session_state.cache_timestamps:
                    del st.session_state.cache_timestamps[key]
        else:
            st.session_state.cache_store.clear()
            st.session_state.cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total_entries = len(st.session_state.cache_store)
        valid_entries = sum(1 for key in st.session_state.cache_store.keys() 
                          if self.is_cache_valid(key))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries
        }

class OptimizedDataLoader:
    """Optimized data loading with intelligent caching"""
    
    def __init__(self):
        self.cache = CacheManager()
        self._preload_cache = {}  # In-memory preload cache
    
    def load_games_with_cache(self, date_str: str, sport_filter: List[str] = None) -> pd.DataFrame:
        """Load games with intelligent caching"""
        cache_params = {
            'date': date_str,
            'sports': sport_filter or []
        }
        cache_key = self.cache.get_cache_key('games', cache_params)
        
        # Try preloaded data first (fastest)
        preloaded_games = self.cache.get_preloaded_data(cache_key)
        if preloaded_games is not None:
            return preloaded_games
        
        # Try to get cached data
        cached_games = self.cache.get_cached_data(cache_key, ttl_minutes=30)  # Increased TTL
        if cached_games is not None:
            return cached_games
        
        # Load fresh data if cache miss
        from utils.live_games import LiveGamesManager
        games_manager = LiveGamesManager()
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            games_df = games_manager.get_upcoming_games_all_sports(target_date=target_date)
            
            # Filter by sport if specified
            if sport_filter:
                games_df = games_df[games_df['sport'].isin(sport_filter)]
            
            # Cache the results and preload for next access
            self.cache.set_cached_data(cache_key, games_df)
            self.cache.preload_data(cache_key, games_df, ttl_minutes=60)
            return games_df
            
        except Exception as e:
            st.error(f"Error loading games: {str(e)}")
            return pd.DataFrame()
    
    def load_odds_with_cache(self, sport_keys: List[str] = None) -> pd.DataFrame:
        """Load odds data with caching"""
        cache_params = {
            'sports': sport_keys or ['all'],
            'timestamp': datetime.now().strftime('%Y-%m-%d-%H')  # Cache per hour
        }
        cache_key = self.cache.get_cache_key('odds', cache_params)
        
        # Try cached data
        cached_odds = self.cache.get_cached_data(cache_key, ttl_minutes=30)
        if cached_odds is not None:
            return cached_odds
        
        # Load fresh odds
        from utils.odds_api import OddsAPIManager
        odds_manager = OddsAPIManager()
        
        try:
            if sport_keys:
                # Load specific sports only
                all_odds = []
                for sport_key in sport_keys:
                    odds_data = odds_manager.get_odds_for_sport(sport_key)
                    for game in odds_data:
                        # Process game data
                        processed_game = self._process_odds_game(game, sport_key)
                        all_odds.append(processed_game)
                
                odds_df = pd.DataFrame(all_odds) if all_odds else pd.DataFrame()
            else:
                # Load comprehensive odds
                odds_df = odds_manager.get_comprehensive_odds()
            
            # Cache results
            self.cache.set_cached_data(cache_key, odds_df)
            return odds_df
            
        except Exception as e:
            st.error(f"Error loading odds: {str(e)}")
            return pd.DataFrame()
    
    def _process_odds_game(self, game: Dict, sport_key: str) -> Dict:
        """Process individual odds game data"""
        from utils.odds_api import OddsAPIManager
        odds_manager = OddsAPIManager()
        
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
        
        # Get best odds
        best_odds = odds_manager.extract_best_odds(game.get('bookmakers', []))
        
        return {
            'game_id': game.get('id', ''),
            'sport': odds_manager.sports_mapping.get(sport_key, sport_key),
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

class BatchAnalysisManager:
    """Manage batch analysis operations efficiently"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    def analyze_games_batch(self, games_df: pd.DataFrame, analysis_type: str = 'basic') -> pd.DataFrame:
        """Perform batch analysis on games"""
        if len(games_df) == 0:
            return games_df
        
        # Create cache key for batch analysis
        games_hash = hashlib.md5(str(games_df.to_dict()).encode()).hexdigest()[:12]
        cache_key = f"batch_analysis_{analysis_type}_{games_hash}"
        
        # Check cache
        cached_analysis = self.cache.get_cached_data(cache_key, ttl_minutes=60)
        if cached_analysis is not None:
            return cached_analysis
        
        # Perform analysis
        analyzed_games = games_df.copy()
        
        try:
            if analysis_type == 'basic':
                analyzed_games = self._add_basic_analysis(analyzed_games)
            elif analysis_type == 'advanced':
                analyzed_games = self._add_advanced_analysis(analyzed_games)
            elif analysis_type == 'ai':
                analyzed_games = self._add_ai_analysis_summary(analyzed_games)
            
            # Cache results
            self.cache.set_cached_data(cache_key, analyzed_games)
            return analyzed_games
            
        except Exception as e:
            st.error(f"Batch analysis error: {str(e)}")
            return games_df
    
    def _add_basic_analysis(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add basic analysis metrics"""
        games_df = games_df.copy()
        
        # Add competitiveness score (placeholder logic)
        games_df['competitiveness'] = 'Medium'  # Would be calculated based on team stats
        
        # Add interest level
        games_df['interest_level'] = games_df.apply(self._calculate_interest_level, axis=1)
        
        # Add time-based priority
        games_df['time_priority'] = games_df.apply(self._calculate_time_priority, axis=1)
        
        return games_df
    
    def _add_advanced_analysis(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced analysis metrics"""
        games_df = self._add_basic_analysis(games_df)
        
        # Add betting value assessment (if odds available)
        if 'home_odds' in games_df.columns:
            games_df['betting_value'] = games_df.apply(self._assess_betting_value, axis=1)
        
        # Add rivalry factor
        games_df['rivalry_factor'] = games_df.apply(self._assess_rivalry, axis=1)
        
        return games_df
    
    def _add_ai_analysis_summary(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Add AI analysis summaries for top games"""
        games_df = self._add_advanced_analysis(games_df)
        
        # Select top games for AI analysis (to avoid overwhelming the API)
        top_games = games_df.nlargest(5, 'interest_level')
        
        for idx in top_games.index:
            game = games_df.loc[idx]
            ai_summary = self._get_quick_ai_summary(game)
            games_df.loc[idx, 'ai_summary'] = ai_summary
        
        return games_df
    
    def _calculate_interest_level(self, game: pd.Series) -> float:
        """Calculate interest level for a game"""
        base_score = 5.0
        
        # Boost for prime time
        if hasattr(game, 'time') and game.get('time', ''):
            time_str = str(game.get('time', ''))
            if any(prime in time_str.lower() for prime in ['7:00', '8:00', '9:00']):
                base_score += 1.0
        
        # Boost for popular leagues
        league = game.get('league', '').upper()
        if league in ['NFL', 'NBA', 'MLB']:
            base_score += 1.5
        elif league in ['NHL', 'WNBA']:
            base_score += 1.0
        
        # Boost for weekends
        try:
            game_date = game.get('date', '')
            if game_date:
                dt = datetime.strptime(game_date, '%Y-%m-%d')
                if dt.weekday() >= 5:  # Saturday or Sunday
                    base_score += 0.5
        except:
            pass
        
        return min(base_score, 10.0)
    
    def _calculate_time_priority(self, game: pd.Series) -> str:
        """Calculate time-based priority"""
        try:
            game_date = game.get('date', '')
            if not game_date:
                return 'Unknown'
            
            game_dt = datetime.strptime(game_date, '%Y-%m-%d')
            today = datetime.now().date()
            
            if game_dt.date() == today:
                return 'Today'
            elif game_dt.date() == today + timedelta(days=1):
                return 'Tomorrow'
            elif game_dt.date() <= today + timedelta(days=7):
                return 'This Week'
            else:
                return 'Future'
        except:
            return 'Unknown'
    
    def _assess_betting_value(self, game: pd.Series) -> str:
        """Assess betting value if odds are available"""
        home_odds = game.get('home_odds', 'N/A')
        away_odds = game.get('away_odds', 'N/A')
        
        if home_odds == 'N/A' or away_odds == 'N/A':
            return 'No Odds'
        
        try:
            # Simple value assessment based on odds spread
            home_num = int(str(home_odds).replace('+', ''))
            away_num = int(str(away_odds).replace('+', ''))
            
            odds_spread = abs(home_num - away_num)
            
            if odds_spread < 100:
                return 'High Value'
            elif odds_spread < 200:
                return 'Medium Value'
            else:
                return 'Low Value'
        except:
            return 'Unknown'
    
    def _assess_rivalry(self, game: pd.Series) -> str:
        """Assess rivalry factor between teams"""
        home_team = str(game.get('home_team', '')).lower()
        away_team = str(game.get('away_team', '')).lower()
        
        # Simple rivalry detection (would be enhanced with real data)
        rivalry_pairs = [
            ('yankees', 'red sox'), ('lakers', 'celtics'), ('cowboys', 'giants'),
            ('packers', 'bears'), ('dodgers', 'giants'), ('heat', 'knicks')
        ]
        
        for team1, team2 in rivalry_pairs:
            if (team1 in home_team and team2 in away_team) or (team2 in home_team and team1 in away_team):
                return 'High'
        
        return 'Standard'
    
    def _get_quick_ai_summary(self, game: pd.Series) -> str:
        """Get a quick AI summary for the game"""
        # This would call AI API for quick summary
        # For now, return a placeholder that indicates AI analysis is available
        home_team = game.get('home_team', 'Home')
        away_team = game.get('away_team', 'Away')
        
        return f"AI analysis available for {away_team} @ {home_team} matchup"