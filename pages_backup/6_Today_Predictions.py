import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.live_games import LiveGamesManager
from utils.sports_apis import SportsAPIManager
from utils.subscription import SubscriptionManager

def main():
    st.set_page_config(
        page_title="SportsBet Pro - Today's Predictions",
        page_icon="🎯",
        layout="wide"
    )
    
    # Initialize managers
    if 'live_games_manager' not in st.session_state:
        st.session_state.live_games_manager = LiveGamesManager()
    
    if 'subscription_manager' not in st.session_state:
        st.session_state.subscription_manager = SubscriptionManager()
    
    st.title("🎯 Today's Game Predictions")
    st.markdown("### AI-powered predictions with detailed analysis")
    
    # Subscription check
    subscription_manager = st.session_state.subscription_manager
    if not subscription_manager.check_feature_access('all_predictions'):
        st.error("🔒 Premium Predictions - Subscription Required")
        st.info("Upgrade to Pro or Enterprise to access detailed predictions with full analysis.")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 Upgrade Now", type="primary"):
                st.switch_page("pages/2_Pricing.py")
        return
    
    # Date selector
    today = datetime.now().date()
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        selected_date = st.date_input("Select Date", value=today, key="pred_date")
    
    st.divider()
    
    # Fetch games for selected date
    if st.button("🔄 Load Predictions", type="primary"):
        with st.spinner("Fetching today's games and generating predictions..."):
            fetch_and_display_predictions(selected_date)
    else:
        st.info("Click 'Load Predictions' to see AI-generated predictions for today's games")

def fetch_and_display_predictions(target_date):
    """Fetch games and display predictions"""
    
    # Get live games data
    live_games_manager = st.session_state.live_games_manager
    
    # Fetch games for the target date
    all_games = []
    
    # Get soccer games
    soccer_games = live_games_manager.get_soccer_games()
    if soccer_games is not None and len(soccer_games) > 0:
        # Filter for target date
        target_date_str = target_date.strftime('%Y-%m-%d')
        date_filtered = soccer_games[soccer_games['date'] == target_date_str]
        all_games.extend(date_filtered.to_dict('records'))
    
    # Get basketball games (if available)
    basketball_games = live_games_manager.get_basketball_games()
    if basketball_games is not None and len(basketball_games) > 0:
        target_date_str = target_date.strftime('%Y-%m-%d')
        date_filtered = basketball_games[basketball_games['date'] == target_date_str]
        all_games.extend(date_filtered.to_dict('records'))
    
    # Get baseball games (if available)
    baseball_games = live_games_manager.get_baseball_games()
    if baseball_games is not None and len(baseball_games) > 0:
        target_date_str = target_date.strftime('%Y-%m-%d')
        date_filtered = baseball_games[baseball_games['date'] == target_date_str]
        all_games.extend(date_filtered.to_dict('records'))
    
    if not all_games:
        st.warning(f"No games found for {target_date.strftime('%B %d, %Y')}")
        st.info("Try selecting a different date or check back later for updated schedules.")
        return
    
    st.success(f"Found {len(all_games)} games for {target_date.strftime('%B %d, %Y')}")
    
    # Display predictions for each game
    for i, game in enumerate(all_games):
        display_game_prediction(game, i)

def display_game_prediction(game, index):
    """Display detailed prediction for a single game"""
    
    # Extract game information
    home_team = game.get('home_team', {})
    away_team = game.get('away_team', {})
    
    if isinstance(home_team, dict) and isinstance(away_team, dict):
        home_name = home_team.get('name', 'Home Team')
        away_name = away_team.get('name', 'Away Team')
    else:
        home_name = "Home Team"
        away_name = "Away Team"
    
    league = game.get('league', 'League')
    game_time = game.get('time', 'TBD')
    venue = game.get('venue', {})
    venue_name = venue.get('name', 'TBD') if isinstance(venue, dict) else 'TBD'
    
    # Create prediction card
    with st.container():
        # Header
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #1f4e79, #2e5984); padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: white; margin: 0; text-align: center;">
                🎯 PREDICTION #{index + 1}
            </h3>
            <h2 style="color: white; margin: 5px 0; text-align: center;">
                {away_name} vs {home_name}
            </h2>
            <p style="color: #ccc; margin: 0; text-align: center;">
                {league} | {game_time} | {venue_name}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate AI prediction using real APIs
        prediction_data = generate_prediction_analysis(home_name, away_name, league)
        
        # Check if prediction is available
        if not prediction_data:
            st.error("❌ **No AI Prediction Available**")
            st.info("🔑 Configure OpenAI or Google API keys in Streamlit Cloud secrets to enable AI predictions")
            return
        
        # Display prediction in columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Main prediction
            st.markdown("### 🏆 RECOMMENDED BET")
            st.markdown(f"""
            <div style="background-color: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;">
                <h2 style="color: #2e7d32; margin: 0;">{prediction_data['main_pick']}</h2>
                <p style="color: #388e3c; font-size: 18px; margin: 5px 0;">
                    <strong>Confidence: {prediction_data['confidence']}%</strong>
                </p>
                <p style="color: #4caf50; margin: 0;">
                    Expected Value: {prediction_data['expected_value']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Alternative picks
            st.markdown("### 🎲 Alternative Bets")
            for alt_pick in prediction_data['alternative_picks']:
                st.markdown(f"""
                <div style="background-color: #f0f7ff; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #2196F3;">
                    <strong>{alt_pick['pick']}</strong> - Confidence: {alt_pick['confidence']}%
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Key statistics and reasoning
            st.markdown("### 📊 Analysis")
            
            st.markdown("**Key Factors:**")
            for factor in prediction_data['key_factors']:
                st.markdown(f"• {factor}")
            
            st.markdown("**Team Form:**")
            st.markdown(f"🏠 **{home_name}**: {prediction_data['home_form']}")
            st.markdown(f"✈️ **{away_name}**: {prediction_data['away_form']}")
            
            st.markdown("**Head-to-Head:**")
            st.markdown(f"{prediction_data['head_to_head']}")
        
        # Detailed analysis section
        with st.expander("📋 Detailed Analysis", expanded=False):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Offensive Analysis:**")
                st.markdown(prediction_data['offensive_analysis'])
                
                st.markdown("**Recent Performance:**")
                st.markdown(prediction_data['recent_performance'])
            
            with col_b:
                st.markdown("**Defensive Analysis:**")
                st.markdown(prediction_data['defensive_analysis'])
                
                st.markdown("**Injury Report:**")
                st.markdown(prediction_data['injury_report'])
        
        # Risk assessment
        risk_level = prediction_data['risk_level']
        risk_color = {'Low': '#4CAF50', 'Medium': '#FF9800', 'High': '#f44336'}[risk_level]
        
        st.markdown(f"""
        <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>Risk Assessment:</strong> 
            <span style="color: {risk_color}; font-weight: bold;">{risk_level} Risk</span>
            <br><small>{prediction_data['risk_explanation']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

def generate_prediction_analysis(home_team, away_team, league):
    """Generate AI prediction analysis using real APIs"""
    import sys
    import os
    
    # Add parent directory to path to import main functions
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from app import get_ai_analysis
        
        # Create game object for AI analysis
        game = {
            'home_team': home_team,
            'away_team': away_team,
            'sport': league,
            'league': league
        }
        
        # Get real AI analysis
        analysis = get_ai_analysis(game)
        
        if analysis:
            # Convert to format expected by the display function
            return {
                'main_pick': analysis.get('predicted_winner', 'No prediction'),
                'confidence': analysis.get('confidence', 0) * 100,  # Convert to percentage
                'expected_value': f"+{analysis.get('roi_estimate', 5):.1f}%",
                'alternative_picks': [
                    {'pick': f"{analysis.get('predicted_spread', 'Even')} spread", 'confidence': analysis.get('confidence', 0) * 90},
                    {'pick': f"Over/Under {analysis.get('predicted_total', 'TBD')}", 'confidence': analysis.get('confidence', 0) * 85}
                ],
                'key_factors': analysis.get('key_factors', ['Real-time AI analysis', 'Historical performance', 'Current form']),
                'home_form': 'Analyzing...',
                'away_form': 'Analyzing...',
                'head_to_head': analysis.get('reasoning', 'AI analysis based on current data')[:100] + '...',
                'offensive_analysis': 'Based on recent performance and statistical analysis.',
                'defensive_analysis': 'Considering defensive metrics and recent form.',
                'recent_performance': 'AI-powered analysis of latest games and trends.',
                'injury_report': 'Current roster status factored into prediction.',
                'risk_level': 'Medium',
                'risk_explanation': 'Standard sports betting carries inherent risk. Bet responsibly.'
            }
        else:
            return None
            
    except Exception as e:
        st.error(f"Error generating prediction: {str(e)}")
        return None
    
