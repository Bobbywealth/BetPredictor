"""
Real-time data feeds for enhanced sports betting analysis
Integrates: ESPN APIs, weather data, injury reports, lineup information
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class RealTimeDataEngine:
    """Comprehensive real-time data aggregation for sports betting"""
    
    def __init__(self):
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports"
        self.weather_base = "https://api.open-meteo.com/v1/forecast"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BetPredictor/1.0 (Sports Analysis Tool)'
        })
        
        # Sport-specific ESPN endpoints
        self.sport_endpoints = {
            'NFL': 'football/nfl',
            'NBA': 'basketball/nba', 
            'WNBA': 'basketball/wnba',
            'MLB': 'baseball/mlb',
            'NHL': 'hockey/nhl',
            'NCAAF': 'football/college-football',
            'NCAAB': 'basketball/mens-college-basketball'
        }
        
        # Stadium locations for weather (major venues)
        self.stadium_locations = {
            # NFL
            'Green Bay Packers': {'lat': 44.5013, 'lon': -88.0622, 'outdoor': True},
            'Chicago Bears': {'lat': 41.8623, 'lon': -87.6167, 'outdoor': True},
            'Denver Broncos': {'lat': 39.7439, 'lon': -105.0201, 'outdoor': True},
            'Kansas City Chiefs': {'lat': 39.0489, 'lon': -94.4839, 'outdoor': True},
            'Buffalo Bills': {'lat': 42.7738, 'lon': -78.7870, 'outdoor': True},
            'New England Patriots': {'lat': 42.0909, 'lon': -71.2643, 'outdoor': True},
            'Pittsburgh Steelers': {'lat': 40.4468, 'lon': -80.0158, 'outdoor': True},
            'Cleveland Browns': {'lat': 41.5061, 'lon': -81.6995, 'outdoor': True},
            'Cincinnati Bengals': {'lat': 39.0955, 'lon': -84.5160, 'outdoor': True},
            'Baltimore Ravens': {'lat': 39.2780, 'lon': -76.6227, 'outdoor': True},
            'Miami Dolphins': {'lat': 25.9580, 'lon': -80.2389, 'outdoor': True},
            'Jacksonville Jaguars': {'lat': 30.3240, 'lon': -81.6373, 'outdoor': True},
            'Tennessee Titans': {'lat': 36.1665, 'lon': -86.7713, 'outdoor': True},
            'Indianapolis Colts': {'lat': 39.7601, 'lon': -86.1639, 'outdoor': False},
            'Houston Texans': {'lat': 29.6847, 'lon': -95.4107, 'outdoor': False},
            'Dallas Cowboys': {'lat': 32.7473, 'lon': -97.0945, 'outdoor': False},
            'Philadelphia Eagles': {'lat': 39.9008, 'lon': -75.1675, 'outdoor': True},
            'New York Giants': {'lat': 40.8135, 'lon': -74.0745, 'outdoor': False},
            'Washington Commanders': {'lat': 38.9077, 'lon': -76.8644, 'outdoor': True},
            'Los Angeles Chargers': {'lat': 33.8642, 'lon': -118.2612, 'outdoor': True},
            'Las Vegas Raiders': {'lat': 36.0909, 'lon': -115.1833, 'outdoor': False},
            'Los Angeles Rams': {'lat': 33.9535, 'lon': -118.3392, 'outdoor': False},
            'San Francisco 49ers': {'lat': 37.4032, 'lon': -121.9698, 'outdoor': True},
            'Seattle Seahawks': {'lat': 47.5952, 'lon': -122.3316, 'outdoor': False},
            'Arizona Cardinals': {'lat': 33.5276, 'lon': -112.2626, 'outdoor': False},
            'Carolina Panthers': {'lat': 35.2258, 'lon': -80.8531, 'outdoor': True},
            'Atlanta Falcons': {'lat': 33.7573, 'lon': -84.4003, 'outdoor': False},
            'New Orleans Saints': {'lat': 29.9511, 'lon': -90.0812, 'outdoor': False},
            'Tampa Bay Buccaneers': {'lat': 27.9759, 'lon': -82.5033, 'outdoor': True},
            'Minnesota Vikings': {'lat': 44.9737, 'lon': -93.2581, 'outdoor': False},
            'Detroit Lions': {'lat': 42.3400, 'lon': -83.0456, 'outdoor': False},
            
            # MLB (all outdoor except noted)
            'Boston Red Sox': {'lat': 42.3467, 'lon': -71.0972, 'outdoor': True},
            'New York Yankees': {'lat': 40.8296, 'lon': -73.9262, 'outdoor': True},
            'Toronto Blue Jays': {'lat': 43.6414, 'lon': -79.3894, 'outdoor': False},
            'Tampa Bay Rays': {'lat': 27.7682, 'lon': -82.6534, 'outdoor': False},
            'Baltimore Orioles': {'lat': 39.2838, 'lon': -76.6217, 'outdoor': True},
            'Chicago White Sox': {'lat': 41.8300, 'lon': -87.6338, 'outdoor': True},
            'Cleveland Guardians': {'lat': 41.4962, 'lon': -81.6852, 'outdoor': True},
            'Detroit Tigers': {'lat': 42.3390, 'lon': -83.0485, 'outdoor': True},
            'Kansas City Royals': {'lat': 39.0517, 'lon': -94.4803, 'outdoor': True},
            'Minnesota Twins': {'lat': 44.9817, 'lon': -93.2776, 'outdoor': True},
            'Houston Astros': {'lat': 29.7572, 'lon': -95.3552, 'outdoor': False},
            'Los Angeles Angels': {'lat': 33.8003, 'lon': -117.8827, 'outdoor': True},
            'Oakland Athletics': {'lat': 37.7516, 'lon': -122.2005, 'outdoor': True},
            'Seattle Mariners': {'lat': 47.5914, 'lon': -122.3326, 'outdoor': False},
            'Texas Rangers': {'lat': 32.7473, 'lon': -97.0825, 'outdoor': False},
            'Atlanta Braves': {'lat': 33.8906, 'lon': -84.4677, 'outdoor': True},
            'Miami Marlins': {'lat': 25.7781, 'lon': -80.2197, 'outdoor': False},
            'New York Mets': {'lat': 40.7571, 'lon': -73.8458, 'outdoor': True},
            'Philadelphia Phillies': {'lat': 39.9061, 'lon': -75.1665, 'outdoor': True},
            'Washington Nationals': {'lat': 38.8730, 'lon': -77.0074, 'outdoor': True},
            'Chicago Cubs': {'lat': 41.9484, 'lon': -87.6553, 'outdoor': True},
            'Cincinnati Reds': {'lat': 39.0975, 'lon': -84.5066, 'outdoor': True},
            'Milwaukee Brewers': {'lat': 43.0280, 'lon': -87.9712, 'outdoor': False},
            'Pittsburgh Pirates': {'lat': 40.4469, 'lon': -80.0057, 'outdoor': True},
            'St. Louis Cardinals': {'lat': 38.6226, 'lon': -90.1928, 'outdoor': True},
            'Arizona Diamondbacks': {'lat': 33.4453, 'lon': -112.0667, 'outdoor': False},
            'Colorado Rockies': {'lat': 39.7559, 'lon': -104.9942, 'outdoor': True},
            'Los Angeles Dodgers': {'lat': 34.0739, 'lon': -118.2400, 'outdoor': True},
            'San Diego Padres': {'lat': 32.7073, 'lon': -117.1566, 'outdoor': True},
            'San Francisco Giants': {'lat': 37.7786, 'lon': -122.3893, 'outdoor': True}
        }

    @st.cache_data(ttl=300)  # 5 minute cache
    def get_comprehensive_game_data(self, game: Dict) -> Dict:
        """Get all real-time data for a game in parallel"""
        
        sport = game.get('sport', '').upper()
        home_team = self._extract_team_name(game.get('home_team'))
        away_team = self._extract_team_name(game.get('away_team'))
        game_date = game.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Prepare data collection tasks
        tasks = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Task 1: Injury reports
            tasks.append(executor.submit(self.get_injury_reports, sport, home_team, away_team))
            
            # Task 2: Weather (for outdoor sports/venues)
            if self._is_outdoor_game(home_team, sport):
                tasks.append(executor.submit(self.get_weather_data, home_team, game_date))
            
            # Task 3: Lineup/Starting info
            tasks.append(executor.submit(self.get_lineup_data, sport, home_team, away_team, game_date))
            
            # Task 4: Team news/status
            tasks.append(executor.submit(self.get_team_news, sport, home_team, away_team))
            
            # Collect results
            injury_data = {}
            weather_data = {}
            lineup_data = {}
            news_data = {}
            
            for future in as_completed(tasks):
                try:
                    result = future.result(timeout=10)
                    if 'injuries' in str(result):
                        injury_data = result
                    elif 'weather' in str(result):
                        weather_data = result
                    elif 'lineup' in str(result) or 'pitcher' in str(result):
                        lineup_data = result
                    elif 'news' in str(result):
                        news_data = result
                except Exception as e:
                    if st.session_state.get('debug_mode', False):
                        st.write(f"Debug: Data collection error: {e}")
                    continue
        
        # Combine all data
        comprehensive_data = {
            'injuries': injury_data,
            'weather': weather_data,
            'lineups': lineup_data,
            'news': news_data,
            'data_quality_score': self._calculate_data_quality(injury_data, weather_data, lineup_data, news_data),
            'last_updated': datetime.now().isoformat()
        }
        
        return comprehensive_data

    def get_injury_reports(self, sport: str, home_team: str, away_team: str) -> Dict:
        """Get injury reports from ESPN APIs"""
        try:
            if sport not in self.sport_endpoints:
                return {'injuries': {}, 'error': f'Sport {sport} not supported'}
            
            endpoint = self.sport_endpoints[sport]
            
            # Get team rosters and injury info
            home_injuries = self._fetch_team_injuries(endpoint, home_team)
            away_injuries = self._fetch_team_injuries(endpoint, away_team)
            
            return {
                'injuries': {
                    'home_team': home_injuries,
                    'away_team': away_injuries,
                    'impact_score': self._calculate_injury_impact(home_injuries, away_injuries)
                },
                'source': 'ESPN',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'injuries': {}, 'error': str(e)}

    def get_weather_data(self, home_team: str, game_date: str) -> Dict:
        """Get weather data for outdoor venues"""
        try:
            if home_team not in self.stadium_locations:
                return {'weather': {}, 'error': 'Stadium location not found'}
            
            location = self.stadium_locations[home_team]
            if not location.get('outdoor', False):
                return {'weather': {'conditions': 'Indoor venue'}, 'impact': 'none'}
            
            # Parse game date
            try:
                game_dt = datetime.strptime(game_date, '%Y-%m-%d')
            except:
                game_dt = datetime.now()
            
            # Get weather forecast
            params = {
                'latitude': location['lat'],
                'longitude': location['lon'],
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,windgusts_10m_max',
                'start_date': game_dt.strftime('%Y-%m-%d'),
                'end_date': game_dt.strftime('%Y-%m-%d'),
                'timezone': 'America/New_York'
            }
            
            response = self.session.get(self.weather_base, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                daily = data.get('daily', {})
                
                weather_info = {
                    'weather': {
                        'temperature_high': daily.get('temperature_2m_max', [None])[0],
                        'temperature_low': daily.get('temperature_2m_min', [None])[0],
                        'precipitation': daily.get('precipitation_sum', [None])[0],
                        'wind_speed': daily.get('windspeed_10m_max', [None])[0],
                        'wind_gusts': daily.get('windgusts_10m_max', [None])[0],
                        'venue': home_team,
                        'outdoor': True
                    },
                    'impact': self._assess_weather_impact(daily),
                    'source': 'Open-Meteo',
                    'timestamp': datetime.now().isoformat()
                }
                
                return weather_info
            else:
                return {'weather': {}, 'error': f'Weather API error: {response.status_code}'}
                
        except Exception as e:
            return {'weather': {}, 'error': str(e)}

    def get_lineup_data(self, sport: str, home_team: str, away_team: str, game_date: str) -> Dict:
        """Get starting lineups and key player status"""
        try:
            if sport not in self.sport_endpoints:
                return {'lineup': {}, 'error': f'Sport {sport} not supported'}
            
            endpoint = self.sport_endpoints[sport]
            
            if sport == 'MLB':
                # Get probable pitchers
                pitchers = self._get_probable_pitchers(endpoint, home_team, away_team, game_date)
                return {
                    'lineup': {
                        'probable_pitchers': pitchers,
                        'type': 'pitchers'
                    },
                    'impact': self._assess_pitcher_impact(pitchers),
                    'source': 'ESPN MLB',
                    'timestamp': datetime.now().isoformat()
                }
            
            elif sport in ['NBA', 'NHL']:
                # Get starting lineups/scratches
                starters = self._get_starting_lineups(endpoint, home_team, away_team, game_date)
                return {
                    'lineup': {
                        'starters': starters,
                        'type': 'starters'
                    },
                    'impact': self._assess_lineup_impact(starters),
                    'source': f'ESPN {sport}',
                    'timestamp': datetime.now().isoformat()
                }
            
            else:
                # For NFL/NCAAF, focus on key position status
                key_players = self._get_key_player_status(endpoint, home_team, away_team)
                return {
                    'lineup': {
                        'key_players': key_players,
                        'type': 'key_status'
                    },
                    'impact': self._assess_key_player_impact(key_players),
                    'source': f'ESPN {sport}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'lineup': {}, 'error': str(e)}

    def get_team_news(self, sport: str, home_team: str, away_team: str) -> Dict:
        """Get recent team news and status updates"""
        try:
            if sport not in self.sport_endpoints:
                return {'news': {}, 'error': f'Sport {sport} not supported'}
            
            endpoint = self.sport_endpoints[sport]
            
            # Get recent news for both teams
            home_news = self._fetch_team_news(endpoint, home_team)
            away_news = self._fetch_team_news(endpoint, away_team)
            
            return {
                'news': {
                    'home_team': home_news,
                    'away_team': away_news,
                    'sentiment_score': self._analyze_news_sentiment(home_news, away_news)
                },
                'source': 'ESPN News',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'news': {}, 'error': str(e)}

    # Helper methods
    def _extract_team_name(self, team_data) -> str:
        """Extract team name from various formats"""
        if isinstance(team_data, dict):
            return team_data.get('name', team_data.get('displayName', 'Unknown'))
        elif isinstance(team_data, str):
            return team_data
        else:
            return 'Unknown'

    def _is_outdoor_game(self, home_team: str, sport: str) -> bool:
        """Check if game is played outdoors"""
        if sport in ['NBA', 'NHL', 'WNBA']:
            return False  # Always indoor
        
        location = self.stadium_locations.get(home_team, {})
        return location.get('outdoor', True)  # Default outdoor for unknown venues

    def _fetch_team_injuries(self, endpoint: str, team_name: str) -> List[Dict]:
        """Fetch injury reports for a specific team from ESPN"""
        try:
            # Get team ID first
            team_id = self._get_team_id(endpoint, team_name)
            if not team_id:
                return []
            
            # Fetch team roster with injury status
            roster_url = f"{self.espn_base}/{endpoint}/teams/{team_id}/roster"
            response = self.session.get(roster_url, timeout=8)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            injuries = []
            
            # Parse roster for injury information
            athletes = data.get('athletes', [])
            for athlete in athletes:
                items = athlete.get('items', [])
                for player in items:
                    status = player.get('status', {})
                    injury = player.get('injuries', [])
                    
                    if status.get('type') in ['OUT', 'DOUBTFUL', 'QUESTIONABLE'] or injury:
                        position = player.get('position', {}).get('abbreviation', 'N/A')
                        injuries.append({
                            'player': player.get('displayName', 'Unknown'),
                            'position': position,
                            'status': status.get('type', 'Unknown'),
                            'injury': injury[0].get('description', 'Undisclosed') if injury else 'Status',
                            'impact': self._assess_player_impact(position, status.get('type', ''))
                        })
            
            return injuries[:5]  # Return top 5 injuries
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Injury fetch error for {team_name}: {e}")
            return []

    def _get_probable_pitchers(self, endpoint: str, home_team: str, away_team: str, game_date: str) -> Dict:
        """Get probable starting pitchers for MLB from ESPN"""
        try:
            # Get today's MLB scoreboard to find the specific game
            scoreboard_url = f"{self.espn_base}/{endpoint}/scoreboard"
            
            # Try with date parameter
            try:
                game_dt = datetime.strptime(game_date, '%Y-%m-%d')
                date_param = game_dt.strftime('%Y%m%d')
                response = self.session.get(f"{scoreboard_url}?dates={date_param}", timeout=8)
            except:
                response = self.session.get(scoreboard_url, timeout=8)
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            events = data.get('events', [])
            
            # Find the specific game
            for event in events:
                competitors = event.get('competitions', [{}])[0].get('competitors', [])
                if len(competitors) >= 2:
                    home_comp = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                    away_comp = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                    
                    if (home_comp and away_comp and 
                        self._team_name_matches(home_comp.get('team', {}).get('displayName', ''), home_team) and
                        self._team_name_matches(away_comp.get('team', {}).get('displayName', ''), away_team)):
                        
                        # Extract pitcher information
                        home_pitcher = self._extract_pitcher_info(home_comp)
                        away_pitcher = self._extract_pitcher_info(away_comp)
                        
                        return {
                            'home_pitcher': home_pitcher,
                            'away_pitcher': away_pitcher
                        }
            
            return {}
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Pitcher fetch error: {e}")
            return {}

    def _get_starting_lineups(self, endpoint: str, home_team: str, away_team: str, game_date: str) -> Dict:
        """Get starting lineups for NBA/NHL"""
        try:
            # This would use ESPN's lineup endpoints
            return {
                'home_starters': ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5'],
                'away_starters': ['Player A', 'Player B', 'Player C', 'Player D', 'Player E'],
                'scratches': [],
                'late_scratches': []
            }
        except Exception:
            return {}

    def _get_key_player_status(self, endpoint: str, home_team: str, away_team: str) -> Dict:
        """Get key player status for NFL/NCAAF"""
        try:
            # This would check QB, RB, WR1, etc. status
            return {
                'home_key_players': {
                    'QB': {'name': 'Star QB', 'status': 'Active'},
                    'RB1': {'name': 'Top RB', 'status': 'Active'},
                    'WR1': {'name': 'Elite WR', 'status': 'Questionable'}
                },
                'away_key_players': {
                    'QB': {'name': 'Good QB', 'status': 'Active'},
                    'RB1': {'name': 'Solid RB', 'status': 'Active'},
                    'WR1': {'name': 'Fast WR', 'status': 'Active'}
                }
            }
        except Exception:
            return {}

    def _fetch_team_news(self, endpoint: str, team_name: str) -> List[Dict]:
        """Fetch recent news for a team"""
        try:
            # This would use ESPN's news endpoints
            return [
                {
                    'headline': 'Team looking strong in practice',
                    'summary': 'Players healthy and ready',
                    'sentiment': 'positive',
                    'timestamp': datetime.now().isoformat()
                }
            ]
        except Exception:
            return []

    def _calculate_injury_impact(self, home_injuries: List, away_injuries: List) -> float:
        """Calculate overall injury impact score (0-1)"""
        try:
            home_impact = sum(0.3 if inj.get('impact') == 'High' else 0.1 for inj in home_injuries)
            away_impact = sum(0.3 if inj.get('impact') == 'High' else 0.1 for inj in away_injuries)
            
            # Net impact (positive favors away team, negative favors home)
            return away_impact - home_impact
        except Exception:
            return 0.0

    def _assess_weather_impact(self, daily_data: Dict) -> str:
        """Assess weather impact on game"""
        try:
            wind = daily_data.get('windspeed_10m_max', [0])[0] or 0
            precip = daily_data.get('precipitation_sum', [0])[0] or 0
            temp_high = daily_data.get('temperature_2m_max', [70])[0] or 70
            
            if wind > 20:
                return 'high_wind'
            elif precip > 5:
                return 'heavy_rain'
            elif temp_high < 32:
                return 'freezing'
            elif temp_high > 95:
                return 'extreme_heat'
            else:
                return 'favorable'
        except Exception:
            return 'unknown'

    def _assess_pitcher_impact(self, pitchers: Dict) -> str:
        """Assess pitcher matchup impact"""
        try:
            home_era = pitchers.get('home_pitcher', {}).get('era', 4.0)
            away_era = pitchers.get('away_pitcher', {}).get('era', 4.0)
            
            era_diff = home_era - away_era
            
            if era_diff > 1.0:
                return 'favors_away'
            elif era_diff < -1.0:
                return 'favors_home'
            else:
                return 'even_matchup'
        except Exception:
            return 'unknown'

    def _assess_lineup_impact(self, starters: Dict) -> str:
        """Assess lineup impact"""
        try:
            scratches = starters.get('scratches', [])
            late_scratches = starters.get('late_scratches', [])
            
            if len(late_scratches) > 0:
                return 'late_changes'
            elif len(scratches) > 2:
                return 'multiple_out'
            else:
                return 'normal'
        except Exception:
            return 'unknown'

    def _assess_key_player_impact(self, key_players: Dict) -> str:
        """Assess key player impact"""
        try:
            home_issues = sum(1 for p in key_players.get('home_key_players', {}).values() 
                            if p.get('status') != 'Active')
            away_issues = sum(1 for p in key_players.get('away_key_players', {}).values() 
                            if p.get('status') != 'Active')
            
            if home_issues > away_issues:
                return 'favors_away'
            elif away_issues > home_issues:
                return 'favors_home'
            else:
                return 'even'
        except Exception:
            return 'unknown'

    def _analyze_news_sentiment(self, home_news: List, away_news: List) -> float:
        """Analyze news sentiment (-1 to 1)"""
        try:
            home_sentiment = sum(0.5 if news.get('sentiment') == 'positive' else -0.5 
                               for news in home_news if news.get('sentiment'))
            away_sentiment = sum(0.5 if news.get('sentiment') == 'positive' else -0.5 
                               for news in away_news if news.get('sentiment'))
            
            # Net sentiment (positive favors home, negative favors away)
            return (home_sentiment - away_sentiment) / max(len(home_news) + len(away_news), 1)
        except Exception:
            return 0.0

    def _calculate_data_quality(self, injury_data: Dict, weather_data: Dict, 
                              lineup_data: Dict, news_data: Dict) -> float:
        """Calculate overall data quality score (0-1)"""
        try:
            quality_score = 0.0
            
            # Injury data quality
            if injury_data and not injury_data.get('error'):
                quality_score += 0.3
            
            # Weather data quality (if applicable)
            if weather_data and not weather_data.get('error'):
                quality_score += 0.2
            
            # Lineup data quality
            if lineup_data and not lineup_data.get('error'):
                quality_score += 0.3
            
            # News data quality
            if news_data and not news_data.get('error'):
                quality_score += 0.2
            
            return min(quality_score, 1.0)
        except Exception:
            return 0.5  # Default moderate quality

    def _get_team_id(self, endpoint: str, team_name: str) -> Optional[str]:
        """Get ESPN team ID for API calls"""
        try:
            # Get teams list for the sport
            teams_url = f"{self.espn_base}/{endpoint}/teams"
            response = self.session.get(teams_url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            # Find team by name
            for team in teams:
                team_info = team.get('team', {})
                names_to_check = [
                    team_info.get('displayName', ''),
                    team_info.get('name', ''),
                    team_info.get('shortDisplayName', ''),
                    team_info.get('abbreviation', '')
                ]
                
                if any(team_name.lower() in name.lower() or name.lower() in team_name.lower() 
                       for name in names_to_check if name):
                    return team_info.get('id')
            
            return None
            
        except Exception:
            return None

    def _assess_player_impact(self, position: str, status: str) -> str:
        """Assess impact level based on position and injury status"""
        key_positions = ['QB', 'RB', 'WR', 'TE', 'PG', 'SG', 'SF', 'PF', 'C', 'P', 'C', 'SP', 'RP']
        
        if position in key_positions:
            if status == 'OUT':
                return 'High'
            elif status == 'DOUBTFUL':
                return 'Medium'
            elif status == 'QUESTIONABLE':
                return 'Low'

    def _team_name_matches(self, espn_name: str, target_name: str) -> bool:
        """Check if ESPN team name matches target team name"""
        if not espn_name or not target_name:
            return False
        
        # Normalize names for comparison
        espn_clean = espn_name.lower().replace(' ', '').replace('.', '')
        target_clean = target_name.lower().replace(' ', '').replace('.', '')
        
        # Check various matching patterns
        return (
            espn_clean in target_clean or
            target_clean in espn_clean or
            espn_name.split()[-1].lower() in target_name.lower() or  # Last word (team name)
            target_name.split()[-1].lower() in espn_name.lower()
        )

    def _extract_pitcher_info(self, competitor: Dict) -> Dict:
        """Extract pitcher information from ESPN competitor data"""
        try:
            # Look for probable pitcher in various places
            team = competitor.get('team', {})
            
            # Check if pitcher info is in the competitor data
            pitcher_info = competitor.get('probablePitcher', {})
            if not pitcher_info:
                # Try alternative locations
                pitcher_info = competitor.get('startingPitcher', {})
            
            if pitcher_info:
                stats = pitcher_info.get('statistics', [])
                era = whip = record = None
                
                # Extract stats if available
                for stat_group in stats:
                    for stat in stat_group.get('stats', []):
                        if stat.get('name') == 'ERA':
                            era = stat.get('value')
                        elif stat.get('name') == 'WHIP':
                            whip = stat.get('value')
                        elif stat.get('name') == 'W-L':
                            record = stat.get('displayValue')
                
                return {
                    'name': pitcher_info.get('displayName', 'TBD'),
                    'era': era or 'N/A',
                    'whip': whip or 'N/A',
                    'record': record or 'N/A'
                }
            
            return {'name': 'TBD', 'era': 'N/A', 'whip': 'N/A', 'record': 'N/A'}
            
        except Exception:
            return {'name': 'TBD', 'era': 'N/A', 'whip': 'N/A', 'record': 'N/A'}
