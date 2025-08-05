import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_customer_portal():
    """Professional customer portal for SportsBet Pro"""
    
    # Check customer authentication
    if not st.session_state.get('is_authenticated', False):
        st.error("🔐 Please log in to access your customer portal")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        return
    
    # Customer welcome
    username = st.session_state.get('username', 'Customer')
    st.title(f"🏆 Welcome back, {username}!")
    
    # Account status
    account_type = st.session_state.get('account_type', 'Free')
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Account Plan", account_type)
    with col2:
        st.metric("Days Remaining", "23" if account_type != 'Free' else "∞")
    with col3:
        st.metric("Predictions Used", "47/100" if account_type != 'Enterprise' else "Unlimited")
    with col4:
        st.metric("Win Rate", "73.2%")
    
    # Customer navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 My Analysis", "📊 My Performance", "💰 Billing", "⚙️ Settings", "🎓 Learning"
    ])
    
    with tab1:
        show_my_analysis()
    
    with tab2:
        show_my_performance()
    
    with tab3:
        show_billing_section()
    
    with tab4:
        show_account_settings()
    
    with tab5:
        show_learning_center()

def show_my_analysis():
    """Customer's personalized analysis section"""
    
    st.markdown("### 🎯 Your Personalized Sports Analysis")
    
    # Quick access to main features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤖 AI Chat Assistant", key="portal_ai_chat", use_container_width=True):
            st.switch_page("pages/ai_chat.py")
    
    with col2:
        if st.button("🏆 Today's Picks", key="portal_picks", use_container_width=True):
            st.switch_page("pages/winning_picks.py")
    
    with col3:
        if st.button("💰 Live Odds", key="portal_odds", use_container_width=True):
            st.switch_page("pages/live_odds.py")
    
    st.divider()
    
    # Recent activity
    st.markdown("#### 📋 Your Recent Activity")
    
    recent_activity = {
        'Date': ['2024-07-28', '2024-07-27', '2024-07-26', '2024-07-25'],
        'Action': ['AI Chat Session', 'Viewed Picks', 'Performance Review', 'Odds Analysis'],
        'Details': [
            'Discussed NFL Week 4 strategies',
            'Reviewed 5 high-confidence picks',
            'Analyzed monthly performance',
            'Compared MLB odds across books'
        ],
        'Result': ['Completed', 'Completed', 'Completed', 'Completed']
    }
    
    df = pd.DataFrame(recent_activity)
    st.dataframe(df, use_container_width=True)
    
    # Personalized recommendations
    st.markdown("#### 💡 Personalized Recommendations")
    
    recommendations = [
        "🏈 Consider betting on Cowboys +3.5 based on your preference for underdogs",
        "⚾ MLB totals have been profitable for you - check today's over/under picks",
        "🏀 Your NBA win rate improves with home favorites - focus on tonight's games",
        "🎯 Try the AI consensus feature for higher confidence picks"
    ]
    
    for rec in recommendations:
        st.info(rec)

def show_my_performance():
    """Customer performance tracking"""
    
    st.markdown("### 📊 Your Betting Performance")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bets", "156", "+12 this week")
    with col2:
        st.metric("Win Rate", "73.2%", "+2.8%")
    with col3:
        st.metric("ROI", "+24.7%", "+3.2%")
    with col4:
        st.metric("Profit", "$1,847", "+$284")
    
    # Performance chart
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    profits = [100 + i*15 + (i%5)*20 for i in range(len(dates))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=profits,
        mode='lines+markers',
        name='Cumulative Profit',
        line=dict(color='#28a745', width=3)
    ))
    
    fig.update_layout(
        title="Your 30-Day Profit Trend",
        xaxis_title="Date",
        yaxis_title="Profit ($)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance by sport
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Performance by Sport")
        sport_performance = {
            'Sport': ['NFL', 'NBA', 'MLB', 'NHL'],
            'Bets': [45, 38, 42, 31],
            'Win Rate': ['78%', '71%', '69%', '74%'],
            'ROI': ['+32%', '+18%', '+21%', '+28%']
        }
        df = pd.DataFrame(sport_performance)
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.markdown("#### Best Performing Strategies")
        strategies = [
            "Home Underdogs: 82% win rate",
            "Over/Under Totals: 76% win rate", 
            "AI Consensus Picks: 91% win rate",
            "Live Betting: 68% win rate"
        ]
        for strategy in strategies:
            st.success(strategy)

def show_billing_section():
    """Customer billing and subscription management"""
    
    st.markdown("### 💰 Billing & Subscription")
    
    # Current plan
    account_type = st.session_state.get('account_type', 'Free')
    
    st.markdown(f"#### Current Plan: **{account_type}**")
    
    if account_type == 'Free':
        st.info("You're currently on our Free plan. Upgrade for more features!")
    else:
        st.success(f"You're subscribed to {account_type} plan")
    
    # Billing information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Plan Details")
        if account_type == 'Professional':
            st.write("- Dual AI Analysis ✅")
            st.write("- Unlimited Daily Picks ✅")
            st.write("- Real-Time Odds ✅")
            st.write("- AI Chat Assistant ✅")
            st.write("- Performance Tracking ✅")
            st.write("- Next billing: August 28, 2024")
            st.write("- Amount: $79.00")
    
    with col2:
        st.markdown("#### Usage This Month")
        st.metric("AI Chat Sessions", "47")
        st.metric("Picks Generated", "156")
        st.metric("Odds Queries", "1,247")
        st.metric("Analysis Reports", "23")
    
    # Plan upgrade options
    st.markdown("#### 🚀 Upgrade Your Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Starter** - $29/month
        - Basic AI Analysis
        - 5 Daily Picks
        - Email Support
        """)
        if st.button("Select Starter", key="upgrade_starter"):
            st.success("Upgrade to Starter initiated!")
    
    with col2:
        st.markdown("""
        **Professional** - $79/month
        - Everything in Starter
        - Dual AI Analysis
        - Unlimited Picks
        - AI Chat Assistant
        """)
        if account_type != 'Professional':
            if st.button("Select Professional", key="upgrade_pro"):
                st.success("Upgrade to Professional initiated!")
        else:
            st.info("Current Plan")
    
    with col3:
        st.markdown("""
        **Enterprise** - $199/month
        - Everything in Professional
        - API Access
        - Custom Algorithms
        - Priority Support
        """)
        if st.button("Select Enterprise", key="upgrade_enterprise"):
            st.success("Upgrade to Enterprise initiated!")

def show_account_settings():
    """Customer account settings"""
    
    st.markdown("### ⚙️ Account Settings")
    
    # Profile settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Profile Information")
        st.text_input("Username", value=st.session_state.get('username', ''), key="profile_username")
        st.text_input("Email", value="user@example.com", key="profile_email")
        st.text_input("Phone", value="+1 (555) 123-4567", key="profile_phone")
        
        if st.button("Update Profile", key="update_profile"):
            st.success("Profile updated successfully!")
    
    with col2:
        st.markdown("#### Notification Preferences")
        st.checkbox("Email notifications for new picks", value=True, key="notify_picks")
        st.checkbox("SMS alerts for high-confidence bets", value=False, key="notify_sms")
        st.checkbox("Weekly performance reports", value=True, key="notify_reports")
        st.checkbox("Marketing communications", value=False, key="notify_marketing")
        
        if st.button("Save Preferences", key="save_notifications"):
            st.success("Notification preferences saved!")
    
    # Security settings
    st.markdown("#### 🔐 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Change Password", key="change_password"):
            st.info("Password change form would appear here")
    
    with col2:
        if st.button("Enable 2FA", key="enable_2fa"):
            st.info("Two-factor authentication setup initiated")
    
    # Account actions
    st.markdown("#### Account Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Data", key="download_data"):
            st.success("Your data export has been queued")
    
    with col2:
        if st.button("Pause Subscription", key="pause_sub"):
            st.warning("Subscription pause initiated")
    
    with col3:
        if st.button("Delete Account", key="delete_account"):
            st.error("Account deletion request submitted")

def show_learning_center():
    """Educational content for customers"""
    
    st.markdown("### 🎓 Learning Center")
    
    # Learning modules
    st.markdown("#### 📚 Educational Modules")
    
    modules = [
        {
            'title': '🏈 NFL Betting Fundamentals',
            'description': 'Learn the basics of NFL point spreads, totals, and moneylines',
            'duration': '15 minutes',
            'completed': True
        },
        {
            'title': '📊 Understanding Betting Odds',
            'description': 'Master American, decimal, and fractional odds formats',
            'duration': '10 minutes',
            'completed': True
        },
        {
            'title': '🤖 AI Analysis Interpretation',
            'description': 'How to read and act on AI-generated betting insights',
            'duration': '20 minutes',
            'completed': False
        },
        {
            'title': '💰 Bankroll Management',
            'description': 'Essential strategies for managing your betting funds',
            'duration': '25 minutes',
            'completed': False
        }
    ]
    
    for module in modules:
        status = "✅ Completed" if module['completed'] else "📖 Start Learning"
        color = "success" if module['completed'] else "info"
        
        with st.expander(f"{module['title']} - {module['duration']}"):
            st.write(module['description'])
            if st.button(status, key=f"module_{module['title']}", type="primary" if not module['completed'] else "secondary"):
                if not module['completed']:
                    st.success(f"Started: {module['title']}")
                else:
                    st.info("Module already completed!")
    
    # Recent articles
    st.markdown("#### 📰 Recent Articles")
    
    articles = [
        "How to Identify Value Bets Using AI Analysis",
        "Week 4 NFL Betting Trends and Insights", 
        "The Psychology of Sports Betting: Avoiding Common Mistakes",
        "Live Betting Strategies for Basketball"
    ]
    
    for article in articles:
        if st.button(f"📖 {article}", key=f"article_{article}"):
            st.info(f"Opening: {article}")
    
    # Responsible gambling
    st.markdown("#### ⚠️ Responsible Gambling Resources")
    st.warning("""
    **Remember:** Sports betting should be fun and recreational. Never bet more than you can afford to lose.
    
    - Set daily/weekly betting limits
    - Take regular breaks from betting
    - Seek help if gambling becomes problematic
    
    **Resources:**
    - National Problem Gambling Helpline: 1-800-522-4700
    - Gamblers Anonymous: www.gamblersanonymous.org
    """)