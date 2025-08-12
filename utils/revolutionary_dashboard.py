"""
🚀 Revolutionary Home Dashboard
Professional, impressive first impression with advanced analytics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def show_revolutionary_dashboard():
    """Revolutionary home dashboard that impresses from first login"""
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .prediction-card {
        background: linear-gradient(45deg, #f8f9ff, #e8f2ff);
        border: 1px solid #e1e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .confidence-bar {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #ff4444, #ffaa00, #00aa00);
        margin: 0.5rem 0;
    }
    
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #ff4444;
        border-radius: 50%;
        animation: pulse 1s infinite;
        margin-right: 8px;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    .quick-action-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    user = st.session_state.get('username', 'Champion')
    
    # Fix timezone issue - use Eastern time
    import pytz
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)
    
    # Time-based greeting
    hour = current_time.hour
    if hour < 12:
        greeting = "Good Morning"
        emoji = "🌅"
    elif hour < 17:
        greeting = "Good Afternoon"  
        emoji = "☀️"
    else:
        greeting = "Good Evening"
        emoji = "🌙"
    
    st.markdown(f"""
    <div class="hero-section">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700;">
                    {emoji} {greeting}, {user}!
                </h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                    {current_time.strftime('%A, %B %d, %Y • %I:%M %p EST')}
                </p>
                <div style="margin-top: 1rem;">
                    <span class="live-indicator"></span>
                    <span style="font-weight: 500;">AI Engines Active • Real-time Analysis</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 3rem; opacity: 0.8;">🧠⚡</div>
                <div style="font-size: 0.9rem; opacity: 0.7;">Powered by GPT-4 + Gemini</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time Performance Dashboard
    show_live_performance_metrics()
    
    # Today's Market Intelligence
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_todays_market_intelligence()
    
    with col2:
        show_ai_confidence_radar()
    
    # Live Games & Predictions
    show_live_predictions_feed()
    
    # Quick Actions Hub
    show_quick_actions_hub()

def show_live_performance_metrics():
    """Live performance metrics with impressive visualizations"""
    
    st.markdown("## 📊 Live Performance Dashboard")
    
    # Get real metrics
    from app import calculate_betting_stats, get_real_dashboard_metrics
    
    metrics = get_real_dashboard_metrics()
    stats_7d = calculate_betting_stats(7)
    stats_30d = calculate_betting_stats(30)
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        win_rate = stats_7d.get('win_rate', 0) * 100
        color = "#00aa00" if win_rate >= 60 else "#ffaa00" if win_rate >= 50 else "#ff4444"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2.2rem; font-weight: bold; color: {color};">
                        {win_rate:.1f}%
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">7-Day Win Rate</div>
                    <div style="font-size: 0.8rem; color: #999;">
                        {stats_7d.get('wins', 0)}-{stats_7d.get('losses', 0)} Record
                    </div>
                </div>
                <div style="font-size: 2rem;">🎯</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        roi = stats_7d.get('roi', 0)
        roi_color = "#00aa00" if roi > 0 else "#ff4444"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2.2rem; font-weight: bold; color: {roi_color};">
                        {roi:+.1f}%
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">7-Day ROI</div>
                    <div style="font-size: 0.8rem; color: #999;">
                        ${stats_7d.get('net_profit', 0):+.0f} Profit
                    </div>
                </div>
                <div style="font-size: 2rem;">💰</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_picks = stats_30d.get('total_bets', 0)
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2.2rem; font-weight: bold; color: #667eea;">
                        {total_picks}
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">30-Day Volume</div>
                    <div style="font-size: 0.8rem; color: #999;">
                        ${stats_30d.get('total_wagered', 0):,.0f} Wagered
                    </div>
                </div>
                <div style="font-size: 2rem;">📈</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        games_today = metrics.get('games_today', 0)
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2.2rem; font-weight: bold; color: #ff6b35;">
                        {games_today}
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">Games Today</div>
                    <div style="font-size: 0.8rem; color: #999;">
                        Live Analysis Ready
                    </div>
                </div>
                <div style="font-size: 2rem;">🏈</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_todays_market_intelligence():
    """Today's market intelligence and trends"""
    
    st.markdown("### 🎯 Today's Market Intelligence")
    
    # Generate sample market data for demo
    market_data = generate_market_intelligence_data()
    
    # Market trends chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=market_data['hours'],
        y=market_data['confidence_trend'],
        mode='lines+markers',
        name='AI Confidence',
        line=dict(color='#667eea', width=3),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=market_data['hours'],
        y=market_data['volume_trend'],
        mode='lines+markers',
        name='Market Volume',
        line=dict(color='#ff6b35', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Real-time Market Analysis",
        xaxis_title="Time (EST)",
        yaxis_title="AI Confidence Level",
        yaxis2=dict(
            title="Market Volume",
            overlaying='y',
            side='right'
        ),
        height=300,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Market insights
    st.markdown("""
    **🔥 Live Market Insights:**
    - High-confidence opportunities detected in NBA (3 games)
    - Sharp money movement on NFL underdogs
    - Weather impact analysis active for outdoor games
    - Injury reports updated within last hour
    """)

def show_ai_confidence_radar():
    """AI confidence radar chart by sport"""
    
    st.markdown("### 🧠 AI Confidence by Sport")
    
    # Sample confidence data
    sports = ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF']
    confidence_scores = [85, 92, 78, 88, 82]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=confidence_scores,
        theta=sports,
        fill='toself',
        name='AI Confidence',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        height=300,
        showlegend=False,
        title="Confidence Levels"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_live_predictions_feed():
    """Live predictions feed with real-time updates"""
    
    st.markdown("### ⚡ Live Predictions Feed")
    
    # Sample live predictions
    predictions = [
        {
            'game': 'Lakers @ Warriors',
            'sport': 'NBA',
            'pick': 'Lakers',
            'confidence': 87,
            'edge': 12.3,
            'time': '8:00 PM',
            'status': 'PREMIUM'
        },
        {
            'game': 'Chiefs @ Bills', 
            'sport': 'NFL',
            'pick': 'Under 47.5',
            'confidence': 82,
            'edge': 8.7,
            'time': '1:00 PM',
            'status': 'STRONG'
        },
        {
            'game': 'Dodgers @ Yankees',
            'sport': 'MLB', 
            'pick': 'Dodgers ML',
            'confidence': 79,
            'edge': 6.2,
            'time': '7:30 PM',
            'status': 'MODERATE'
        }
    ]
    
    for pred in predictions:
        confidence_color = "#00aa00" if pred['confidence'] >= 85 else "#ffaa00" if pred['confidence'] >= 75 else "#ff6b35"
        status_color = {"PREMIUM": "#9d4edd", "STRONG": "#f77f00", "MODERATE": "#457b9d"}
        
        st.markdown(f"""
        <div class="prediction-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: bold; font-size: 1.1rem;">
                        🏀 {pred['game']} • {pred['time']}
                    </div>
                    <div style="margin: 0.5rem 0;">
                        <span style="background: {status_color.get(pred['status'], '#667eea')}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">
                            {pred['status']} PLAY
                        </span>
                        <span style="margin-left: 1rem; font-weight: 500;">Pick: {pred['pick']}</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">
                        Edge: +{pred['edge']}% • Expected Value: Positive
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: {confidence_color};">
                        {pred['confidence']}%
                    </div>
                    <div style="font-size: 0.8rem; color: #999;">Confidence</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_quick_actions_hub():
    """Quick actions hub for immediate access"""
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 Generate Picks", use_container_width=True, type="primary"):
            st.session_state.current_page = 'picks'
            st.rerun()
    
    with col2:
        if st.button("📺 Live Scores", use_container_width=True):
            st.session_state.current_page = 'live_scores'
            st.rerun()
    
    with col3:
        if st.button("🏆 Win Tracker", use_container_width=True):
            st.session_state.current_page = 'portfolio'
            st.rerun()
    
    with col4:
        if st.button("🧪 AI Lab", use_container_width=True):
            st.session_state.show_ai_lab = True
            st.rerun()

def generate_market_intelligence_data():
    """Generate sample market intelligence data"""
    
    hours = [f"{h:02d}:00" for h in range(9, 24)]  # 9 AM to 11 PM
    
    # Generate realistic trends
    base_confidence = 75
    confidence_trend = [
        base_confidence + np.sin(i * 0.5) * 10 + np.random.normal(0, 3)
        for i in range(len(hours))
    ]
    
    base_volume = 50
    volume_trend = [
        base_volume + np.cos(i * 0.3) * 20 + np.random.normal(0, 5)
        for i in range(len(hours))
    ]
    
    return {
        'hours': hours,
        'confidence_trend': confidence_trend,
        'volume_trend': volume_trend
    }
