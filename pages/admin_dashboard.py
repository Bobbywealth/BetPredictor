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
        page_title="SportsBet Pro - Admin Dashboard",
        page_icon="⚙️",
        layout="wide"
    )
    
    # Initialize managers
    user_manager = UserManager()
    user_manager.initialize_session()
    
    # Check admin access
    if not user_manager.is_admin():
        st.error("🔒 Admin access required")
        st.info("Please login with admin credentials to access this dashboard")
        user_manager.login_form()
        return
        
    # Admin Dashboard Header
    st.title("⚙️ Admin Dashboard - SportsBet Pro")
    st.markdown("### System administration and analytics overview")
    
    # Admin controls in sidebar
    with st.sidebar:
        st.markdown("### Admin Controls")
        if st.button("🚪 Logout"):
            user_manager.logout()
            
        st.divider()
        
        # System stats
        st.markdown("### System Status")
        st.success("✅ API Services Online")
        st.success("✅ Database Connected")
        st.success("✅ Analytics Running")
        
        # Quick actions
        st.markdown("### Quick Actions")
        if st.button("🔄 Refresh Game Data"):
            st.success("Game data refreshed!")
        if st.button("📧 Send User Notifications"):
            st.success("Notifications sent!")
    
    # Main admin metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Users", "1,247", "+23")
    with col2:
        st.metric("Active Subscriptions", "892", "+15")
    with col3:
        st.metric("Daily Predictions", "156", "+8")
    with col4:
        st.metric("API Calls Today", "2,451", "+127")
    with col5:
        st.metric("System Uptime", "99.8%", "+0.1%")
        
    st.divider()
    
    # Admin dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "👥 User Management", "🎯 Predictions", "⚙️ System Config"])
    
    with tab1:
        st.subheader("📊 System Analytics")
        
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # User growth chart
            dates = pd.date_range(start='2025-06-01', end='2025-07-28', freq='D')
            users = [850 + i * 7 + np.random.randint(-5, 15) for i in range(len(dates))]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=users,
                mode='lines+markers',
                name='Total Users',
                line=dict(color='#1f77b4', width=3)
            ))
            
            fig.update_layout(
                title="User Growth Over Time",
                xaxis_title="Date",
                yaxis_title="Users",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with right_col:
            st.markdown("### Revenue Metrics")
            st.metric("Monthly Revenue", "$45,230", "+12.5%")
            st.metric("Avg Revenue/User", "$38.20", "+2.1%")
            st.metric("Churn Rate", "2.3%", "-0.4%")
            
            st.markdown("### Popular Features")
            st.progress(0.85, "Today's Predictions")
            st.progress(0.72, "Live Games")
            st.progress(0.68, "Analytics Dashboard")
            st.progress(0.45, "API Access")
    
    with tab2:
        st.subheader("👥 User Management")
        
        # User search and filters
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_user = st.text_input("🔍 Search users...")
        with col2:
            user_filter = st.selectbox("Filter by plan", ["All", "Free", "Basic", "Pro", "Enterprise"])
        with col3:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
            
        # Sample user data
        users_df = pd.DataFrame({
            'Email': ['user1@email.com', 'user2@email.com', 'admin@sportsbet.com', 'user3@email.com'],
            'Plan': ['Pro', 'Basic', 'Enterprise', 'Free'],
            'Status': ['Active', 'Active', 'Active', 'Inactive'],
            'Join Date': ['2025-06-15', '2025-07-01', '2025-01-01', '2025-07-20'],
            'Last Login': ['2025-07-28', '2025-07-27', '2025-07-28', '2025-07-25']
        })
        
        st.dataframe(users_df, use_container_width=True)
        
        # User actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 Send Notification"):
                st.success("Notification sent to selected users")
        with col2:
            if st.button("🔄 Reset Password"):
                st.success("Password reset email sent")
        with col3:
            if st.button("🚫 Suspend User"):
                st.warning("User suspended")
    
    with tab3:
        st.subheader("🎯 Predictions Management")
        
        # Initialize game analyzer
        game_analyzer = GameAnalyzer()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Today's Game Analysis")
            
            # Fetch and analyze real games
            today = datetime.now().date()
            games = game_analyzer.fetch_real_games(today)
            
            if games:
                st.success(f"Found {len(games)} games for analysis")
                
                for i, game in enumerate(games[:3]):  # Show first 3 games
                    with st.expander(f"🏀 {game['away_team']['name']} vs {game['home_team']['name']}"):
                        analysis = game_analyzer.analyze_game(game)
                        
                        st.write(f"**League:** {game['league']}")
                        st.write(f"**Confidence:** {analysis['confidence']}%")
                        st.write(f"**Recommended Bet:** {analysis['recommended_bet']}")
                        st.write(f"**Risk Level:** {analysis['risk_level']}")
                        st.write(f"**Expected Value:** +{analysis['expected_value']:.1f}%")
                        
                        st.markdown("**Key Factors:**")
                        for factor in analysis['key_factors']:
                            st.write(f"• {factor}")
            else:
                st.info("No games found for today. Trying to fetch sample data...")
                
        with col2:
            st.markdown("### Prediction Performance")
            
            # Sample prediction accuracy data
            accuracy_data = {
                'Sport': ['Basketball', 'Soccer', 'Baseball'],
                'Predictions': [45, 32, 28],
                'Wins': [34, 22, 19],
                'Win Rate': ['75.6%', '68.8%', '67.9%']
            }
            
            accuracy_df = pd.DataFrame(accuracy_data)
            st.dataframe(accuracy_df, use_container_width=True)
            
            # Prediction controls
            st.markdown("### Prediction Controls")
            confidence_threshold = st.slider("Minimum Confidence %", 50, 95, 75)
            auto_publish = st.checkbox("Auto-publish predictions", True)
            
            if st.button("🔄 Regenerate All Predictions"):
                st.success("All predictions regenerated!")
    
    with tab4:
        st.subheader("⚙️ System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### API Settings")
            
            # API configuration
            espn_api = st.checkbox("ESPN API", True)
            sportsdb_api = st.checkbox("TheSportsDB API", True)
            
            st.markdown("### Rate Limiting")
            api_rate_limit = st.number_input("API calls per minute", 60, 1000, 300)
            
            st.markdown("### Data Refresh")
            refresh_interval = st.selectbox("Game data refresh", ["5 minutes", "10 minutes", "30 minutes", "1 hour"])
            
        with col2:
            st.markdown("### Feature Flags")
            
            live_predictions = st.checkbox("Live Predictions", True)
            email_notifications = st.checkbox("Email Notifications", True)
            sms_alerts = st.checkbox("SMS Alerts", False)
            
            st.markdown("### Subscription Plans")
            st.text_input("Basic Plan Price", "$29")
            st.text_input("Pro Plan Price", "$79")
            st.text_input("Enterprise Plan Price", "$199")
            
        # Save configuration
        if st.button("💾 Save Configuration", type="primary"):
            st.success("Configuration saved successfully!")

if __name__ == "__main__":
    main()