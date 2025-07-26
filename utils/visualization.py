import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class Visualizer:
    def __init__(self):
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#FF9FF3', '#FF7F7F', '#87CEEB', '#98D8C8'
        ]
    
    def create_team_performance_chart(self, data, team):
        """Create a performance chart for a specific team"""
        # Get team games
        team_games = data[
            (data['team1'] == team) | (data['team2'] == team)
        ].copy()
        
        if len(team_games) == 0:
            # Return empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for this team",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            fig.update_layout(title=f"{team} Performance")
            return fig
        
        # Calculate team scores and opponent scores
        team_scores = []
        opponent_scores = []
        results = []
        dates = []
        
        for _, game in team_games.iterrows():
            if game['team1'] == team:
                team_score = game['team1_score']
                opp_score = game['team2_score']
            else:
                team_score = game['team2_score']
                opp_score = game['team1_score']
            
            team_scores.append(team_score)
            opponent_scores.append(opp_score)
            dates.append(game['date'])
            
            if team_score > opp_score:
                results.append('Win')
            elif team_score < opp_score:
                results.append('Loss')
            else:
                results.append('Draw')
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=[f'{team} - Goals Scored vs Conceded', 'Match Results Over Time'],
            vertical_spacing=0.1
        )
        
        # Goals scored vs conceded
        fig.add_trace(
            go.Scatter(
                x=dates, y=team_scores,
                mode='lines+markers',
                name='Goals Scored',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates, y=opponent_scores,
                mode='lines+markers',
                name='Goals Conceded',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
        
        # Results over time
        result_colors = {'Win': '#4ECDC4', 'Loss': '#FF6B6B', 'Draw': '#FFEAA7'}
        for result_type in ['Win', 'Loss', 'Draw']:
            result_dates = [dates[i] for i, r in enumerate(results) if r == result_type]
            result_values = [1 if result_type == 'Win' else (-1 if result_type == 'Loss' else 0) 
                           for _ in result_dates]
            
            if result_dates:
                fig.add_trace(
                    go.Scatter(
                        x=result_dates, y=result_values,
                        mode='markers',
                        name=result_type,
                        marker=dict(
                            color=result_colors[result_type],
                            size=10,
                            symbol='circle'
                        )
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            title=f"{team} Performance Analysis",
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Goals", row=1, col=1)
        fig.update_yaxes(title_text="Result", row=2, col=1, tickvals=[-1, 0, 1], 
                        ticktext=['Loss', 'Draw', 'Win'])
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        return fig
    
    def create_prediction_chart(self, prediction_result):
        """Create a visualization for prediction results"""
        teams = ['Team 1', 'Team 2']
        if 'draw_prob' in prediction_result:
            teams.append('Draw')
        
        probabilities = [
            prediction_result['team1_win_prob'],
            prediction_result['team2_win_prob']
        ]
        
        if 'draw_prob' in prediction_result:
            probabilities.append(prediction_result['draw_prob'])
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=teams,
                y=probabilities,
                marker_color=self.color_palette[:len(teams)],
                text=[f'{p:.1%}' for p in probabilities],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Match Prediction Probabilities',
            xaxis_title='Outcome',
            yaxis_title='Probability',
            yaxis_tickformat='.0%',
            height=400
        )
        
        return fig
    
    def create_feature_importance_chart(self, feature_importance):
        """Create feature importance visualization"""
        if not feature_importance:
            fig = go.Figure()
            fig.add_annotation(
                text="No feature importance data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        features = list(feature_importance.keys())
        importance = list(feature_importance.values())
        
        # Sort by importance
        sorted_data = sorted(zip(features, importance), key=lambda x: x[1], reverse=True)
        features, importance = zip(*sorted_data)
        
        fig = go.Figure(data=[
            go.Bar(
                y=features,
                x=importance,
                orientation='h',
                marker_color='#4ECDC4'
            )
        ])
        
        fig.update_layout(
            title='Feature Importance in Model',
            xaxis_title='Importance',
            yaxis_title='Features',
            height=max(400, len(features) * 30)
        )
        
        return fig
    
    def create_confusion_matrix(self, confusion_matrix):
        """Create confusion matrix heatmap"""
        labels = ['Team 2 Win', 'Team 1 Win', 'Draw']
        
        # Ensure we have the right number of labels
        if len(confusion_matrix) == 2:
            labels = ['Team 2 Win', 'Team 1 Win']
        
        fig = go.Figure(data=go.Heatmap(
            z=confusion_matrix,
            x=labels,
            y=labels,
            colorscale='Blues',
            text=confusion_matrix,
            texttemplate="%{text}",
            textfont={"size": 16}
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title='Predicted',
            yaxis_title='Actual',
            height=400
        )
        
        return fig
    
    def create_monthly_trends(self, data):
        """Create monthly trends visualization"""
        monthly_data = data.groupby(['year', 'month']).agg({
            'total_score': 'mean',
            'score_difference': 'mean'
        }).reset_index()
        
        monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Average Total Score per Game', 'Average Score Difference'],
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_data['date'],
                y=monthly_data['total_score'],
                mode='lines+markers',
                name='Avg Total Score',
                line=dict(color='#4ECDC4', width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_data['date'],
                y=monthly_data['score_difference'],
                mode='lines+markers',
                name='Avg Score Difference',
                line=dict(color='#FF6B6B', width=3)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='Monthly Performance Trends',
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Score", row=1, col=1)
        fig.update_yaxes(title_text="Difference", row=2, col=1)
        
        return fig
    
    def create_team_comparison_chart(self, comparison_df):
        """Create team comparison visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Win Rate Comparison',
                'Average Points Scored',
                'Average Points Conceded',
                'Total Games Played'
            ],
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Win Rate
        fig.add_trace(
            go.Bar(
                x=comparison_df['Team'],
                y=comparison_df['Win Rate'],
                name='Win Rate',
                marker_color='#4ECDC4'
            ),
            row=1, col=1
        )
        
        # Avg Points Scored
        fig.add_trace(
            go.Bar(
                x=comparison_df['Team'],
                y=comparison_df['Avg Points Scored'],
                name='Avg Scored',
                marker_color='#45B7D1'
            ),
            row=1, col=2
        )
        
        # Avg Points Conceded
        fig.add_trace(
            go.Bar(
                x=comparison_df['Team'],
                y=comparison_df['Avg Points Conceded'],
                name='Avg Conceded',
                marker_color='#FF6B6B'
            ),
            row=2, col=1
        )
        
        # Total Games
        fig.add_trace(
            go.Bar(
                x=comparison_df['Team'],
                y=comparison_df['Total Games'],
                name='Total Games',
                marker_color='#96CEB4'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Team Performance Comparison',
            height=600,
            showlegend=False
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Win Rate", row=1, col=1, tickformat='.0%')
        fig.update_yaxes(title_text="Points", row=1, col=2)
        fig.update_yaxes(title_text="Points", row=2, col=1)
        fig.update_yaxes(title_text="Games", row=2, col=2)
        
        return fig
    
    def create_seasonal_chart(self, seasonal_df):
        """Create seasonal analysis chart"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Games per Season',
                'Average Total Score',
                'Average Score Difference',
                'Draw Rate'
            ]
        )
        
        # Games per season
        fig.add_trace(
            go.Bar(
                x=seasonal_df['year'],
                y=seasonal_df['total_games'],
                marker_color='#4ECDC4',
                name='Total Games'
            ),
            row=1, col=1
        )
        
        # Average total score
        fig.add_trace(
            go.Scatter(
                x=seasonal_df['year'],
                y=seasonal_df['avg_total_score'],
                mode='lines+markers',
                marker_color='#45B7D1',
                name='Avg Total Score'
            ),
            row=1, col=2
        )
        
        # Average score difference
        fig.add_trace(
            go.Scatter(
                x=seasonal_df['year'],
                y=seasonal_df['avg_score_difference'],
                mode='lines+markers',
                marker_color='#FF6B6B',
                name='Avg Score Diff'
            ),
            row=2, col=1
        )
        
        # Draw rate
        fig.add_trace(
            go.Bar(
                x=seasonal_df['year'],
                y=seasonal_df['draw_rate'],
                marker_color='#FFEAA7',
                name='Draw Rate'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Seasonal Analysis',
            height=600,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Games", row=1, col=1)
        fig.update_yaxes(title_text="Score", row=1, col=2)
        fig.update_yaxes(title_text="Difference", row=2, col=1)
        fig.update_yaxes(title_text="Rate", row=2, col=2, tickformat='.0%')
        
        return fig
