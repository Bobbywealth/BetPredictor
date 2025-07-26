import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self):
        pass
    
    def process_data(self, data, date_range=None, selected_sports=None):
        """Process and clean the uploaded data"""
        try:
            # Make a copy to avoid modifying original data
            processed_data = data.copy()
            
            # Convert date column to datetime
            processed_data['date'] = pd.to_datetime(processed_data['date'], errors='coerce')
            
            # Remove rows with invalid dates
            processed_data = processed_data.dropna(subset=['date'])
            
            # Filter by date range if provided
            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                processed_data = processed_data[
                    (processed_data['date'] >= pd.to_datetime(start_date)) &
                    (processed_data['date'] <= pd.to_datetime(end_date))
                ]
            
            # Filter by selected sports
            if selected_sports:
                processed_data = processed_data[processed_data['sport'].isin(selected_sports)]
            
            # Ensure numeric scores
            processed_data['team1_score'] = pd.to_numeric(processed_data['team1_score'], errors='coerce')
            processed_data['team2_score'] = pd.to_numeric(processed_data['team2_score'], errors='coerce')
            
            # Remove rows with invalid scores
            processed_data = processed_data.dropna(subset=['team1_score', 'team2_score'])
            
            # Clean team names (strip whitespace, standardize case)
            processed_data['team1'] = processed_data['team1'].str.strip().str.title()
            processed_data['team2'] = processed_data['team2'].str.strip().str.title()
            
            # Add derived columns
            processed_data['winner'] = processed_data.apply(self._determine_winner, axis=1)
            processed_data['total_score'] = processed_data['team1_score'] + processed_data['team2_score']
            processed_data['score_difference'] = abs(processed_data['team1_score'] - processed_data['team2_score'])
            processed_data['month'] = processed_data['date'].dt.month
            processed_data['year'] = processed_data['date'].dt.year
            processed_data['day_of_week'] = processed_data['date'].dt.day_name()
            
            # Sort by date
            processed_data = processed_data.sort_values('date')
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            return data  # Return original data if processing fails
    
    def _determine_winner(self, row):
        """Determine the winner of a match"""
        if row['team1_score'] > row['team2_score']:
            return row['team1']
        elif row['team1_score'] < row['team2_score']:
            return row['team2']
        else:
            return 'Draw'
    
    def get_team_stats(self, data, team):
        """Get comprehensive statistics for a team"""
        # Games where team is team1 (home)
        home_games = data[data['team1'] == team].copy()
        home_games['team_score'] = home_games['team1_score']
        home_games['opponent_score'] = home_games['team2_score']
        home_games['opponent'] = home_games['team2']
        
        # Games where team is team2 (away)
        away_games = data[data['team2'] == team].copy()
        away_games['team_score'] = away_games['team2_score']
        away_games['opponent_score'] = away_games['team1_score']
        away_games['opponent'] = away_games['team1']
        
        # Combine all games
        all_games = pd.concat([home_games, away_games], ignore_index=True)
        
        if len(all_games) == 0:
            return {
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'win_rate': 0,
                'avg_points_scored': 0,
                'avg_points_conceded': 0,
                'home_games': 0,
                'away_games': 0,
                'home_win_rate': 0,
                'away_win_rate': 0
            }
        
        # Calculate basic stats
        wins = len(all_games[all_games['team_score'] > all_games['opponent_score']])
        losses = len(all_games[all_games['team_score'] < all_games['opponent_score']])
        draws = len(all_games[all_games['team_score'] == all_games['opponent_score']])
        
        # Home vs Away performance
        home_wins = len(home_games[home_games['team_score'] > home_games['opponent_score']])
        away_wins = len(away_games[away_games['team_score'] > away_games['opponent_score']])
        
        return {
            'total_games': len(all_games),
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': wins / len(all_games) if len(all_games) > 0 else 0,
            'avg_points_scored': all_games['team_score'].mean(),
            'avg_points_conceded': all_games['opponent_score'].mean(),
            'home_games': len(home_games),
            'away_games': len(away_games),
            'home_win_rate': home_wins / len(home_games) if len(home_games) > 0 else 0,
            'away_win_rate': away_wins / len(away_games) if len(away_games) > 0 else 0
        }
    
    def get_head_to_head(self, data, team1, team2):
        """Get head-to-head match history between two teams"""
        h2h_matches = data[
            ((data['team1'] == team1) & (data['team2'] == team2)) |
            ((data['team1'] == team2) & (data['team2'] == team1))
        ].copy()
        
        if len(h2h_matches) == 0:
            return pd.DataFrame()
        
        # Add winner column for easier analysis
        h2h_matches['winner'] = h2h_matches.apply(
            lambda row: team1 if (
                (row['team1'] == team1 and row['team1_score'] > row['team2_score']) or
                (row['team2'] == team1 and row['team2_score'] > row['team1_score'])
            ) else (
                team2 if (
                    (row['team1'] == team2 and row['team1_score'] > row['team2_score']) or
                    (row['team2'] == team2 and row['team2_score'] > row['team1_score'])
                ) else 'Draw'
            ), axis=1
        )
        
        return h2h_matches.sort_values('date', ascending=False)
    
    def get_seasonal_analysis(self, data):
        """Analyze performance by season/year"""
        if len(data) == 0:
            return None
        
        seasonal_data = []
        
        for year in sorted(data['year'].unique()):
            year_data = data[data['year'] == year]
            
            if len(year_data) == 0:
                continue
            
            total_games = len(year_data)
            avg_total_score = year_data['total_score'].mean()
            avg_score_difference = year_data['score_difference'].mean()
            
            # Count draws
            draws = len(year_data[year_data['team1_score'] == year_data['team2_score']])
            draw_rate = draws / total_games if total_games > 0 else 0
            
            seasonal_data.append({
                'year': year,
                'total_games': total_games,
                'avg_total_score': avg_total_score,
                'avg_score_difference': avg_score_difference,
                'draw_rate': draw_rate,
                'draws': draws
            })
        
        return pd.DataFrame(seasonal_data) if seasonal_data else None
    
    def get_monthly_trends(self, data):
        """Get monthly performance trends"""
        if len(data) == 0:
            return None
        
        monthly_data = data.groupby(['year', 'month']).agg({
            'total_score': 'mean',
            'score_difference': 'mean',
            'team1_score': 'mean',
            'team2_score': 'mean'
        }).reset_index()
        
        monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))
        
        return monthly_data.sort_values('date')
    
    def get_team_form(self, data, team, num_games=5):
        """Get recent form for a team (last N games)"""
        team_games = data[
            (data['team1'] == team) | (data['team2'] == team)
        ].sort_values('date', ascending=False).head(num_games)
        
        if len(team_games) == 0:
            return {
                'games_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'form_string': '',
                'avg_goals_scored': 0,
                'avg_goals_conceded': 0
            }
        
        wins = 0
        draws = 0
        losses = 0
        goals_scored = []
        goals_conceded = []
        form_string = ""
        
        for _, game in team_games.iterrows():
            if game['team1'] == team:
                team_score = game['team1_score']
                opp_score = game['team2_score']
            else:
                team_score = game['team2_score']
                opp_score = game['team1_score']
            
            goals_scored.append(team_score)
            goals_conceded.append(opp_score)
            
            if team_score > opp_score:
                wins += 1
                form_string += "W"
            elif team_score < opp_score:
                losses += 1
                form_string += "L"
            else:
                draws += 1
                form_string += "D"
        
        return {
            'games_played': len(team_games),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'form_string': form_string,
            'avg_goals_scored': np.mean(goals_scored) if goals_scored else 0,
            'avg_goals_conceded': np.mean(goals_conceded) if goals_conceded else 0
        }
