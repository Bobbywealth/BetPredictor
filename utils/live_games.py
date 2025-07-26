import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import json

class LiveGamesManager:
    """Manager for fetching and displaying live/upcoming games with detailed information"""
    
    def __init__(self):
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports"
        self.sportsdb_base_url = "https://www.thesportsdb.com/api/v1/json/3"
        
    def get_espn_live_schedule(self, sport="football", league="nfl", date=None):
        """Get live and upcoming games from ESPN with detailed info"""
        try:
            sport_mapping = {
                "basketball": "basketball", 
                "baseball": "baseball",
                "soccer": "soccer"
            }
            
            league_mapping = {
                "basketball": "nba",
                "baseball": "mlb", 
                "soccer": "mls"
            }
            
            sport_key = sport_mapping.get(sport, "football")
            league_key = league_mapping.get(sport, "nfl")
            
            # Add date parameter for specific dates - ESPN uses YYYYMMDD format
            url = f"{self.espn_base_url}/{sport_key}/{league_key}/scoreboard"
            if date:
                # Ensure date is in correct format and add proper parameter
                if len(date) == 8 and date.isdigit():
                    url += f"?dates={date}"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            games = []
            
            # Debug: log the API response structure
            if st.session_state.get('debug_mode', False):
                st.write(f"ESPN API Response keys: {list(data.keys())}")
                if 'events' in data:
                    st.write(f"Found {len(data['events'])} events")
            
            if 'events' in data and len(data['events']) > 0:
                for event in data['events']:
                    try:
                        # Extract detailed game information
                        game_date = event.get('date', '')
                        game_name = event.get('name', '')
                        short_name = event.get('shortName', '')
                        status_info = event.get('status', {})
                        status_type = status_info.get('type', {})
                        
                        # Get venue information
                        competitions = event.get('competitions', [])
                        venue_info = {}
                        broadcast_info = []
                        
                        if competitions:
                            competition = competitions[0]
                            venue = competition.get('venue', {})
                            venue_info = {
                                'name': venue.get('fullName', 'TBD'),
                                'city': venue.get('address', {}).get('city', ''),
                                'state': venue.get('address', {}).get('state', ''),
                                'capacity': venue.get('capacity', 'N/A')
                            }
                            
                            # Get broadcast information
                            broadcasts = competition.get('broadcasts', [])
                            for broadcast in broadcasts:
                                names = broadcast.get('names', [])
                                if names:
                                    broadcast_info.extend(names)
                            
                            # Get team information
                            competitors = competition.get('competitors', [])
                            
                            if len(competitors) >= 2:
                                home_team = competitors[0] if competitors[0].get('homeAway') == 'home' else competitors[1]
                                away_team = competitors[1] if competitors[0].get('homeAway') == 'home' else competitors[0]
                                
                                # Team details
                                home_team_info = {
                                    'name': home_team['team']['displayName'],
                                    'abbreviation': home_team['team'].get('abbreviation', ''),
                                    'logo': home_team['team'].get('logo', ''),
                                    'color': home_team['team'].get('color', ''),
                                    'record': home_team.get('records', [{}])[0].get('summary', '') if home_team.get('records') else '',
                                    'score': int(home_team.get('score', 0))
                                }
                                
                                away_team_info = {
                                    'name': away_team['team']['displayName'],
                                    'abbreviation': away_team['team'].get('abbreviation', ''),
                                    'logo': away_team['team'].get('logo', ''),
                                    'color': away_team['team'].get('color', ''),
                                    'record': away_team.get('records', [{}])[0].get('summary', '') if away_team.get('records') else '',
                                    'score': int(away_team.get('score', 0))
                                }
                                
                                # Parse game time
                                game_datetime = None
                                display_time = "TBD"
                                if game_date:
                                    try:
                                        game_datetime = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                                        # Convert to local time for display
                                        from datetime import timezone
                                        local_time = game_datetime.replace(tzinfo=timezone.utc).astimezone()
                                        display_time = local_time.strftime('%I:%M %p ET')
                                    except:
                                        display_time = "TBD"
                                
                                games.append({
                                    'game_id': event.get('id', ''),
                                    'game_name': game_name,
                                    'short_name': short_name,
                                    'date': game_date[:10] if game_date else datetime.now().strftime('%Y-%m-%d'),
                                    'time': display_time,
                                    'datetime': game_datetime,
                                    'status': status_type.get('description', 'Unknown'),
                                    'status_detail': status_info.get('displayClock', ''),
                                    'period': status_info.get('period', ''),
                                    'home_team': home_team_info,
                                    'away_team': away_team_info,
                                    'venue': venue_info,
                                    'broadcasts': broadcast_info,
                                    'sport': sport,
                                    'league': league_key.upper(),
                                    'source': 'ESPN'
                                })
                    except Exception as e:
                        continue  # Skip malformed games
            
            return pd.DataFrame(games)
            
        except Exception as e:
            st.error(f"Error fetching ESPN schedule: {str(e)}")
            return pd.DataFrame()
    
    def get_upcoming_games_all_sports(self):
        """Get real games for soccer, baseball, and basketball only"""
        all_games = []
        
        # Get today and tomorrow's dates in YYYYMMDD format
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        dates_to_check = [
            yesterday.strftime('%Y%m%d'),  # Yesterday for any ongoing games
            today.strftime('%Y%m%d'),     # Today
            tomorrow.strftime('%Y%m%d')   # Tomorrow
        ]
        
        # Try ESPN for basketball and baseball - first without dates, then with dates
        espn_sports = [
            ('basketball', 'nba'),
            ('baseball', 'mlb')
        ]
        
        # Try ESPN but handle off-season gracefully
        for sport, league in espn_sports:
            try:
                games_df = self.get_espn_live_schedule(sport, league, None)
                if not games_df.empty:
                    all_games.append(games_df)
            except Exception as e:
                # ESPN may return 400 during off-season, which is expected
                if st.session_state.get('debug_mode', False):
                    st.write(f"ESPN {sport}/{league}: Off-season or no games")
        
        # Try TheSportsDB for soccer (more comprehensive soccer coverage)
        try:
            soccer_games = self.get_sportsdb_soccer_games()
            if not soccer_games.empty:
                all_games.append(soccer_games)
        except Exception as e:
            pass
        
        # ESPN soccer leagues are often limited, TheSportsDB is more reliable for soccer
        
        if all_games:
            combined_df = pd.concat(all_games, ignore_index=True)
            # Remove duplicates based on game_id
            if 'game_id' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['game_id'], keep='first')
            return combined_df
        else:
            return pd.DataFrame()
    
    def get_sportsdb_soccer_games(self):
        """Get soccer games from TheSportsDB API"""
        try:
            # Get major soccer leagues
            leagues_to_check = [
                '4328',  # English Premier League
                '4335',  # Spanish La Liga
                '4331',  # German Bundesliga
                '4332',  # Italian Serie A
                '4334',  # French Ligue 1
                '4346'   # UEFA Champions League
            ]
            
            all_soccer_games = []
            
            for league_id in leagues_to_check:
                try:
                    # Get both past and upcoming events for this league
                    past_url = f"{self.sportsdb_base_url}/eventspastleague.php?id={league_id}"
                    next_url = f"{self.sportsdb_base_url}/eventsnextleague.php?id={league_id}"
                    
                    # Try past events first
                    response = requests.get(past_url, timeout=10)
                    
                    # Also try upcoming events
                    upcoming_response = requests.get(next_url, timeout=10)
                    
                    # Process both past and upcoming events
                    events_to_process = []
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('events'):
                            events_to_process.extend(data['events'][:5])
                    
                    if upcoming_response.status_code == 200:
                        upcoming_data = upcoming_response.json()
                        if upcoming_data.get('events'):
                            events_to_process.extend(upcoming_data['events'][:5])
                    
                    # Process all events
                    for event in events_to_process:
                        try:
                            # Parse date
                            event_date = event.get('dateEvent', '')
                            if event_date:
                                # Accept any valid game data, regardless of date
                                from datetime import datetime, timedelta
                                try:
                                    game_date = datetime.strptime(event_date, '%Y-%m-%d')
                                except:
                                    continue
                                
                                # Determine game status
                                status = 'Scheduled'
                                if event.get('intHomeScore') is not None and event.get('intAwayScore') is not None:
                                    if event.get('intHomeScore') != '' and event.get('intAwayScore') != '':
                                        status = 'Final'
                                
                                all_soccer_games.append({
                                    'game_id': f"sdb_{event.get('idEvent', '')}",
                                    'game_name': f"{event.get('strHomeTeam', '')} vs {event.get('strAwayTeam', '')}",
                                    'short_name': f"{event.get('strHomeTeam', '')[:3]} vs {event.get('strAwayTeam', '')[:3]}",
                                    'date': event_date,
                                    'time': event.get('strTime', 'TBD'),
                                    'datetime': game_date,
                                    'status': status,
                                    'status_detail': '',
                                    'period': '',
                                    'home_team': {
                                        'name': event.get('strHomeTeam', ''),
                                        'abbreviation': event.get('strHomeTeam', '')[:3],
                                        'logo': event.get('strHomeTeamBadge', ''),
                                        'color': '',
                                        'record': '',
                                        'score': int(event.get('intHomeScore', 0) or 0)
                                    },
                                    'away_team': {
                                        'name': event.get('strAwayTeam', ''),
                                        'abbreviation': event.get('strAwayTeam', '')[:3],
                                        'logo': event.get('strAwayTeamBadge', ''),
                                        'color': '',
                                        'record': '',
                                        'score': int(event.get('intAwayScore', 0) or 0)
                                    },
                                    'venue': {
                                        'name': event.get('strVenue', 'TBD'),
                                        'city': event.get('strCity', ''),
                                        'state': event.get('strCountry', ''),
                                        'capacity': 'N/A'
                                    },
                                    'broadcasts': [],
                                    'sport': 'soccer',
                                    'league': event.get('strLeague', 'Soccer'),
                                    'source': 'TheSportsDB'
                                })
                        except Exception as e:
                            continue
                except Exception as e:
                    continue
            
            return pd.DataFrame(all_soccer_games)
            
        except Exception as e:
            return pd.DataFrame()
    
    def filter_games_by_status(self, games_df, status_filter="all"):
        """Filter games by their status"""
        if games_df.empty:
            return games_df
        
        if status_filter == "live":
            return games_df[games_df['status'].str.contains('In Progress|Live|Halftime|Overtime', case=False, na=False)]
        elif status_filter == "upcoming":
            return games_df[games_df['status'].str.contains('Scheduled|Pre-Game', case=False, na=False)]
        elif status_filter == "finished":
            return games_df[games_df['status'].str.contains('Final|Completed', case=False, na=False)]
        else:
            return games_df
    
    def get_game_details(self, game_id, sport="football", league="nfl"):
        """Get detailed information about a specific game"""
        try:
            url = f"{self.espn_base_url}/{sport}/{league}/summary"
            params = {'event': game_id}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    def format_venue_string(self, venue_info):
        """Format venue information into a readable string"""
        if not venue_info or not venue_info.get('name'):
            return "Venue TBD"
        
        venue_str = venue_info['name']
        if venue_info.get('city') and venue_info.get('state'):
            venue_str += f" ({venue_info['city']}, {venue_info['state']})"
        elif venue_info.get('city'):
            venue_str += f" ({venue_info['city']})"
        
        return venue_str
    
    def get_time_until_game(self, game_datetime):
        """Calculate time until game starts"""
        if not game_datetime:
            return "Time TBD"
        
        now = datetime.now(game_datetime.tzinfo)
        time_diff = game_datetime - now
        
        if time_diff.total_seconds() < 0:
            return "Started"
        
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"