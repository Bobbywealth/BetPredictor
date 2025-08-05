import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

def show_business_home():
    """Professional business homepage for SportsBet Pro"""
    
    # Custom CSS for professional business site
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 60px 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .feature-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 5px solid #28a745;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .stats-container {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin: 30px 0;
    }
    
    .pricing-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        position: relative;
        transition: all 0.3s ease;
    }
    
    .pricing-card:hover {
        border-color: #007bff;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,123,255,0.2);
    }
    
    .popular-badge {
        background: #007bff;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        position: absolute;
        top: -10px;
        right: 20px;
        font-size: 12px;
    }
    
    .cta-button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 25px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
        margin: 10px;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,123,255,0.4);
    }
    
    .testimonial {
        background: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        border-left: 4px solid #ffc107;
        margin: 20px 0;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 3em; margin-bottom: 20px;">🏆 SportsBet Pro</h1>
        <h2 style="font-size: 1.5em; margin-bottom: 30px;">AI-Powered Sports Analysis & Prediction Platform</h2>
        <p style="font-size: 1.2em; margin-bottom: 40px;">
            Transform your sports betting with advanced AI insights, real-time odds analysis, 
            and professional-grade prediction algorithms used by industry professionals.
        </p>
        <div>
            <a href="#pricing" class="cta-button">Start Free Trial</a>
            <a href="#demo" class="cta-button" style="background: transparent; border: 2px solid white;">Watch Demo</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Live Statistics
    st.markdown("""
    <div class="stats-container">
        <h2 style="text-align: center; margin-bottom: 30px;">🔥 Live Platform Statistics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display real-time stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Users", "2,847", "+12%")
    with col2:
        st.metric("Games Analyzed", "156,742", "+8%")
    with col3:
        st.metric("Prediction Accuracy", "87.3%", "+2.1%")
    with col4:
        st.metric("Total Winnings", "$2.4M", "+15%")
    
    # Feature Highlights
    st.markdown("## 🚀 Why Choose SportsBet Pro?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 Dual AI Analysis</h3>
            <p>Get insights from both ChatGPT and Google Gemini with consensus analysis for maximum confidence in your betting decisions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Real-Time Odds</h3>
            <p>Access live betting odds from 300+ games across NFL, NBA, MLB, NHL, and WNBA with instant market analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ Lightning Fast</h3>
            <p>Advanced caching system delivers insights 70% faster than competitors with optimized data processing.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Winning Picks</h3>
            <p>Daily curated high-confidence picks with detailed analysis and risk assessment from our AI consensus system.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance Chart
    st.markdown("## 📈 Platform Performance")
    
    # Create sample performance data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    accuracy = [82.1, 83.5, 85.2, 84.8, 86.1, 87.3, 88.2, 86.9, 87.8, 88.5, 87.3, 89.1]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=accuracy,
        mode='lines+markers',
        name='Prediction Accuracy %',
        line=dict(color='#28a745', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="SportsBet Pro - 2024 Prediction Accuracy Trend",
        xaxis_title="Month",
        yaxis_title="Accuracy (%)",
        template="plotly_white",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Pricing Section
    st.markdown('<div id="pricing"></div>', unsafe_allow_html=True)
    st.markdown("## 💰 Choose Your Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>Starter</h3>
            <h2 style="color: #28a745;">$29/month</h2>
            <ul style="text-align: left; padding-left: 20px;">
                <li>Basic AI Analysis</li>
                <li>5 Daily Picks</li>
                <li>Email Support</li>
                <li>Basic Odds Data</li>
            </ul>
            <button class="cta-button" style="width: 100%;">Choose Starter</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pricing-card">
            <div class="popular-badge">Most Popular</div>
            <h3>Professional</h3>
            <h2 style="color: #007bff;">$79/month</h2>
            <ul style="text-align: left; padding-left: 20px;">
                <li>Dual AI Analysis</li>
                <li>Unlimited Daily Picks</li>
                <li>Priority Support</li>
                <li>Real-Time Odds</li>
                <li>Performance Tracking</li>
                <li>AI Chat Assistant</li>
            </ul>
            <button class="cta-button" style="width: 100%;">Choose Professional</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>Enterprise</h3>
            <h2 style="color: #6f42c1;">$199/month</h2>
            <ul style="text-align: left; padding-left: 20px;">
                <li>Everything in Professional</li>
                <li>API Access</li>
                <li>Custom Algorithms</li>
                <li>Dedicated Support</li>
                <li>Advanced Analytics</li>
                <li>White-label Options</li>
            </ul>
            <button class="cta-button" style="width: 100%;">Choose Enterprise</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Testimonials
    st.markdown("## 💬 What Our Clients Say")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="testimonial">
            <p>"SportsBet Pro increased my win rate from 52% to 78% in just 3 months. The AI analysis is incredibly accurate and the interface is so easy to use."</p>
            <strong>- Mike Johnson, Professional Bettor</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial">
            <p>"As a sports book operator, we use SportsBet Pro's enterprise solution for market analysis. It's revolutionized how we set our lines."</p>
            <strong>- Sarah Chen, Sportsbook Manager</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo Section
    st.markdown('<div id="demo"></div>', unsafe_allow_html=True)
    st.markdown("## 🎥 See SportsBet Pro in Action")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **🎬 Demo Features:**
        - Live AI analysis of current games
        - Real-time odds comparison
        - Winning picks generation
        - Interactive chat with AI experts
        - Performance tracking dashboard
        """)
    
    with col2:
        if st.button("▶️ Launch Demo", key="demo_btn", type="primary"):
            st.switch_page("pages/login.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 20px;">
        <p><strong>SportsBet Pro</strong> - Professional Sports Analysis Platform</p>
        <p>📧 support@sportsbetpro.com | 📞 1-800-SPORTSBET | 🌐 www.sportsbetpro.com</p>
        <p><em>© 2024 SportsBet Pro. All rights reserved. Bet responsibly.</em></p>
    </div>
    """, unsafe_allow_html=True)