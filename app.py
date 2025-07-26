import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Import custom modules
from models.predictor import SportsPredictor
from utils.data_processor import DataProcessor
from utils.visualization import Visualizer
from data.sample_data import get_sample_data

# Page configuration
st.set_page_config(
    page_title="Sports Betting Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'predictor' not in st.session_state:
    st.session_state.predictor = SportsPredictor()
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = Visualizer()

def main():
    st.title("🏆 Sports Betting Prediction App")
    
    # Gambling disclaimer
    st.warning(
        "⚠️ **IMPORTANT DISCLAIMER**: This application is for educational and entertainment purposes only. "
        "Sports betting involves significant financial risk. Never bet more than you can afford to lose. "
        "Predictions are not guaranteed and past performance does not indicate future results. "
        "Please gamble responsibly and seek help if you have a gambling problem."
    )
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "Data Upload & Processing",
        "Team Analysis",
        "Make Predictions",
        "Model Performance",
        "Historical Analysis"
    ])
    
    if page == "Data Upload & Processing":
        data_upload_page()
    elif page == "Team Analysis":
        team_analysis_page()
    elif page == "Make Predictions":
        prediction_page()
    elif page == "Model Performance":
        model_performance_page()
    elif page == "Historical Analysis":
        historical_analysis_page()

def data_upload_page():
    st.header("📊 Data Upload & Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Your Data")
        uploaded_file = st.file_uploader(
            "Upload CSV file with historical sports data",
            type=['csv'],
            help="File should contain columns: team1, team2, team1_score, team2_score, date, sport"
        )
        
        if uploaded_file is not None:
            try:
                data = pd.read_csv(uploaded_file)
                st.success(f"Successfully uploaded {len(data)} records!")
                st.session_state.uploaded_data = data
                
                # Display data preview
                st.subheader("Data Preview")
                st.dataframe(data.head())
                
                # Data validation
                required_columns = ['team1', 'team2', 'team1_score', 'team2_score', 'date', 'sport']
                missing_columns = [col for col in required_columns if col not in data.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {missing_columns}")
                else:
                    st.success("All required columns present!")
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with col2:
        st.subheader("Use Sample Data")
        sport_type = st.selectbox("Select sport for sample data", ["football", "basketball", "baseball"])
        
        if st.button("Load Sample Data"):
            sample_data = get_sample_data(sport_type)
            st.session_state.uploaded_data = sample_data
            st.success(f"Loaded sample {sport_type} data with {len(sample_data)} records!")
            st.dataframe(sample_data.head())
    
    # Data processing options
    if 'uploaded_data' in st.session_state:
        st.subheader("Data Processing Options")
        
        col3, col4 = st.columns(2)
        with col3:
            date_range = st.date_input(
                "Select date range for analysis",
                value=[datetime.now() - timedelta(days=365), datetime.now()],
                help="Choose the date range for your analysis"
            )
        
        with col4:
            selected_sports = st.multiselect(
                "Select sports to include",
                options=st.session_state.uploaded_data['sport'].unique(),
                default=st.session_state.uploaded_data['sport'].unique()
            )
        
        if st.button("Process Data"):
            processed_data = st.session_state.data_processor.process_data(
                st.session_state.uploaded_data,
                date_range,
                selected_sports
            )
            st.session_state.processed_data = processed_data
            st.success("Data processed successfully!")
            
            # Train the model with processed data
            if len(processed_data) > 10:
                st.session_state.predictor.train_model(processed_data)
                st.success("Model trained with processed data!")

def team_analysis_page():
    st.header("🏈 Team Analysis")
    
    if 'processed_data' not in st.session_state:
        st.warning("Please upload and process data first!")
        return
    
    data = st.session_state.processed_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Team selection
        teams = list(set(data['team1'].tolist() + data['team2'].tolist()))
        selected_team = st.selectbox("Select team to analyze", teams)
        
        if selected_team:
            team_stats = st.session_state.data_processor.get_team_stats(data, selected_team)
            
            st.subheader(f"📈 {selected_team} Statistics")
            
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("Total Games", team_stats['total_games'])
                st.metric("Win Rate", f"{team_stats['win_rate']:.2%}")
            
            with metrics_col2:
                st.metric("Avg Points Scored", f"{team_stats['avg_points_scored']:.1f}")
                st.metric("Avg Points Conceded", f"{team_stats['avg_points_conceded']:.1f}")
            
            with metrics_col3:
                st.metric("Home Win Rate", f"{team_stats['home_win_rate']:.2%}")
                st.metric("Away Win Rate", f"{team_stats['away_win_rate']:.2%}")
    
    with col2:
        if selected_team:
            # Performance visualization
            fig = st.session_state.visualizer.create_team_performance_chart(data, selected_team)
            st.plotly_chart(fig, use_container_width=True)
    
    # Head-to-head comparison
    st.subheader("⚔️ Head-to-Head Comparison")
    col3, col4 = st.columns(2)
    
    with col3:
        team1 = st.selectbox("Select Team 1", teams, key="team1_select")
    with col4:
        team2 = st.selectbox("Select Team 2", [t for t in teams if t != team1], key="team2_select")
    
    if team1 and team2:
        h2h_data = st.session_state.data_processor.get_head_to_head(data, team1, team2)
        
        if len(h2h_data) > 0:
            st.write(f"**Historical matchups: {len(h2h_data)} games**")
            
            col5, col6, col7 = st.columns(3)
            with col5:
                team1_wins = len(h2h_data[h2h_data['winner'] == team1])
                st.metric(f"{team1} Wins", team1_wins)
            with col6:
                team2_wins = len(h2h_data[h2h_data['winner'] == team2])
                st.metric(f"{team2} Wins", team2_wins)
            with col7:
                draws = len(h2h_data[h2h_data['winner'] == 'Draw'])
                st.metric("Draws", draws)
            
            # Display recent matchups
            st.subheader("Recent Matchups")
            st.dataframe(h2h_data.tail(5))
        else:
            st.info("No historical matchups found between these teams.")

def prediction_page():
    st.header("🔮 Make Predictions")
    
    if 'processed_data' not in st.session_state:
        st.warning("Please upload and process data first!")
        return
    
    if not hasattr(st.session_state.predictor, 'model') or st.session_state.predictor.model is None:
        st.warning("Model not trained yet. Please process data first!")
        return
    
    data = st.session_state.processed_data
    teams = list(set(data['team1'].tolist() + data['team2'].tolist()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Match Details")
        team1 = st.selectbox("Home Team", teams, key="pred_team1")
        team2 = st.selectbox("Away Team", [t for t in teams if t != team1], key="pred_team2")
        sport = st.selectbox("Sport", data['sport'].unique())
        match_date = st.date_input("Match Date", datetime.now())
        
    with col2:
        st.subheader("Additional Factors")
        weather = st.selectbox("Weather Conditions", ["Clear", "Rain", "Snow", "Wind"])
        home_advantage = st.slider("Home Advantage Factor", 0.0, 2.0, 1.0, 0.1)
        recent_form_weight = st.slider("Recent Form Weight", 0.0, 1.0, 0.5, 0.1)
    
    if st.button("Generate Prediction", type="primary"):
        if team1 and team2 and team1 != team2:
            # Generate prediction
            prediction_result = st.session_state.predictor.predict_match(
                team1, team2, sport, data, 
                home_advantage=home_advantage,
                recent_form_weight=recent_form_weight
            )
            
            st.subheader("🎯 Prediction Results")
            
            # Main prediction
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric(
                    "Predicted Winner",
                    prediction_result['predicted_winner'],
                    delta=f"Confidence: {prediction_result['confidence']:.1%}"
                )
            
            with col4:
                st.metric(
                    f"{team1} Win Probability",
                    f"{prediction_result['team1_win_prob']:.1%}"
                )
            
            with col5:
                st.metric(
                    f"{team2} Win Probability",
                    f"{prediction_result['team2_win_prob']:.1%}"
                )
            
            # Betting recommendations
            st.subheader("💰 Betting Recommendations")
            
            recommendations = st.session_state.predictor.get_betting_recommendations(prediction_result)
            
            for i, rec in enumerate(recommendations):
                with st.container():
                    st.write(f"**Recommendation {i+1}:**")
                    col6, col7, col8 = st.columns(3)
                    
                    with col6:
                        st.write(f"**Bet Type:** {rec['bet_type']}")
                        st.write(f"**Selection:** {rec['selection']}")
                    
                    with col7:
                        st.write(f"**Confidence:** {rec['confidence']:.1%}")
                        st.write(f"**Risk Level:** {rec['risk_level']}")
                    
                    with col8:
                        st.write(f"**Expected Value:** {rec['expected_value']:.2f}")
                        st.write(f"**Suggested Stake:** {rec['suggested_stake']}")
                    
                    st.write(f"**Reasoning:** {rec['reasoning']}")
                    st.divider()
            
            # Visualization
            fig = st.session_state.visualizer.create_prediction_chart(prediction_result)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Please select two different teams!")

def model_performance_page():
    st.header("📊 Model Performance")
    
    if not hasattr(st.session_state.predictor, 'model') or st.session_state.predictor.model is None:
        st.warning("Model not trained yet. Please process data first!")
        return
    
    # Get model performance metrics
    performance_metrics = st.session_state.predictor.get_model_performance()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accuracy", f"{performance_metrics['accuracy']:.3f}")
    with col2:
        st.metric("Precision", f"{performance_metrics['precision']:.3f}")
    with col3:
        st.metric("Recall", f"{performance_metrics['recall']:.3f}")
    with col4:
        st.metric("F1 Score", f"{performance_metrics['f1_score']:.3f}")
    
    # Feature importance
    if 'feature_importance' in performance_metrics:
        st.subheader("📈 Feature Importance")
        fig = st.session_state.visualizer.create_feature_importance_chart(
            performance_metrics['feature_importance']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Confusion matrix
    if 'confusion_matrix' in performance_metrics:
        st.subheader("🎯 Confusion Matrix")
        fig = st.session_state.visualizer.create_confusion_matrix(
            performance_metrics['confusion_matrix']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Model details
    st.subheader("🔧 Model Details")
    model_info = st.session_state.predictor.get_model_info()
    
    col5, col6 = st.columns(2)
    with col5:
        st.write(f"**Model Type:** {model_info['model_type']}")
        st.write(f"**Training Samples:** {model_info['training_samples']}")
        st.write(f"**Features Used:** {model_info['n_features']}")
    
    with col6:
        st.write(f"**Last Trained:** {model_info['last_trained']}")
        st.write(f"**Cross-validation Score:** {model_info['cv_score']:.3f}")

def historical_analysis_page():
    st.header("📈 Historical Analysis")
    
    if 'processed_data' not in st.session_state:
        st.warning("Please upload and process data first!")
        return
    
    data = st.session_state.processed_data
    
    # Time series analysis
    st.subheader("⏰ Performance Over Time")
    
    # Sport selection for analysis
    selected_sport = st.selectbox("Select sport for analysis", data['sport'].unique())
    sport_data = data[data['sport'] == selected_sport]
    
    # Monthly performance trends
    fig = st.session_state.visualizer.create_monthly_trends(sport_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # Team performance comparison
    st.subheader("🏆 Team Performance Comparison")
    
    teams = list(set(sport_data['team1'].tolist() + sport_data['team2'].tolist()))
    selected_teams = st.multiselect(
        "Select teams to compare",
        teams,
        default=teams[:5] if len(teams) >= 5 else teams
    )
    
    if selected_teams:
        comparison_data = []
        for team in selected_teams:
            team_stats = st.session_state.data_processor.get_team_stats(sport_data, team)
            comparison_data.append({
                'Team': team,
                'Win Rate': team_stats['win_rate'],
                'Avg Points Scored': team_stats['avg_points_scored'],
                'Avg Points Conceded': team_stats['avg_points_conceded'],
                'Total Games': team_stats['total_games']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create comparison charts
        fig = st.session_state.visualizer.create_team_comparison_chart(comparison_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display comparison table
        st.subheader("📋 Detailed Comparison")
        st.dataframe(
            comparison_df.style.highlight_max(axis=0, subset=['Win Rate', 'Avg Points Scored'])
                            .highlight_min(axis=0, subset=['Avg Points Conceded'])
        )
    
    # Seasonal analysis
    st.subheader("🗓️ Seasonal Analysis")
    
    if len(sport_data) > 0:
        seasonal_stats = st.session_state.data_processor.get_seasonal_analysis(sport_data)
        
        if seasonal_stats is not None and not seasonal_stats.empty:
            fig = st.session_state.visualizer.create_seasonal_chart(seasonal_stats)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
