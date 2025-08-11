"""
Live Scores API - Real ESPN Integration
Fetches actual live scores and game status from ESPN APIs
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class LiveScoresAPI:
    """
    Fetches real live scores from ESPN APIs
    """
    
    def __init__(self):
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Sport endpoint mappings
        self.sport_endpoints = {
            'NFL': 'football/nfl',
            'NBA': 'basketball/nba', 
            'WNBA': 'basketball/wnba',
            'MLB': 'baseball/mlb',
            'NHL': 'hockey/nhl',
            'NCAAF': 'football/college-football',
            'NCAAB': 'basketball/mens-college-basketball'
        }

    def get_live_scores_for_date(self, date_str: str, sports: List[str]) -> Dict[str, List[Dict]]:
        """Get live scores for multiple sports on a specific date"""
        
        all_scores = {}
        
        for sport in sports:
            if sport.upper() in self.sport_endpoints:
                try:
                    scores = self._fetch_sport_scores(sport.upper(), date_str)
                    if scores:
                        all_scores[sport.upper()] = scores
                except Exception as e:
                    if st.session_state.get('debug_mode', False):
                        st.write(f"Debug: Error fetching {sport} scores: {e}")
                    
        return all_scores

    def _fetch_sport_scores(self, sport: str, date_str: str) -> List[Dict]:
        """Fetch scores for a specific sport"""
        
        endpoint = self.sport_endpoints.get(sport)
        if not endpoint:
            return []
        
        try:
            # ESPN scoreboard URL with date
            url = f"{self.espn_base}/{endpoint}/scoreboard"
            
            # Add date parameter
            params = {'dates': date_str.replace('-', '')}  # ESPN uses YYYYMMDD format
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            games = []
            
            # Parse ESPN scoreboard response
            events = data.get('events', [])
            
            for event in events:
                try:
                    game_info = self._parse_espn_game(event, sport)
                    if game_info:
                        games.append(game_info)
                except Exception as e:
                    if st.session_state.get('debug_mode', False):
                        st.write(f"Debug: Error parsing game: {e}")
                    continue
            
            return games
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Error fetching {sport} scoreboard: {e}")
            return []

    def _parse_espn_game(self, event: Dict, sport: str) -> Optional[Dict]:
        """Parse ESPN game data into standardized format"""
        
        try:
            # Basic game info
            game_id = event.get('id', '')
            name = event.get('name', '')
            short_name = event.get('shortName', '')
            
            # Game status
            status_info = event.get('status', {})
            status_type = status_info.get('type', {})
            status_name = status_type.get('name', 'Unknown')
            status_detail = status_type.get('detail', '')
            status_short_detail = status_type.get('shortDetail', '')
            
            # Determine game state
            game_state = self._determine_game_state(status_name, status_detail)
            
            # Teams and scores
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) < 2:
                return None
            
            # Parse teams (ESPN format: [0] = away, [1] = home usually, but check homeAway)
            home_team = None
            away_team = None
            
            for competitor in competitors:
                team = competitor.get('team', {})
                is_home = competitor.get('homeAway') == 'home'
                
                team_info = {
                    'name': team.get('displayName', 'Unknown'),
                    'short_name': team.get('abbreviation', 'UNK'),
                    'logo': team.get('logo', ''),
                    'color': team.get('color', ''),
                    'score': competitor.get('score', '0'),
                    'record': competitor.get('records', [{}])[0].get('summary', '') if competitor.get('records') else '',
                    'winner': competitor.get('winner', False)
                }
                
                if is_home:
                    home_team = team_info
                else:
                    away_team = team_info
            
            if not home_team or not away_team:
                return None
            
            # Game time info
            date_str = event.get('date', '')
            game_time = ''
            if date_str:
                try:
                    game_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    est_tz = pytz.timezone('US/Eastern')
                    game_est = game_dt.astimezone(est_tz)
                    game_time = game_est.strftime('%I:%M %p ET')
                except:
                    game_time = 'TBD'
            
            # Additional game details
            venue = competition.get('venue', {})
            venue_name = venue.get('fullName', 'TBD')
            
            # Period/inning info for live games
            period_info = self._get_period_info(status_info, sport)
            
            # Weather (if available)
            weather = competition.get('weather', {})
            weather_info = ''
            if weather:
                temp = weather.get('temperature')
                condition = weather.get('conditionId', '')
                if temp:
                    weather_info = f"{temp}°F"
                if condition:
                    weather_info += f" {condition}" if weather_info else condition
            
            return {
                'game_id': game_id,
                'sport': sport,
                'name': name,
                'short_name': short_name,
                'home_team': home_team,
                'away_team': away_team,
                'status': game_state,
                'status_detail': status_short_detail,
                'game_time': game_time,
                'venue': venue_name,
                'period_info': period_info,
                'weather': weather_info,
                'is_live': game_state in ['live', 'halftime', 'overtime'],
                'is_final': game_state == 'final',
                'is_upcoming': game_state == 'scheduled'
            }
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Error parsing ESPN game: {e}")
            return None

    def _determine_game_state(self, status_name: str, status_detail: str) -> str:
        """Determine standardized game state from ESPN status"""
        
        status_lower = status_name.lower()
        detail_lower = status_detail.lower()
        
        if 'final' in status_lower:
            return 'final'
        elif any(word in status_lower for word in ['in progress', 'live', '1st', '2nd', '3rd', '4th']):
            return 'live'
        elif 'halftime' in status_lower or 'half' in detail_lower:
            return 'halftime'
        elif 'overtime' in status_lower or 'ot' in detail_lower:
            return 'overtime'
        elif 'delayed' in status_lower:
            return 'delayed'
        elif 'postponed' in status_lower:
            return 'postponed'
        elif 'canceled' in status_lower:
            return 'canceled'
        else:
            return 'scheduled'

    def _get_period_info(self, status_info: Dict, sport: str) -> str:
        """Get period/inning information for live games"""
        
        try:
            period = status_info.get('period', 0)
            clock = status_info.get('displayClock', '')
            
            if not period:
                return ''
            
            # Sport-specific period names
            if sport in ['NFL', 'NCAAF']:
                if period <= 4:
                    period_name = f"{self._ordinal(period)} Quarter"
                else:
                    period_name = f"OT{period - 4}" if period > 5 else "OT"
            elif sport in ['NBA', 'WNBA', 'NCAAB']:
                if period <= 2:
                    period_name = f"{self._ordinal(period)} Half"
                elif period <= 4:
                    period_name = f"{self._ordinal(period)} Quarter"  
                else:
                    period_name = f"OT{period - 4}" if period > 5 else "OT"
            elif sport == 'NHL':
                if period <= 3:
                    period_name = f"{self._ordinal(period)} Period"
                else:
                    period_name = f"OT{period - 3}" if period > 4 else "OT"
            elif sport == 'MLB':
                if period <= 9:
                    period_name = f"Top {self._ordinal(period)}" if clock and 'top' in clock.lower() else f"Bot {self._ordinal(period)}"
                else:
                    period_name = f"Extra Innings"
            else:
                period_name = f"Period {period}"
            
            if clock and clock != '0:00':
                return f"{period_name} - {clock}"
            else:
                return period_name
                
        except Exception:
            return ''

    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    def get_trending_games(self) -> List[Dict]:
        """Get trending/popular games across all sports"""
        
        try:
            # Get today's games from major sports
            today = datetime.now().strftime('%Y-%m-%d')
            major_sports = ['NFL', 'NBA', 'MLB']
            
            trending = []
            
            for sport in major_sports:
                scores = self._fetch_sport_scores(sport, today)
                
                # Prioritize live games
                live_games = [g for g in scores if g.get('is_live', False)]
                trending.extend(live_games[:2])  # Top 2 live games per sport
                
                # Add close games
                close_games = [g for g in scores 
                             if g.get('is_final', False) and 
                             abs(int(g.get('home_team', {}).get('score', 0)) - 
                                 int(g.get('away_team', {}).get('score', 0))) <= 7]
                trending.extend(close_games[:1])  # Top 1 close game per sport
            
            return trending[:10]  # Return top 10 trending
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Error getting trending games: {e}")
            return []
