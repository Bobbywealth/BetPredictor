from datetime import datetime, date, timedelta
import requests
import streamlit as st

class DateBasedSportsManager:
    """Enhanced sports data manager with comprehensive date-based fetching"""
    
    def __init__(self):
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports"
    
    def get_games_for_date_range(self, start_date, end_date, sports_list):
        """Get games for a specific date range across multiple sports"""
        all_games = []
        
        current_date = start_date
        while current_date <= end_date:
            for sport, league in sports_list:
                games = self.fetch_espn_games_for_date(sport, league, current_date)
                if games:
                    all_games.extend(games)
            current_date += timedelta(days=1)
        
        return all_games
    
    def fetch_espn_games_for_date(self, sport, league, target_date):
        """Fetch ESPN games for a specific date with multiple URL patterns"""
        games = []
        
        # Multiple URL patterns to try
        date_formats = [
            target_date.strftime('%Y%m%d'),  # 20250728
            target_date.strftime('%Y-%m-%d'), # 2025-07-28
            target_date.strftime('%m%d%Y'),   # 07282025
        ]
        
        url_patterns = [
            f"{self.espn_base_url}/{sport}/{league}/scoreboard",
            f"{self.espn_base_url}/{sport}/{league}/schedule",
            f"{self.espn_base_url}/{sport}/{league}/scoreboard?dates={{date}}",
            f"{self.espn_base_url}/{sport}/{league}/schedule?dates={{date}}"
        ]
        
        for url_pattern in url_patterns:
            for date_format in date_formats + [None]:
                try:
                    if date_format and '{date}' in url_pattern:
                        url = url_pattern.format(date=date_format)
                    elif date_format:
                        url = f"{url_pattern}?dates={date_format}"
                    else:
                        url = url_pattern
                    
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        events = data.get('events', [])
                        
                        for event in events:
                            game_date_str = event.get('date', '')
                            if game_date_str:
                                try:
                                    game_dt = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                                    game_date_obj = game_dt.date()
                                    
                                    # Check if game matches target date
                                    if game_date_obj == target_date:
                                        game_info = self.parse_espn_event(event, sport, league)
                                        if game_info:
                                            games.append(game_info)
                                except Exception:
                                    continue
                        
                        # If we found games, return them
                        if games:
                            return games
                            
                except Exception as e:
                    continue
        
        return games
    
    def parse_espn_event(self, event, sport, league):
        """Parse ESPN event data into standardized format"""
        try:
            game_date_str = event.get('date', '')
            game_name = event.get('name', 'Unknown Game')
            
            # Parse date and time
            display_date = ''
            display_time = 'TBD'
            
            if game_date_str:
                try:
                    game_dt = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                    display_date = game_dt.strftime('%Y-%m-%d')
                    display_time = game_dt.strftime('%I:%M %p ET')
                except:
                    display_date = game_date_str[:10] if len(game_date_str) >= 10 else game_date_str
            
            # Get team information
            competitors = event.get('competitions', [{}])[0].get('competitors', [])
            home_team = {'name': 'TBD', 'score': 0, 'abbreviation': '', 'logo': ''}
            away_team = {'name': 'TBD', 'score': 0, 'abbreviation': '', 'logo': ''}
            
            if len(competitors) >= 2:
                for competitor in competitors:
                    team_info = {
                        'name': competitor['team']['displayName'],
                        'abbreviation': competitor['team'].get('abbreviation', ''),
                        'logo': competitor['team'].get('logo', ''),
                        'score': int(competitor.get('score', 0))
                    }
                    
                    if competitor.get('homeAway') == 'home':
                        home_team = team_info
                    else:
                        away_team = team_info
            
            return {
                'game_id': f"espn_{event.get('id', '')}",
                'game_name': game_name,
                'short_name': event.get('shortName', ''),
                'date': display_date,
                'time': display_time,
                'status': event.get('status', {}).get('type', {}).get('name', 'Scheduled'),
                'home_team': home_team,
                'away_team': away_team,
                'sport': sport,
                'league': league.upper(),
                'source': 'ESPN'
            }
            
        except Exception as e:
            return None
    
    def get_monthly_games(self, year, month, sports_list):
        """Get all games for a specific month"""
        # Get first and last day of month
        first_day = date(year, month, 1)
        
        # Get last day of month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_games_for_date_range(first_day, last_day, sports_list)