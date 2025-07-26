import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_sample_data(sport='football'):
    """Generate sample sports data for demonstration"""
    
    # Define teams for different sports
    teams_data = {
        'football': [
            'Manchester United', 'Liverpool', 'Chelsea', 'Arsenal', 'Manchester City',
            'Tottenham', 'Newcastle', 'Brighton', 'Aston Villa', 'West Ham',
            'Crystal Palace', 'Fulham', 'Brentford', 'Wolves', 'Everton'
        ],
        'basketball': [
            'Lakers', 'Warriors', 'Celtics', 'Heat', 'Bulls',
            'Knicks', 'Nets', 'Clippers', 'Nuggets', 'Suns',
            'Mavericks', 'Rockets', 'Spurs', 'Jazz', 'Blazers'
        ],
        'baseball': [
            'Yankees', 'Red Sox', 'Dodgers', 'Giants', 'Cubs',
            'Cardinals', 'Astros', 'Braves', 'Phillies', 'Mets',
            'Padres', 'Angels', 'Athletics', 'Rangers', 'Mariners'
        ]
    }
    
    # Define typical score ranges for different sports
    score_ranges = {
        'football': (0, 6),      # Goals
        'basketball': (80, 130), # Points
        'baseball': (0, 15)      # Runs
    }
    
    teams = teams_data.get(sport, teams_data['football'])
    min_score, max_score = score_ranges.get(sport, score_ranges['football'])
    
    # Generate sample data
    data = []
    start_date = datetime.now() - timedelta(days=365 * 2)  # 2 years of data
    
    # Generate matches
    for i in range(500):  # 500 sample matches
        # Random date in the past 2 years
        random_days = random.randint(0, 730)
        match_date = start_date + timedelta(days=random_days)
        
        # Random teams
        team1, team2 = random.sample(teams, 2)
        
        # Generate scores with some realistic patterns
        if sport == 'football':
            # Football scores are typically lower
            team1_score = np.random.poisson(1.5)  # Average 1.5 goals
            team2_score = np.random.poisson(1.3)  # Slightly lower for away team
        elif sport == 'basketball':
            # Basketball scores are higher and more varied
            team1_score = random.randint(min_score, max_score)
            team2_score = random.randint(min_score, max_score)
            # Add some home advantage
            team1_score += random.randint(0, 8)
        else:  # baseball
            # Baseball scores
            team1_score = np.random.poisson(4.5)  # Average 4.5 runs
            team2_score = np.random.poisson(4.2)  # Slightly lower for away team
        
        # Ensure scores are within reasonable range
        team1_score = max(0, min(team1_score, max_score))
        team2_score = max(0, min(team2_score, max_score))
        
        data.append({
            'date': match_date.strftime('%Y-%m-%d'),
            'team1': team1,
            'team2': team2,
            'team1_score': int(team1_score),
            'team2_score': int(team2_score),
            'sport': sport
        })
    
    # Add some additional features for demonstration
    for match in data:
        # Add some realistic patterns
        if random.random() < 0.15:  # 15% chance of draw in football
            if sport == 'football':
                match['team2_score'] = match['team1_score']
        
        # Weekend vs weekday effect
        match_datetime = datetime.strptime(match['date'], '%Y-%m-%d')
        if match_datetime.weekday() >= 5:  # Weekend
            # Slightly higher scores on weekends
            if random.random() < 0.3:
                match['team1_score'] += 1
                match['team2_score'] += 1
    
    return pd.DataFrame(data)

def get_team_names(sport='football'):
    """Get list of team names for a specific sport"""
    teams_data = {
        'football': [
            'Manchester United', 'Liverpool', 'Chelsea', 'Arsenal', 'Manchester City',
            'Tottenham', 'Newcastle', 'Brighton', 'Aston Villa', 'West Ham',
            'Crystal Palace', 'Fulham', 'Brentford', 'Wolves', 'Everton'
        ],
        'basketball': [
            'Lakers', 'Warriors', 'Celtics', 'Heat', 'Bulls',
            'Knicks', 'Nets', 'Clippers', 'Nuggets', 'Suns',
            'Mavericks', 'Rockets', 'Spurs', 'Jazz', 'Blazers'
        ],
        'baseball': [
            'Yankees', 'Red Sox', 'Dodgers', 'Giants', 'Cubs',
            'Cardinals', 'Astros', 'Braves', 'Phillies', 'Mets',
            'Padres', 'Angels', 'Athletics', 'Rangers', 'Mariners'
        ]
    }
    
    return teams_data.get(sport, teams_data['football'])

def validate_data_format(data):
    """Validate that uploaded data has the correct format"""
    required_columns = ['team1', 'team2', 'team1_score', 'team2_score', 'date', 'sport']
    
    if not isinstance(data, pd.DataFrame):
        return False, "Data must be a pandas DataFrame"
    
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    # Check data types
    try:
        pd.to_datetime(data['date'])
        pd.to_numeric(data['team1_score'])
        pd.to_numeric(data['team2_score'])
    except:
        return False, "Invalid data types. Ensure date is in YYYY-MM-DD format and scores are numeric"
    
    return True, "Data format is valid"

def get_sample_csv_template():
    """Generate a sample CSV template for users to download"""
    template_data = {
        'date': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'team1': ['Team A', 'Team B', 'Team C'],
        'team2': ['Team B', 'Team C', 'Team A'],
        'team1_score': [2, 1, 3],
        'team2_score': [1, 0, 2],
        'sport': ['football', 'football', 'football']
    }
    
    return pd.DataFrame(template_data)
