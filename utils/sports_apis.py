import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import json

class SportsAPIManager:
    """Manager class for integrating multiple sports APIs"""
    
    def __init__(self):
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports"
        self.sportsdb_base_url = "https://www.thesportsdb.com/api/v1/json/3"
        self.api_football_base_url = "https://api-football-v1.p.rapidapi.com/v3"
        
    def get_espn_scores(self, sport="football", league="nfl"):
        """Get live scores from ESPN API (free)"""
        try:
            sport_mapping = {
                "football": "football",
                "basketball": "basketball", 
                "baseball": "baseball",
                "hockey": "hockey"
            }
            
            league_mapping = {
                "football": "nfl",
                "basketball": "nba",
                "baseball": "mlb", 
                "hockey": "nhl"
            }
            
            sport_key = sport_mapping.get(sport, "football")
            league_key = league_mapping.get(sport, "nfl")
            
            url = f"{self.espn_base_url}/{sport_key}/{league_key}/scoreboard"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            games = []
            
            if 'events' in data:
                for event in data['events']:
                    try:
                        # Extract game information
                        game_date = event.get('date', '')
                        status = event.get('status', {}).get('type', {}).get('description', 'Unknown')
                        
                        competitions = event.get('competitions', [])
                        if competitions:
                            competition = competitions[0]
                            competitors = competition.get('competitors', [])
                            
                            if len(competitors) >= 2:
                                team1 = competitors[0]['team']['displayName']
                                team2 = competitors[1]['team']['displayName']
                                
                                # Get scores
                                team1_score = int(competitors[0].get('score', 0))
                                team2_score = int(competitors[1].get('score', 0))
                                
                                # Determine home/away
                                if competitors[0].get('homeAway') == 'home':
                                    home_team, away_team = team1, team2
                                    home_score, away_score = team1_score, team2_score
                                else:
                                    home_team, away_team = team2, team1
                                    home_score, away_score = team2_score, team1_score
                                
                                games.append({
                                    'date': game_date[:10] if game_date else datetime.now().strftime('%Y-%m-%d'),
                                    'team1': home_team,
                                    'team2': away_team,
                                    'team1_score': home_score,
                                    'team2_score': away_score,
                                    'sport': sport,
                                    'league': league_key.upper(),
                                    'status': status,
                                    'source': 'ESPN'
                                })
                    except Exception as e:
                        continue  # Skip malformed games
            
            return pd.DataFrame(games)
            
        except Exception as e:
            st.error(f"Error fetching ESPN data: {str(e)}")
            return pd.DataFrame()
    
    def get_sportsdb_data(self, sport="Soccer"):
        """Get data from TheSportsDB (free)"""
        try:
            # Get recent matches for a league
            sport_mapping = {
                "football": "Soccer",
                "basketball": "Basketball",
                "baseball": "Baseball",
                "american_football": "American Football"
            }
            
            sport_name = sport_mapping.get(sport, "Soccer")
            
            # Get leagues for this sport
            leagues_url = f"{self.sportsdb_base_url}/search_all_leagues.php?s={sport_name}"
            leagues_response = requests.get(leagues_url, timeout=10)
            
            if leagues_response.status_code == 200:
                leagues_data = leagues_response.json()
                if leagues_data.get('leagues'):
                    # Get first major league
                    league_id = leagues_data['leagues'][0]['idLeague']
                    
                    # Get recent events
                    events_url = f"{self.sportsdb_base_url}/eventspastleague.php?id={league_id}"
                    events_response = requests.get(events_url, timeout=10)
                    
                    if events_response.status_code == 200:
                        events_data = events_response.json()
                        games = []
                        
                        if events_data.get('events'):
                            for event in events_data['events'][:50]:  # Limit to 50 recent games
                                try:
                                    games.append({
                                        'date': event.get('dateEvent', ''),
                                        'team1': event.get('strHomeTeam', ''),
                                        'team2': event.get('strAwayTeam', ''),
                                        'team1_score': int(event.get('intHomeScore', 0)),
                                        'team2_score': int(event.get('intAwayScore', 0)),
                                        'sport': sport,
                                        'league': event.get('strLeague', ''),
                                        'status': 'Final',
                                        'source': 'TheSportsDB'
                                    })
                                except (ValueError, TypeError):
                                    continue
                        
                        return pd.DataFrame(games)
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error fetching TheSportsDB data: {str(e)}")
            return pd.DataFrame()
    
    def get_api_football_data(self, api_key=None):
        """Get data from API-Football (requires API key)"""
        if not api_key:
            return pd.DataFrame()
        
        try:
            headers = {
                'X-RapidAPI-Key': api_key,
                'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
            }
            
            # Get live fixtures
            url = f"{self.api_football_base_url}/fixtures"
            params = {
                'live': 'all'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                games = []
                
                if data.get('response'):
                    for fixture in data['response'][:20]:  # Limit to 20 games
                        try:
                            teams = fixture.get('teams', {})
                            goals = fixture.get('goals', {})
                            fixture_info = fixture.get('fixture', {})
                            
                            games.append({
                                'date': fixture_info.get('date', '')[:10],
                                'team1': teams.get('home', {}).get('name', ''),
                                'team2': teams.get('away', {}).get('name', ''),
                                'team1_score': goals.get('home', 0) or 0,
                                'team2_score': goals.get('away', 0) or 0,
                                'sport': 'football',
                                'league': fixture.get('league', {}).get('name', ''),
                                'status': fixture_info.get('status', {}).get('long', 'Unknown'),
                                'source': 'API-Football'
                            })
                        except Exception as e:
                            continue
                
                return pd.DataFrame(games)
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error fetching API-Football data: {str(e)}")
            return pd.DataFrame()
    
    def get_mysportsfeeds_data(self, api_key=None, password=None):
        """Get data from MySportsFeeds (requires API key)"""
        if not api_key:
            return pd.DataFrame()
        
        try:
            # MySportsFeeds uses basic auth
            auth = (api_key, password or "MYSPORTSFEEDS")
            base_url = "https://api.mysportsfeeds.com/v2.1/pull"
            
            # Get current season games for NFL
            season = "current"
            url = f"{base_url}/nfl/{season}/games.json"
            
            response = requests.get(url, auth=auth, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                games = []
                
                if data.get('games'):
                    for game in data['games'][:30]:  # Limit to 30 games
                        try:
                            schedule = game.get('schedule', {})
                            score = game.get('score', {})
                            
                            home_team = schedule.get('homeTeam', {}).get('abbreviation', '')
                            away_team = schedule.get('awayTeam', {}).get('abbreviation', '')
                            
                            home_score = score.get('homeScoreTotal', 0) if score else 0
                            away_score = score.get('awayScoreTotal', 0) if score else 0
                            
                            games.append({
                                'date': schedule.get('startTime', '')[:10],
                                'team1': home_team,
                                'team2': away_team,
                                'team1_score': int(home_score),
                                'team2_score': int(away_score),
                                'sport': 'american_football',
                                'league': 'NFL',
                                'status': 'Final' if score else 'Scheduled',
                                'source': 'MySportsFeeds'
                            })
                        except (ValueError, TypeError):
                            continue
                
                return pd.DataFrame(games)
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error fetching MySportsFeeds data: {str(e)}")
            return pd.DataFrame()
    
    def get_all_data(self, api_keys=None):
        """Fetch data from all available APIs and combine them"""
        all_data = []
        
        # ESPN data (always free)
        st.info("Fetching data from ESPN...")
        for sport in ['football', 'basketball', 'baseball']:
            espn_data = self.get_espn_scores(sport=sport)
            if not espn_data.empty:
                all_data.append(espn_data)
        
        # TheSportsDB data (always free)
        st.info("Fetching data from TheSportsDB...")
        for sport in ['football', 'basketball', 'baseball']:
            sportsdb_data = self.get_sportsdb_data(sport=sport)
            if not sportsdb_data.empty:
                all_data.append(sportsdb_data)
        
        # API-Football data (if key provided)
        if api_keys and api_keys.get('api_football'):
            st.info("Fetching data from API-Football...")
            api_football_data = self.get_api_football_data(api_keys['api_football'])
            if not api_football_data.empty:
                all_data.append(api_football_data)
        
        # MySportsFeeds data (if key provided)
        if api_keys and api_keys.get('mysportsfeeds'):
            st.info("Fetching data from MySportsFeeds...")
            mysportsfeeds_data = self.get_mysportsfeeds_data(
                api_keys['mysportsfeeds'], 
                api_keys.get('mysportsfeeds_password')
            )
            if not mysportsfeeds_data.empty:
                all_data.append(mysportsfeeds_data)
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # Clean and standardize the data
            combined_data = self._clean_combined_data(combined_data)
            
            st.success(f"Successfully fetched {len(combined_data)} games from {len(all_data)} API sources!")
            return combined_data
        else:
            st.warning("No data could be fetched from any API source.")
            return pd.DataFrame()
    
    def _clean_combined_data(self, data):
        """Clean and standardize the combined API data"""
        try:
            # Remove duplicates based on teams, date, and scores
            data = data.drop_duplicates(subset=['team1', 'team2', 'date', 'team1_score', 'team2_score'])
            
            # Ensure date format is consistent
            data['date'] = pd.to_datetime(data['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Remove rows with missing essential data
            data = data.dropna(subset=['team1', 'team2', 'date'])
            
            # Ensure scores are numeric
            data['team1_score'] = pd.to_numeric(data['team1_score'], errors='coerce').fillna(0)
            data['team2_score'] = pd.to_numeric(data['team2_score'], errors='coerce')
            
            # Clean team names
            data['team1'] = data['team1'].str.strip().str.title()
            data['team2'] = data['team2'].str.strip().str.title()
            
            # Only keep completed games for training
            completed_statuses = ['Final', 'Completed', 'Full Time', 'Game Over']
            data = data[data['status'].isin(completed_statuses) | (data['team1_score'] + data['team2_score'] > 0)]
            
            return data.reset_index(drop=True)
            
        except Exception as e:
            st.error(f"Error cleaning combined data: {str(e)}")
            return data

    def get_live_odds(self, api_key=None):
        """Get live betting odds if API supports it"""
        # This would be implemented with premium APIs that provide odds
        # For now, return empty DataFrame
        return pd.DataFrame()
    
    def test_api_connection(self, api_name, api_key=None):
        """Test connection to a specific API"""
        try:
            if api_name.lower() == 'espn':
                test_data = self.get_espn_scores('football', 'nfl')
                return not test_data.empty, f"ESPN: Retrieved {len(test_data)} games"
            
            elif api_name.lower() == 'thesportsdb':
                test_data = self.get_sportsdb_data('football')
                return not test_data.empty, f"TheSportsDB: Retrieved {len(test_data)} games"
            
            elif api_name.lower() == 'api_football' and api_key:
                test_data = self.get_api_football_data(api_key)
                return not test_data.empty, f"API-Football: Retrieved {len(test_data)} games"
            
            elif api_name.lower() == 'mysportsfeeds' and api_key:
                test_data = self.get_mysportsfeeds_data(api_key)
                return not test_data.empty, f"MySportsFeeds: Retrieved {len(test_data)} games"
            
            else:
                return False, f"API {api_name} not configured or missing API key"
                
        except Exception as e:
            return False, f"Error testing {api_name}: {str(e)}"