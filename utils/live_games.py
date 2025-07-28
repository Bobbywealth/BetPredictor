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
            
            return games
            
        except Exception as e:
            # Don't show errors to users - handle gracefully
            if st.session_state.get('debug_mode', False):
                st.error(f"Error fetching ESPN schedule: {str(e)}")
            return []
    
    def get_upcoming_games_all_sports(self, target_date=None, sport_filter=None):
        """Get comprehensive games across all major sports categories with date filtering"""
        all_games = []
        
        # Use target date or default to today
        if target_date:
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            elif hasattr(target_date, 'date'):
                target_date = target_date.date()
        else:
            target_date = datetime.now().date()
        
        # Get dates around target date for API calls
        target_datetime = datetime.combine(target_date, datetime.min.time())
        yesterday = target_datetime - timedelta(days=1)
        tomorrow = target_datetime + timedelta(days=1)
        
        dates_to_check = [
            yesterday.strftime('%Y%m%d'),
            target_datetime.strftime('%Y%m%d'),
            tomorrow.strftime('%Y%m%d')
        ]
        
        # ESPN Sports - Focus on working endpoints
        espn_sports = [
            # Basketball (Working)
            ('basketball', 'nba'),
            ('basketball', 'wnba'),
            
            # Baseball (Working)
            ('baseball', 'mlb'),
            
            # Football (Working)
            ('football', 'nfl'),
            
            # Hockey (Working)
            ('hockey', 'nhl')
        ]
        
        # Apply sport filter if specified
        if sport_filter:
            espn_sports = [(s, l) for s, l in espn_sports if s == sport_filter]
        
        # Fetch from ESPN with date filtering
        for sport, league in espn_sports:
            try:
                # Try target date first, then fallback to current
                games_found = False
                for date_str in [target_datetime.strftime('%Y%m%d'), None]:
                    try:
                        games = self.get_espn_live_schedule(sport, league, date_str)
                        if games and len(games) > 0:
                            # Filter games by target date
                            filtered_games = self.filter_games_by_date(games, target_date)
                            if filtered_games:
                                all_games.extend(filtered_games)
                                games_found = True
                                break
                    except Exception:
                        continue
                
                if not games_found and st.session_state.get('debug_mode', False):
                    st.write(f"⚠️ No {sport}/{league} games found for {target_date}")
                    
            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.write(f"⚠️ {sport}/{league}: {str(e)[:50]}...")
                continue
        
        # TheSportsDB for comprehensive soccer coverage (only if no sport filter or soccer filter)
        if not sport_filter or sport_filter == 'soccer':
            try:
                soccer_games_df = self.get_sportsdb_soccer_games()
                if isinstance(soccer_games_df, pd.DataFrame) and not soccer_games_df.empty:
                    # Convert DataFrame to list of dicts for consistency
                    soccer_games = soccer_games_df.to_dict('records')
                    # Filter soccer games by target date
                    filtered_soccer = self.filter_games_by_date(soccer_games, target_date)
                    if filtered_soccer:
                        all_games.extend(filtered_soccer)
            except Exception as e:
                pass
        
        # Additional soccer leagues from TheSportsDB (only if no sport filter or soccer filter)
        if not sport_filter or sport_filter == 'soccer':
            additional_soccer_leagues = [
                '4328',  # Premier League
                '4335',  # La Liga
                '4331',  # Bundesliga
                '4332',  # Serie A
                '4334',  # Ligue 1
                '4346',  # UEFA Champions League
                '4480',  # UEFA Europa League
                '4481'   # UEFA Conference League
            ]
            
            for league_id in additional_soccer_leagues:
                try:
                    league_games = self.get_sportsdb_league_specific(league_id)
                    if league_games:
                        # Filter by target date
                        filtered_league_games = self.filter_games_by_date(league_games, target_date)
                        if filtered_league_games:
                            all_games.extend(filtered_league_games)
                except Exception as e:
                    continue
        
        # Convert to DataFrame and remove duplicates
        if all_games:
            df = pd.DataFrame(all_games)
            
            # Remove duplicates based on game_id if available
            if 'game_id' in df.columns:
                df = df.drop_duplicates(subset=['game_id'], keep='first')
            else:
                # Fallback: remove duplicates based on game name and date
                df = df.drop_duplicates(subset=['game_name', 'date'], keep='first')
            
            return df
        else:
            return pd.DataFrame()
    
    def get_sportsdb_league_specific(self, league_id):
        """Get games from a specific TheSportsDB league"""
        try:
            # Get recent and upcoming games for specific league
            games_list = []
            
            # Try both past and upcoming events
            urls = [
                f"{self.sportsdb_base_url}/eventspastleague.php?id={league_id}",
                f"{self.sportsdb_base_url}/eventsnextleague.php?id={league_id}"
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('events'):
                            # Take recent/upcoming games (limit to 3 per endpoint)
                            for event in data['events'][:3]:
                                games_list.append({
                                    'game_id': f"sdb_league_{event.get('idEvent', '')}",
                                    'game_name': f"{event.get('strHomeTeam', '')} vs {event.get('strAwayTeam', '')}",
                                    'short_name': f"{event.get('strHomeTeam', '')[:3]} vs {event.get('strAwayTeam', '')[:3]}",
                                    'date': event.get('dateEvent', ''),
                                    'time': event.get('strTime', 'TBD'),
                                    'status': 'Final' if event.get('intHomeScore') else 'Scheduled',
                                    'home_team': {
                                        'name': event.get('strHomeTeam', ''),
                                        'score': event.get('intHomeScore', 0) or 0,
                                        'logo': event.get('strHomeTeamBadge', ''),
                                        'abbreviation': event.get('strHomeTeam', '')[:3] if event.get('strHomeTeam') else ''
                                    },
                                    'away_team': {
                                        'name': event.get('strAwayTeam', ''),
                                        'score': event.get('intAwayScore', 0) or 0,
                                        'logo': event.get('strAwayTeamBadge', ''),
                                        'abbreviation': event.get('strAwayTeam', '')[:3] if event.get('strAwayTeam') else ''
                                    },
                                    'league': event.get('strLeague', 'Soccer'),
                                    'sport': 'soccer',
                                    'source': 'TheSportsDB'
                                })
                except Exception as e:
                    continue
            
            return games_list
            
        except Exception as e:
            return []
    
    def filter_games_by_date(self, games, target_date):
        """Filter games to only include those on or around the target date"""
        if not games or not target_date:
            return games
            
        filtered_games = []
        target_str = target_date.strftime('%Y-%m-%d')
        
        # Allow games within 2 days of target date to account for timezone differences
        target_datetime = datetime.combine(target_date, datetime.min.time())
        min_date = target_datetime - timedelta(days=2)
        max_date = target_datetime + timedelta(days=2)
        
        for game in games:
            game_date_str = game.get('date', '')
            if game_date_str:
                try:
                    # Parse various date formats
                    if len(game_date_str) == 10:  # YYYY-MM-DD
                        game_date = datetime.strptime(game_date_str, '%Y-%m-%d')
                    elif len(game_date_str) == 19:  # YYYY-MM-DDTHH:MM:SS
                        game_date = datetime.strptime(game_date_str[:10], '%Y-%m-%d')
                    else:
                        continue
                    
                    # Include games within date range
                    if min_date <= game_date <= max_date:
                        filtered_games.append(game)
                        
                except (ValueError, TypeError):
                    # If date parsing fails, include game to be safe
                    continue
            else:
                # If no date, include recent games (they might be live)
                filtered_games.append(game)
        
        return filtered_games
    
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
                                
                                # Format time better - convert 24hr to 12hr if possible
                                formatted_time = event.get('strTime', 'TBD')
                                if formatted_time and formatted_time != 'TBD':
                                    try:
                                        # Try to parse and format time
                                        from datetime import datetime
                                        time_obj = datetime.strptime(formatted_time, '%H:%M:%S')
                                        formatted_time = time_obj.strftime('%I:%M %p')
                                    except:
                                        # Keep original if parsing fails
                                        pass
                                
                                all_soccer_games.append({
                                    'game_id': f"sdb_{event.get('idEvent', '')}",
                                    'game_name': f"{event.get('strHomeTeam', '')} vs {event.get('strAwayTeam', '')}",
                                    'short_name': f"{event.get('strHomeTeam', '')[:3]} vs {event.get('strAwayTeam', '')[:3]}",
                                    'date': event_date,
                                    'time': formatted_time,
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