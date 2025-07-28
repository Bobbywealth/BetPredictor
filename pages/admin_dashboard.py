import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def show_admin_dashboard():
    """Professional admin dashboard for SportsBet Pro"""
    
    # Check admin access
    if not st.session_state.get('is_admin', False):
        st.error("🚫 Access Denied: Admin privileges required")
        st.info("Please contact your system administrator for access.")
        return
    
    st.title("🔧 SportsBet Pro - Admin Dashboard")
    
    # Admin header
    st.success(f"👨‍💼 Welcome back, {st.session_state.get('username', 'Admin')}!")
    
    # Key metrics
    st.markdown("## 📊 Platform Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "2,847", "+127 this week", delta_color="normal")
    with col2:
        st.metric("Active Subscriptions", "1,956", "+89 this month", delta_color="normal")
    with col3:
        st.metric("Monthly Revenue", "$147,420", "+12.3%", delta_color="normal")
    with col4:
        st.metric("System Uptime", "99.97%", "Last 30 days", delta_color="normal")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Analytics", "👥 User Management", "💰 Revenue", "⚙️ System", "🎯 AI Performance"
    ])
    
    with tab1:
        show_analytics_section()
    
    with tab2:
        show_user_management()
    
    with tab3:
        show_revenue_section()
    
    with tab4:
        show_system_section()
    
    with tab5:
        show_ai_performance()

def show_analytics_section():
    """Analytics section for admin dashboard"""
    
    st.markdown("### 📊 User Analytics")
    
    # User growth chart
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    users = [2500 + i*10 + (i%7)*15 for i in range(len(dates))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=users, mode='lines+markers', name='Total Users'))
    fig.update_layout(title="User Growth - Last 30 Days", xaxis_title="Date", yaxis_title="Users")
    st.plotly_chart(fig, use_container_width=True)
    
    # Usage statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Most Popular Features")
        feature_data = {
            'Feature': ['AI Chat', 'Winning Picks', 'Live Odds', 'Performance Tracking', 'Deep Analysis'],
            'Usage %': [89, 76, 68, 54, 43]
        }
        fig = px.bar(feature_data, x='Feature', y='Usage %', title="Feature Usage Statistics")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### User Engagement")
        engagement_data = {
            'Metric': ['Daily Active Users', 'Weekly Active Users', 'Monthly Active Users'],
            'Count': [1847, 2456, 2847],
            'Percentage': [65, 86, 100]
        }
        df = pd.DataFrame(engagement_data)
        st.dataframe(df, use_container_width=True)

def show_user_management():
    """User management section"""
    
    st.markdown("### 👥 User Management")
    
    # User search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_user = st.text_input("🔍 Search Users", placeholder="Enter username or email")
    
    with col2:
        user_type_filter = st.selectbox("Filter by Type", ["All", "Free", "Starter", "Professional", "Enterprise"])
    
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Suspended", "Pending"])
    
    # Sample users data
    users_data = {
        'Username': ['mike_johnson', 'sarah_chen', 'alex_rodriguez', 'emma_wilson', 'david_lee'],
        'Email': ['mike@email.com', 'sarah@email.com', 'alex@email.com', 'emma@email.com', 'david@email.com'],
        'Plan': ['Professional', 'Enterprise', 'Starter', 'Professional', 'Free'],
        'Status': ['Active', 'Active', 'Active', 'Suspended', 'Active'],
        'Last Login': ['2024-07-28', '2024-07-27', '2024-07-28', '2024-07-25', '2024-07-26'],
        'Revenue': ['$79', '$199', '$29', '$79', '$0']
    }
    
    df = pd.DataFrame(users_data)
    st.dataframe(df, use_container_width=True)
    
    # User actions
    st.markdown("#### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📧 Send Notification", key="send_notification"):
            st.success("Notification sent to selected users!")
    
    with col2:
        if st.button("🔒 Suspend User", key="suspend_user"):
            st.warning("User suspension functionality activated")
    
    with col3:
        if st.button("💰 Update Billing", key="update_billing"):
            st.info("Billing update interface opened")
    
    with col4:
        if st.button("📊 Export Data", key="export_users"):
            st.success("User data exported successfully!")

def show_revenue_section():
    """Revenue and billing section"""
    
    st.markdown("### 💰 Revenue Analytics")
    
    # Revenue metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Monthly Recurring Revenue", "$147,420", "+$18,230")
    with col2:
        st.metric("Average Revenue Per User", "$75.36", "+$4.20")
    with col3:
        st.metric("Churn Rate", "2.3%", "-0.8%", delta_color="inverse")
    
    # Revenue by plan
    plan_revenue = {
        'Plan': ['Starter', 'Professional', 'Enterprise'],
        'Subscribers': [456, 1234, 266],
        'Monthly Revenue': ['$13,224', '$97,486', '$52,834']
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Revenue by Plan")
        df = pd.DataFrame(plan_revenue)
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.markdown("#### Revenue Trend")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
        revenue = [98000, 112000, 125000, 134000, 142000, 147000, 147420]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=revenue, mode='lines+markers', name='Revenue'))
        fig.update_layout(title="Monthly Revenue Growth")
        st.plotly_chart(fig, use_container_width=True)

def show_system_section():
    """System monitoring section"""
    
    st.markdown("### ⚙️ System Status")
    
    # System health
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Server Uptime", "99.97%", "30 days")
    with col2:
        st.metric("API Response Time", "127ms", "-23ms")
    with col3:
        st.metric("Database Load", "34%", "+2%")
    with col4:
        st.metric("Cache Hit Rate", "94.2%", "+1.8%")
    
    # System alerts
    st.markdown("#### Recent System Events")
    
    alerts_data = {
        'Timestamp': ['2024-07-28 10:15', '2024-07-28 09:42', '2024-07-27 23:18'],
        'Type': ['Info', 'Warning', 'Info'],
        'Message': [
            'Database backup completed successfully',
            'High CPU usage detected on server-02',
            'System maintenance completed'
        ],
        'Status': ['Resolved', 'Monitoring', 'Resolved']
    }
    
    df = pd.DataFrame(alerts_data)
    st.dataframe(df, use_container_width=True)
    
    # System controls
    st.markdown("#### System Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Restart Services", key="restart_services"):
            st.warning("Service restart initiated...")
    
    with col2:
        if st.button("💾 Backup Database", key="backup_db"):
            st.success("Database backup started")
    
    with col3:
        if st.button("🧹 Clear Cache", key="clear_cache"):
            st.info("System cache cleared")

def show_ai_performance():
    """AI performance monitoring"""
    
    st.markdown("### 🎯 AI Performance Metrics")
    
    # AI accuracy metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Accuracy", "87.3%", "+2.1%")
    with col2:
        st.metric("ChatGPT Accuracy", "86.8%", "+1.9%")
    with col3:
        st.metric("Gemini Accuracy", "87.9%", "+2.3%")
    
    # AI usage statistics
    ai_stats = {
        'AI Model': ['ChatGPT', 'Gemini', 'Consensus'],
        'Requests Today': [1247, 1156, 892],
        'Average Response Time': ['1.2s', '0.9s', '2.1s'],
        'Success Rate': ['98.2%', '97.8%', '99.1%']
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### AI Usage Statistics")
        df = pd.DataFrame(ai_stats)
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.markdown("#### Model Performance")
        models = ['ChatGPT', 'Gemini', 'Consensus']
        accuracy = [86.8, 87.9, 91.2]
        
        fig = px.bar(x=models, y=accuracy, title="AI Model Accuracy Comparison")
        st.plotly_chart(fig, use_container_width=True)
    
    # AI model controls
    st.markdown("#### AI Model Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retrain Models", key="retrain_models"):
            st.success("Model retraining scheduled")
    
    with col2:
        if st.button("📊 Generate Report", key="ai_report"):
            st.info("AI performance report generated")
    
    with col3:
        if st.button("⚙️ Model Settings", key="model_settings"):
            st.info("Model configuration panel opened")