import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.live_games import LiveGamesManager
from utils.sports_apis import SportsAPIManager

def check_subscription():
    """Check if user has valid subscription"""
    # For demo purposes - in real app, this would check payment status
    return st.session_state.get('subscription_active', False)

def main():
    st.set_page_config(
        page_title="SportsBet Pro - Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize session state
    if 'api_manager' not in st.session_state:
        st.session_state.api_manager = SportsAPIManager()
    
    if 'live_games_manager' not in st.session_state:
        st.session_state.live_games_manager = LiveGamesManager()
    
    # Testing mode - full access
    st.info("🧪 **Testing Mode**: Full dashboard access for system evaluation")
    
    st.title("📊 SportsBet Pro Dashboard")
    st.markdown("### Your personalized sports betting analytics platform")
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Active Predictions", "12", "+3")
    
    with col2:
        st.metric("Win Rate", "73.5%", "+2.1%")
    
    with col3:
        st.metric("ROI", "+24.8%", "+5.2%")
    
    with col4:
        st.metric("Units Won", "+18.5", "+4.2")
    
    with col5:
        st.metric("Streak", "W5", "")
    
    st.divider()
    
    # Main Dashboard Content
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("📈 Performance Analytics")
        
        # Sample performance chart
        dates = pd.date_range(start='2025-06-01', end='2025-07-27', freq='D')
        cumulative_profit = [0]
        for i in range(1, len(dates)):
            change = np.random.normal(0.5, 2)  # Slight positive bias
            cumulative_profit.append(cumulative_profit[-1] + change)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=cumulative_profit,
            mode='lines',
            name='Cumulative Profit',
            line=dict(color='green', width=3)
        ))
        
        fig.update_layout(
            title="Profit/Loss Over Time",
            xaxis_title="Date",
            yaxis_title="Units",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent Predictions Table
        st.subheader("🎯 Recent Predictions")
        recent_predictions = pd.DataFrame({
            'Date': ['2025-07-27', '2025-07-26', '2025-07-25', '2025-07-24'],
            'Game': ['Lakers vs Warriors', 'Red Sox vs Yankees', 'Man City vs Arsenal', 'Chiefs vs Bills'],
            'Prediction': ['Lakers +5.5', 'Over 8.5', 'Man City ML', 'Under 47.5'],
            'Confidence': ['85%', '92%', '78%', '88%'],
            'Status': ['Pending', 'Won ✅', 'Won ✅', 'Lost ❌'],
            'Result': ['-', '+1.8u', '+1.0u', '-1.1u']
        })
        
        st.dataframe(recent_predictions, use_container_width=True)
    
    with right_col:
        st.subheader("🔥 Today's Hot Picks")
        
        hot_picks = [
            {
                'game': 'Lakers @ Warriors',
                'pick': 'Over 215.5',
                'confidence': 94,
                'reasoning': 'Both teams averaging 110+ PPG in last 10 games'
            },
            {
                'game': 'Yankees @ Red Sox',
                'pick': 'Yankees -1.5',
                'confidence': 87,
                'reasoning': 'Yankees 8-2 in last 10 vs Red Sox'
            },
            {
                'game': 'Chelsea @ Arsenal',
                'pick': 'BTTS Yes',
                'confidence': 91,
                'reasoning': 'Both teams scored in 7/8 recent meetings'
            }
        ]
        
        for pick in hot_picks:
            with st.expander(f"🎯 {pick['game']} - {pick['confidence']}%"):
                st.write(f"**Pick:** {pick['pick']}")
                st.write(f"**Confidence:** {pick['confidence']}%")
                st.write(f"**Analysis:** {pick['reasoning']}")
                st.button(f"Place Bet", key=f"bet_{pick['game']}")
        
        st.divider()
        
        # Subscription Status
        st.subheader("💎 Subscription Status")
        st.success("Pro Plan Active")
        st.write("✅ Unlimited predictions")
        st.write("✅ Real-time data")
        st.write("✅ Advanced analytics")
        st.write("✅ SMS alerts")
        
        if st.button("Manage Subscription"):
            st.info("Redirecting to billing portal...")

if __name__ == "__main__":
    import numpy as np
    main()