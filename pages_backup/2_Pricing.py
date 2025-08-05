import streamlit as st
from datetime import datetime

def main():
    st.set_page_config(
        page_title="SportsBet Pro - Pricing",
        page_icon="💰",
        layout="wide"
    )
    
    # Back navigation
    if st.button("← Back to Home", key="back_home"):
        st.switch_page("pages/landing.py")
    
    st.title("💰 Choose Your Plan")
    st.markdown("### Unlock the power of AI-driven sports predictions")
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; text-align: center;">
            <h3>🥉 Basic</h3>
            <h2>$29/month</h2>
            <hr>
            <p>✅ 5 predictions per day</p>
            <p>✅ Basic analytics</p>
            <p>✅ Email alerts</p>
            <p>❌ SMS alerts</p>
            <p>❌ Advanced stats</p>
            <p>❌ API access</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Choose Basic", key="basic", type="secondary"):
            handle_subscription("basic", 29)
    
    with col2:
        st.markdown("""
        <div style="border: 3px solid #4CAF50; border-radius: 10px; padding: 20px; text-align: center; background-color: #f8fff8;">
            <h3>🥈 Pro</h3>
            <h2>$79/month</h2>
            <p style="color: #4CAF50; font-weight: bold;">MOST POPULAR</p>
            <hr>
            <p>✅ Unlimited predictions</p>
            <p>✅ Advanced analytics</p>
            <p>✅ Email & SMS alerts</p>
            <p>✅ Real-time data</p>
            <p>✅ Betting recommendations</p>
            <p>❌ API access</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Choose Pro", key="pro", type="primary"):
            handle_subscription("pro", 79)
    
    with col3:
        st.markdown("""
        <div style="border: 2px solid #FFD700; border-radius: 10px; padding: 20px; text-align: center; background-color: #fffef0;">
            <h3>🥇 Enterprise</h3>
            <h2>$199/month</h2>
            <hr>
            <p>✅ Everything in Pro</p>
            <p>✅ API access</p>
            <p>✅ Custom integrations</p>
            <p>✅ White-label options</p>
            <p>✅ Priority support</p>
            <p>✅ Custom models</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Choose Enterprise", key="enterprise", type="secondary"):
            handle_subscription("enterprise", 199)
    
    st.divider()
    
    # Features comparison table
    st.subheader("📋 Feature Comparison")
    
    features_data = {
        'Feature': [
            'Daily Predictions',
            'Sports Covered',
            'Real-time Data',
            'Advanced Analytics',
            'Email Alerts',
            'SMS Alerts',
            'API Access',
            'Custom Models',
            'Priority Support',
            'Money-back Guarantee'
        ],
        'Basic': [
            '5 per day',
            '3 sports',
            '❌',
            '❌',
            '✅',
            '❌',
            '❌',
            '❌',
            '❌',
            '30 days'
        ],
        'Pro': [
            'Unlimited',
            '10+ sports',
            '✅',
            '✅',
            '✅',
            '✅',
            '❌',
            '❌',
            '✅',
            '30 days'
        ],
        'Enterprise': [
            'Unlimited',
            'All sports',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '✅',
            '60 days'
        ]
    }
    
    import pandas as pd
    df = pd.DataFrame(features_data)
    st.dataframe(df, use_container_width=True)
    
    # FAQ Section
    st.subheader("❓ Frequently Asked Questions")
    
    with st.expander("How accurate are your predictions?"):
        st.write("Our AI models achieve 73-78% accuracy across different sports, with performance varying by league and market conditions.")
    
    with st.expander("Can I cancel anytime?"):
        st.write("Yes! You can cancel your subscription at any time. No long-term contracts or hidden fees.")
    
    with st.expander("Do you offer refunds?"):
        st.write("We offer a 30-day money-back guarantee for Basic and Pro plans, and 60 days for Enterprise.")
    
    with st.expander("What payment methods do you accept?"):
        st.write("We accept all major credit cards, PayPal, and ACH transfers for Enterprise accounts.")
    
    # Testimonials
    st.subheader("💬 What Our Customers Say")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px;">
            <p><em>"Increased my betting ROI by 40% in the first month!"</em></p>
            <p><strong>- Mike T., Pro User</strong></p>
            <p>⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px;">
            <p><em>"The most accurate predictions I've ever used."</em></p>
            <p><strong>- Sarah L., Enterprise User</strong></p>
            <p>⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px;">
            <p><em>"Customer support is fantastic. Highly recommended!"</em></p>
            <p><strong>- James R., Pro User</strong></p>
            <p>⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)

def handle_subscription(plan, price):
    """Handle subscription selection"""
    st.session_state.selected_plan = plan
    st.session_state.selected_price = price
    
    st.success(f"Selected {plan.title()} plan (${price}/month)")
    st.info("In a real application, this would redirect to Stripe checkout.")
    
    # Demo subscription activation
    if st.button("Activate Demo Subscription", key=f"activate_{plan}"):
        st.session_state.subscription_active = True
        st.session_state.subscription_plan = plan
        st.success("Demo subscription activated! You now have access to all features.")
        st.balloons()

if __name__ == "__main__":
    main()