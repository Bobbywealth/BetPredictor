"""
Game Result Monitor - Checks for finished games and sends notifications
"""

import streamlit as st
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import requests
from utils.notification_system import notification_manager

class GameMonitor:
    """Monitors games and sends notifications when they finish"""
    
    def __init__(self):
        self.monitoring = False
        self.check_interval = 300  # 5 minutes
        self.monitored_games = {}
    
    def add_game_to_monitor(self, game_data: Dict, pick_data: Dict = None):
        """Add a game to be monitored for completion"""
        game_id = f"{game_data.get('away_team', '')}_{game_data.get('home_team', '')}_{game_data.get('game_date', '')}"
        
        self.monitored_games[game_id] = {
            'game_data': game_data,
            'pick_data': pick_data,
            'start_time': game_data.get('commence_time'),
            'status': 'scheduled',
            'last_checked': datetime.now().isoformat()
        }
        
        # Store in session state for persistence
        if 'monitored_games' not in st.session_state:
            st.session_state.monitored_games = {}
        st.session_state.monitored_games[game_id] = self.monitored_games[game_id]
    
    def check_game_results(self):
        """Check for completed games and send notifications"""
        if 'monitored_games' not in st.session_state:
            return
        
        current_time = datetime.now()
        completed_games = []
        
        for game_id, game_info in st.session_state.monitored_games.items():
            if game_info.get('status') == 'completed':
                continue
            
            game_data = game_info['game_data']
            
            # Check if enough time has passed since game start
            start_time_str = game_info.get('start_time')
            if start_time_str:
                try:
                    if start_time_str.endswith('Z'):
                        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    else:
                        start_time = datetime.fromisoformat(start_time_str)
                    
                    # Check if game should be finished (3+ hours after start for most sports)
                    if current_time > start_time + timedelta(hours=3):
                        # Fetch final score
                        final_result = self._fetch_game_result(game_data)
                        
                        if final_result:
                            # Mark as completed
                            game_info['status'] = 'completed'
                            game_info['final_result'] = final_result
                            
                            # Send notification
                            pick_data = game_info.get('pick_data')
                            notification_manager.game_finished_notification(final_result, pick_data)
                            
                            completed_games.append(game_id)
                            
                except Exception as e:
                    print(f"Error checking game {game_id}: {e}")
                    continue
        
        # Remove completed games from monitoring
        for game_id in completed_games:
            if game_id in st.session_state.monitored_games:
                del st.session_state.monitored_games[game_id]
    
    def _fetch_game_result(self, game_data: Dict) -> Dict:
        """Fetch final result for a specific game"""
        try:
            sport = game_data.get('sport', 'NFL').lower()
            home_team = game_data.get('home_team', '')
            away_team = game_data.get('away_team', '')
            game_date = game_data.get('game_date', datetime.now().strftime('%Y-%m-%d'))
            
            # Use ESPN API to get final scores
            if sport == 'nfl':
                espn_sport = 'football/nfl'
            elif sport == 'nba':
                espn_sport = 'basketball/nba'
            elif sport == 'mlb':
                espn_sport = 'baseball/mlb'
            elif sport == 'nhl':
                espn_sport = 'hockey/nhl'
            else:
                espn_sport = 'football/nfl'  # Default
            
            # Get scoreboard for the date
            url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_sport}/scoreboard"
            params = {'dates': game_date.replace('-', '')}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            # Find matching game
            for event in events:
                competitions = event.get('competitions', [])
                for competition in competitions:
                    competitors = competition.get('competitors', [])
                    
                    if len(competitors) >= 2:
                        home_competitor = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                        away_competitor = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                        
                        if home_competitor and away_competitor:
                            home_name = home_competitor.get('team', {}).get('displayName', '')
                            away_name = away_competitor.get('team', {}).get('displayName', '')
                            
                            # Simple name matching
                            if (self._teams_match(home_name, home_team) and 
                                self._teams_match(away_name, away_team)):
                                
                                # Check if game is completed
                                status = competition.get('status', {})
                                if status.get('type', {}).get('completed'):
                                    home_score = int(home_competitor.get('score', 0))
                                    away_score = int(away_competitor.get('score', 0))
                                    
                                    winner = home_name if home_score > away_score else away_name
                                    
                                    return {
                                        'home_team': home_name,
                                        'away_team': away_name,
                                        'home_score': home_score,
                                        'away_score': away_score,
                                        'winner': winner,
                                        'status': 'completed',
                                        'game_date': game_date
                                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching game result: {e}")
            return None
    
    def _teams_match(self, name1: str, name2: str) -> bool:
        """Check if two team names match (fuzzy matching)"""
        if not name1 or not name2:
            return False
        
        # Normalize names
        def normalize(name):
            return name.lower().replace(' ', '').replace('.', '').replace('-', '')
        
        norm1 = normalize(str(name1))
        norm2 = normalize(str(name2))
        
        # Exact match
        if norm1 == norm2:
            return True
        
        # Check if one contains the other (for cases like "Lakers" vs "Los Angeles Lakers")
        if len(norm1) >= 4 and len(norm2) >= 4:
            return norm1 in norm2 or norm2 in norm1
        
        return False
    
    def start_monitoring(self):
        """Start the background monitoring thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.check_game_results()
                    time.sleep(self.check_interval)
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the background monitoring"""
        self.monitoring = False
    
    def get_monitored_games_status(self) -> Dict:
        """Get status of all monitored games"""
        if 'monitored_games' not in st.session_state:
            return {}
        
        status = {
            'total_games': len(st.session_state.monitored_games),
            'scheduled': 0,
            'in_progress': 0,
            'completed': 0
        }
        
        for game_info in st.session_state.monitored_games.values():
            game_status = game_info.get('status', 'scheduled')
            if game_status in status:
                status[game_status] += 1
        
        return status

# Global game monitor instance
game_monitor = GameMonitor()

def add_picks_to_monitor(picks: List[Dict]):
    """Add generated picks to game monitoring"""
    for pick in picks:
        game_data = pick.get('game_data', {})
        ai_analysis = pick.get('ai_analysis', {})
        
        pick_data = {
            'predicted_winner': ai_analysis.get('pick', ''),
            'confidence': ai_analysis.get('confidence', 0),
            'away_team': game_data.get('away_team', ''),
            'home_team': game_data.get('home_team', '')
        }
        
        game_monitor.add_game_to_monitor(game_data, pick_data)
    
    # Start monitoring if not already running
    game_monitor.start_monitoring()

def show_monitoring_status():
    """Show monitoring status in UI"""
    status = game_monitor.get_monitored_games_status()
    
    if status['total_games'] > 0:
        st.info(f"🔍 Monitoring {status['total_games']} games for results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Scheduled", status['scheduled'])
        with col2:
            st.metric("In Progress", status['in_progress'])
        with col3:
            st.metric("Completed", status['completed'])
    else:
        st.info("No games currently being monitored")
