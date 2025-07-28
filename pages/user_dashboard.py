import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_management import UserManager
from utils.game_analyzer import GameAnalyzer

def main():
    st.set_page_config(
        page_title="SportsBet Pro - Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize managers
    user_manager = UserManager()
    user_manager.initialize_session()
    game_analyzer = GameAnalyzer()
    
    # Check authentication
    if not user_manager.is_authenticated():
        st.markdown("# 🏆 SportsBet Pro - Professional Sports Analytics")
        st.markdown("### Your gateway to AI-powered sports predictions")
        st.info("Please login to access your personalized dashboard")
        user_manager.login_form()
        return
    
    # User Dashboard Header
    user_info = user_manager.get_user_info()
    st.title(f"📊 Welcome back, {user_info['email'].split('@')[0].title()}!")
    st.markdown("### Your personalized sports analytics dashboard")
    
    # User controls in sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user_info['email']}")
        st.caption(f"Plan: {user_info['role'].title()}")
        
        if st.button("🚪 Logout"):
            user_manager.logout()
            
        st.divider()
        
        # Quick navigation
        st.markdown("### Quick Navigation")
        if st.button("🎯 Today's Predictions", use_container_width=True):
            st.session_state.show_predictions = True
        if st.button("📈 My Performance", use_container_width=True):
            st.session_state.show_performance = True
        if st.button("🏀 Live Games", use_container_width=True):
            st.session_state.show_live_games = True
            
        st.divider()
        
        # User stats
        st.markdown("### Your Stats")
        st.metric("Win Rate", "73.5%", "+2.1%")
        st.metric("Total Bets", "47", "+3")
        st.metric("Profit", "+$284", "+$45")
    
    # Main dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Predictions", "8", "+2")
    with col2:
        st.metric("This Week ROI", "+18.3%", "+5.2%")
    with col3:
        st.metric("Win Streak", "W4", "")
    with col4:
        st.metric("Confidence Avg", "82.1%", "+1.5%")
        
    st.divider()
    
    # Dashboard tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Today's Predictions", "📈 Performance", "🏀 Live Games"])
    
    with tab1:
        st.subheader("🎯 Today's Game Predictions")
        st.markdown("AI-powered predictions for today's games")
        
        # Fetch real games
        today = datetime.now().date()
        games = game_analyzer.fetch_real_games(today)
        
        # Add sample WNBA games for demonstration
        sample_wnba_games = [
            {
                'game_id': 'wnba_sea_con_20250728',
                'home_team': {'name': 'Connecticut Sun', 'abbreviation': 'CON', 'record': '18-8'},
                'away_team': {'name': 'Seattle Storm', 'abbreviation': 'SEA', 'record': '15-11'},
                'league': 'WNBA',
                'sport': 'basketball',
                'time': '7:00 PM ET',
                'venue': {'name': 'Mohegan Sun Arena', 'city': 'Uncasville', 'state': 'CT'}
            },
            {
                'game_id': 'wnba_ny_dal_20250728',
                'home_team': {'name': 'Dallas Wings', 'abbreviation': 'DAL', 'record': '12-14'},
                'away_team': {'name': 'New York Liberty', 'abbreviation': 'NY', 'record': '20-6'},
                'league': 'WNBA',
                'sport': 'basketball',
                'time': '8:00 PM ET',
                'venue': {'name': 'College Park Center', 'city': 'Arlington', 'state': 'TX'}
            }
        ]
        
        all_games = games + sample_wnba_games
        
        if all_games:
            st.success(f"Found {len(all_games)} games for analysis")
            
            for i, game in enumerate(all_games[:4]):  # Show up to 4 games
                with st.container():
                    # Game header
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 15px; border-radius: 10px; margin: 10px 0; color: white;">
                        <h3 style="margin: 0; text-align: center;">
                            🏀 {game['away_team']['name']} @ {game['home_team']['name']}
                        </h3>
                        <p style="margin: 5px 0; text-align: center; opacity: 0.9;">
                            {game['league']} | {game.get('time', 'TBD')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Analyze game
                    analysis = game_analyzer.analyze_game(game)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Main prediction
                        st.markdown(f"""
                        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; 
                                    border-left: 4px solid #4CAF50; margin: 10px 0;">
                            <h4 style="color: #2e7d32; margin: 0;">🏆 RECOMMENDED BET</h4>
                            <h3 style="color: #1b5e20; margin: 8px 0;">{analysis['recommended_bet']}</h3>
                            <p style="color: #388e3c; margin: 0;">
                                <strong>Confidence: {analysis['confidence']}%</strong> | 
                                Expected Value: +{analysis['expected_value']:.1f}%
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Key factors
                        st.markdown("**📊 Key Analysis Points:**")
                        for factor in analysis['key_factors']:
                            st.markdown(f"• {factor}")
                            
                    with col2:
                        # Team records
                        st.markdown("**📋 Team Records:**")
                        home_record = game['home_team'].get('record', 'N/A')
                        away_record = game['away_team'].get('record', 'N/A')
                        st.markdown(f"🏠 {game['home_team']['name']}: {home_record}")
                        st.markdown(f"✈️ {game['away_team']['name']}: {away_record}")
                        
                        # Risk assessment
                        st.markdown("**⚖️ Risk Level:**")
                        risk_color = '#4CAF50' if analysis['risk_level'] == 'LOW' else '#FF9800' if analysis['risk_level'] == 'MEDIUM' else '#f44336'
                        st.markdown(f"<span style='color: {risk_color}; font-weight: bold;'>{analysis['risk_level']} RISK</span>", unsafe_allow_html=True)
                        
                        # Betting tip
                        st.markdown("**💰 Betting Tip:**")
                        st.info(f"Recommended stake: 3-5% of bankroll")
                        
                    st.divider()
        else:
            st.info("No games available for today. Check back later for updates!")
    
    with tab2:
        st.subheader("📈 Your Performance Analytics")
        
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # Performance chart
            dates = pd.date_range(start='2025-06-01', end='2025-07-28', freq='D')
            cumulative_profit = [0.0]
            for i in range(1, len(dates)):
                change = np.random.normal(1.2, 3.5)  # Slight positive bias
                cumulative_profit.append(float(cumulative_profit[-1] + change))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=cumulative_profit,
                mode='lines',
                name='Cumulative Profit',
                line=dict(color='green', width=3),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title="Your Profit/Loss Over Time",
                xaxis_title="Date",
                yaxis_title="Profit ($)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with right_col:
            st.markdown("### Performance Summary")
            st.metric("Total Profit", "+$284.50", "+$45.20")
            st.metric("Best Day", "+$67.30", "July 25")
            st.metric("Avg Bet Size", "$15.20", "+$2.10")
            
            st.markdown("### Recent Activity")
            st.success("✅ Lakers +5.5 - Won")
            st.success("✅ Over 210.5 - Won") 
            st.error("❌ Celtics ML - Lost")
            st.success("✅ Under 8.5 - Won")
        
        # Recent bets table
        st.markdown("### Recent Betting History")
        betting_history = pd.DataFrame({
            'Date': ['2025-07-28', '2025-07-27', '2025-07-26', '2025-07-25', '2025-07-24'],
            'Game': ['Storm @ Sun', 'Lakers @ Warriors', 'Red Sox @ Yankees', 'Man City @ Arsenal', 'Chiefs @ Bills'],
            'Bet': ['Sun -3.5', 'Lakers +5.5', 'Over 8.5', 'Man City ML', 'Under 47.5'],
            'Stake': ['$20', '$25', '$15', '$30', '$20'],
            'Odds': ['-110', '+105', '-115', '-120', '-105'],
            'Result': ['Pending', 'Won +$26.25', 'Won +$13.04', 'Won +$25.00', 'Lost -$20.00'],
            'Profit': ['-', '+$26.25', '+$13.04', '+$25.00', '-$20.00']
        })
        
        st.dataframe(betting_history, use_container_width=True)
    
    with tab3:
        st.subheader("🏀 Live Games & Scores")
        
        # Fetch live games
        games = game_analyzer.fetch_real_games(datetime.now().date())
        
        if games:
            for game in games[:6]:  # Show up to 6 games
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{game['away_team']['name']} @ {game['home_team']['name']}**")
                    st.caption(f"{game['league']} | {game.get('time', 'TBD')}")
                    
                with col2:
                    away_score = game['away_team'].get('score', 0)
                    home_score = game['home_team'].get('score', 0)
                    
                    # Convert scores to integers safely
                    try:
                        away_score = int(away_score) if away_score else 0
                        home_score = int(home_score) if home_score else 0
                        
                        if away_score > 0 or home_score > 0:
                            st.markdown(f"**{away_score} - {home_score}**")
                        else:
                            st.markdown("**vs**")
                    except (ValueError, TypeError):
                        st.markdown("**vs**")
                        
                with col3:
                    status = game.get('status', 'Scheduled')
                    if 'Final' in status:
                        st.success(status)
                    elif 'In Progress' in status or 'Live' in status:
                        st.warning(status)
                    else:
                        st.info(status)
                        
                st.divider()
        else:
            st.info("No live games at the moment. Check back during game times!")

if __name__ == "__main__":
    main()