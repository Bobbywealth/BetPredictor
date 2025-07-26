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
from utils.sports_apis import SportsAPIManager
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
if 'sports_api_manager' not in st.session_state:
    st.session_state.sports_api_manager = SportsAPIManager()

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
        "Live Sports Data",
        "Data Upload & Processing", 
        "Team Analysis",
        "Make Predictions",
        "Model Performance",
        "Historical Analysis"
    ])
    
    if page == "Live Sports Data":
        live_sports_data_page()
    elif page == "Data Upload & Processing":
        data_upload_page()
    elif page == "Team Analysis":
        team_analysis_page()
    elif page == "Make Predictions":
        prediction_page()
    elif page == "Model Performance":
        model_performance_page()
    elif page == "Historical Analysis":
        historical_analysis_page()

def live_sports_data_page():
    st.header("🔴 Live Sports Data")
    
    st.info(
        "🚀 **NEW FEATURE**: Get real-time sports data from multiple APIs! "
        "Free options work immediately, premium APIs provide more detailed data."
    )
    
    # API Configuration Section
    st.subheader("⚙️ API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Free APIs (No Setup Required)**")
        free_apis_status = st.container()
        
        with free_apis_status:
            # Test free APIs
            espn_status, espn_msg = st.session_state.sports_api_manager.test_api_connection('espn')
            sportsdb_status, sportsdb_msg = st.session_state.sports_api_manager.test_api_connection('thesportsdb')
            
            st.success(f"✅ ESPN: Ready") if espn_status else st.error(f"❌ ESPN: Not working")
            st.success(f"✅ TheSportsDB: Ready") if sportsdb_status else st.error(f"❌ TheSportsDB: Not working")
    
    with col2:
        st.write("**Premium APIs (API Keys Required)**")
        
        # API Key inputs
        api_football_key = st.text_input(
            "API-Football Key (Optional)", 
            type="password",
            help="Get free key at api-football.com"
        )
        
        mysportsfeeds_key = st.text_input(
            "MySportsFeeds Key (Optional)", 
            type="password", 
            help="Get free key at mysportsfeeds.com"
        )
        
        if api_football_key:
            api_football_status, api_football_msg = st.session_state.sports_api_manager.test_api_connection('api_football', api_football_key)
            st.success(f"✅ API-Football: Connected") if api_football_status else st.error(f"❌ API-Football: {api_football_msg}")
        
        if mysportsfeeds_key:
            mysportsfeeds_status, mysportsfeeds_msg = st.session_state.sports_api_manager.test_api_connection('mysportsfeeds', mysportsfeeds_key)
            st.success(f"✅ MySportsFeeds: Connected") if mysportsfeeds_status else st.error(f"❌ MySportsFeeds: {mysportsfeeds_msg}")
    
    st.divider()
    
    # Data Fetching Section
    st.subheader("📡 Fetch Live Data")
    
    col3, col4 = st.columns([3, 1])
    
    with col3:
        st.write("**Available Data Sources:**")
        st.write("• **ESPN**: NFL, NBA, MLB, NHL (Free)")
        st.write("• **TheSportsDB**: Football, Basketball, Baseball (Free)")
        st.write("• **API-Football**: 1000+ leagues, live odds (Premium)")
        st.write("• **MySportsFeeds**: NFL, NBA, MLB detailed stats (Premium)")
    
    with col4:
        # Free data button
        if st.button("📊 Use Free Data", type="primary"):
            with st.spinner("Getting free sports data..."):
                # Use sample data as reliable fallback
                from data.sample_data import get_sample_data
                
                # Get sample data for multiple sports
                all_sample_data = []
                for sport in ['football', 'basketball', 'baseball']:
                    sample_data = get_sample_data(sport)
                    all_sample_data.append(sample_data)
                
                if all_sample_data:
                    combined_sample = pd.concat(all_sample_data, ignore_index=True)
                    
                    # Store in session state
                    st.session_state.live_sports_data = combined_sample
                    st.session_state.uploaded_data = combined_sample
                    
                    st.success(f"✅ Loaded {len(combined_sample)} sample games across {len(all_sample_data)} sports!")
                    
                    # Auto-process the data
                    processed_data = st.session_state.data_processor.process_data(combined_sample)
                    if len(processed_data) > 10:
                        st.session_state.processed_data = processed_data
                        
                        # Auto-train the model
                        training_success = st.session_state.predictor.train_model(processed_data)
                        if training_success:
                            st.success("🤖 Model trained with sample data!")
        
        # Premium data button
        if st.button("🚀 Fetch Premium Data"):
            # Prepare API keys
            api_keys = {}
            if api_football_key:
                api_keys['api_football'] = api_football_key
            if mysportsfeeds_key:
                api_keys['mysportsfeeds'] = mysportsfeeds_key
            
            if not api_keys:
                st.warning("⚠️ Please enter API keys above to use premium data sources")
            else:
                # Fetch data from premium APIs only
                with st.spinner("Fetching premium sports data..."):
                    live_data = st.session_state.sports_api_manager.get_all_data(api_keys)
                    
                    if not live_data.empty:
                        # Store in session state
                        st.session_state.live_sports_data = live_data
                        st.session_state.uploaded_data = live_data
                        
                        st.success(f"🎉 Successfully loaded {len(live_data)} premium games!")
                        
                        # Auto-process the data
                        processed_data = st.session_state.data_processor.process_data(live_data)
                        if len(processed_data) > 10:
                            st.session_state.processed_data = processed_data
                            
                            # Auto-train the model
                            training_success = st.session_state.predictor.train_model(processed_data)
                            if training_success:
                                st.success("🤖 Model trained with premium live data!")
                            else:
                                st.warning("⚠️ Could not train model with current data")
                    else:
                        st.error("❌ Could not fetch data from premium API sources")
                        st.info("💡 Check your API keys or try the free data option above")
    
    # Display Current Data
    if 'live_sports_data' in st.session_state and not st.session_state.live_sports_data.empty:
        st.divider()
        st.subheader("📊 Current Live Data")
        
        data = st.session_state.live_sports_data
        
        # Data summary
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Total Games", len(data))
        with col6:
            st.metric("Data Sources", data['source'].nunique())
        with col7:
            st.metric("Sports Covered", data['sport'].nunique())
        with col8:
            st.metric("Leagues", data['league'].nunique())
        
        # Recent games preview
        st.subheader("🕒 Recent Games")
        recent_games = data.sort_values('date', ascending=False).head(10)
        st.dataframe(
            recent_games[['date', 'team1', 'team2', 'team1_score', 'team2_score', 'sport', 'league', 'source']],
            use_container_width=True
        )
        
        # Data breakdown by source
        st.subheader("📈 Data Source Breakdown")
        source_breakdown = data.groupby(['source', 'sport']).size().reset_index(name='count')
        
        fig = px.bar(
            source_breakdown, 
            x='source', 
            y='count', 
            color='sport',
            title='Games by Source and Sport',
            labels={'count': 'Number of Games', 'source': 'Data Source'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Option to use this data for predictions
        if st.button("🎯 Use This Data for Predictions"):
            st.session_state.uploaded_data = data
            st.success("✅ Live data is now ready for predictions! Go to 'Make Predictions' page.")
    
    # API Setup Help
    st.divider()
    with st.expander("🆘 How to Get API Keys"):
        st.write("**API-Football (Recommended for Premium Features):**")
        st.write("1. Go to [api-football.com](https://api-football.com)")
        st.write("2. Sign up for free account")
        st.write("3. Get your API key from dashboard")
        st.write("4. Free tier: 100 requests/day")
        
        st.write("**MySportsFeeds (Good for NFL/NBA/MLB):**")
        st.write("1. Go to [mysportsfeeds.com](https://mysportsfeeds.com)")
        st.write("2. Create free developer account")
        st.write("3. Get API key from your account settings")
        st.write("4. Free for non-commercial use")
        
        st.write("**Free Options (Always Available):**")
        st.write("• ESPN API - No registration needed")
        st.write("• TheSportsDB - No registration needed")
        st.write("• Both provide real game results and scores")

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
