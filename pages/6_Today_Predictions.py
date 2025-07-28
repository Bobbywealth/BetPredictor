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
        
        # Generate AI prediction (mock for demo - in real app would use ML model)
        prediction_data = generate_prediction_analysis(home_name, away_name, league)
        
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
    """Generate AI prediction analysis (mock data for demo)"""
    import random
    
    # In a real application, this would use actual ML models and historical data
    confidence = random.randint(75, 95)
    
    # Generate realistic predictions based on sport
    if 'soccer' in league.lower() or 'football' in league.lower():
        main_picks = [
            f"{home_team} to Win", 
            f"{away_team} to Win",
            "Both Teams to Score",
            "Over 2.5 Goals",
            "Under 2.5 Goals"
        ]
    elif 'basketball' in league.lower() or 'nba' in league.lower():
        main_picks = [
            f"{home_team} +5.5",
            f"{away_team} -5.5", 
            "Over 215.5 Points",
            "Under 215.5 Points"
        ]
    else:  # Baseball
        main_picks = [
            f"{home_team} Moneyline",
            f"{away_team} Moneyline",
            "Over 8.5 Runs",
            "Under 8.5 Runs"
        ]
    
    main_pick = random.choice(main_picks)
    
    return {
        'main_pick': main_pick,
        'confidence': confidence,
        'expected_value': f"+{random.randint(8, 25)}.{random.randint(0, 9)}%",
        'alternative_picks': [
            {'pick': random.choice(main_picks), 'confidence': random.randint(65, 85)},
            {'pick': random.choice(main_picks), 'confidence': random.randint(60, 80)}
        ],
        'key_factors': [
            f"{home_team} has won 4 of last 5 home games",
            f"{away_team} averages {random.randint(15, 25)} shots per game",
            f"Weather conditions favor {random.choice([home_team, away_team])}",
            f"Key player {random.choice(['available', 'questionable', 'out'])} for {random.choice([home_team, away_team])}"
        ],
        'home_form': f"W-W-L-W-W (Last 5: {random.randint(60, 85)}% win rate)",
        'away_form': f"W-L-W-L-W (Last 5: {random.randint(55, 80)}% win rate)",
        'head_to_head': f"{random.choice([home_team, away_team])} leads series {random.randint(5, 15)}-{random.randint(3, 12)} in last 20 meetings",
        'offensive_analysis': f"{home_team} averaging {random.randint(15, 30)} scoring opportunities per game. Strong in final third with {random.randint(65, 85)}% pass accuracy.",
        'defensive_analysis': f"{away_team} has conceded only {random.randint(8, 15)} goals in last 10 games. Solid defensive structure with {random.randint(70, 90)}% tackle success rate.",
        'recent_performance': f"Both teams coming off {random.choice(['wins', 'losses', 'draws'])} in previous fixtures. {home_team} has {random.choice(['improved', 'declined', 'maintained'])} form recently.",
        'injury_report': f"{random.choice([home_team, away_team])} missing {random.randint(1, 3)} key players. {random.choice([home_team, away_team])} at full strength.",
        'risk_level': random.choice(['Low', 'Medium', 'High']),
        'risk_explanation': f"Based on team form, historical data, and current conditions. {random.choice(['Both teams', 'Home team', 'Away team'])} showing consistent performance patterns."
    }

if __name__ == "__main__":
    main()