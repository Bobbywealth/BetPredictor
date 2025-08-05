import streamlit as st
from datetime import datetime

def main():
    st.set_page_config(
        page_title="SportsBet Pro - Support",
        page_icon="🆘",
        layout="wide"
    )
    
    st.title("🆘 Support Center")
    st.markdown("### Get help with SportsBet Pro")
    
    # Quick Actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Submit Ticket", use_container_width=True):
            st.session_state.show_ticket_form = True
    
    with col2:
        if st.button("💬 Live Chat", use_container_width=True):
            st.info("Live chat opening...")
    
    with col3:
        if st.button("📞 Schedule Call", use_container_width=True):
            st.info("Redirecting to calendar...")
    
    with col4:
        if st.button("📚 Documentation", use_container_width=True):
            st.switch_page("pages/3_API_Documentation.py")
    
    st.divider()
    
    # Support Ticket Form
    if st.session_state.get('show_ticket_form', False):
        st.subheader("📝 Submit Support Ticket")
        
        with st.form("support_ticket"):
            col1, col2 = st.columns(2)
            
            with col1:
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                category = st.selectbox("Category", [
                    "Technical Issue",
                    "Billing Question", 
                    "Feature Request",
                    "API Issue",
                    "Account Problem",
                    "General Question"
                ])
            
            with col2:
                subject = st.text_input("Subject")
                email = st.text_input("Your Email", value=st.session_state.get('user_profile', {}).get('email', ''))
            
            description = st.text_area("Description", height=150, 
                                     placeholder="Please describe your issue in detail...")
            
            # File upload
            uploaded_file = st.file_uploader("Attach File (optional)", 
                                           type=['png', 'jpg', 'pdf', 'txt', 'log'])
            
            if st.form_submit_button("Submit Ticket"):
                if subject and description:
                    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    st.success(f"Ticket submitted successfully! Ticket ID: {ticket_id}")
                    st.info("You'll receive an email confirmation shortly.")
                    st.session_state.show_ticket_form = False
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")
    
    # FAQ Section
    st.subheader("❓ Frequently Asked Questions")
    
    faqs = {
        "How do I upgrade my subscription?": {
            "answer": "Go to the Pricing page and select your desired plan. You can upgrade instantly with any major credit card.",
            "category": "Billing"
        },
        "Why are my predictions not showing?": {
            "answer": "Check your subscription status and internet connection. Predictions are generated daily at 6 AM EST.",
            "category": "Technical"
        },
        "How accurate are the predictions?": {
            "answer": "Our AI models achieve 73-78% accuracy across different sports, with performance varying by league and market conditions.",
            "category": "General"
        },
        "Can I get a refund?": {
            "answer": "Yes! We offer a 30-day money-back guarantee for Basic and Pro plans, and 60 days for Enterprise.",
            "category": "Billing"
        },
        "How do I cancel my subscription?": {
            "answer": "Go to Account > Subscription Details and click 'Cancel Subscription'. You can also contact support.",
            "category": "Billing"
        },
        "What sports do you cover?": {
            "answer": "We cover NBA, NFL, MLB, NHL, Premier League, La Liga, Champions League, and many more. Enterprise users get access to all sports.",
            "category": "General"
        }
    }
    
    # FAQ Search
    search_term = st.text_input("🔍 Search FAQs", placeholder="Type your question...")
    
    # FAQ Categories
    category_filter = st.selectbox("Filter by Category", 
                                 ["All", "General", "Technical", "Billing", "API"])
    
    # Display FAQs
    for question, details in faqs.items():
        if category_filter == "All" or details["category"] == category_filter:
            if not search_term or search_term.lower() in question.lower():
                with st.expander(f"📌 {question}"):
                    st.write(details['answer'])
                    st.caption(f"Category: {details['category']}")
    
    st.divider()
    
    # Contact Information
    st.subheader("📞 Contact Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📧 Email Support**
        - General: support@sportsbetpro.com
        - Technical: tech@sportsbetpro.com
        - Billing: billing@sportsbetpro.com
        - API: api@sportsbetpro.com
        """)
    
    with col2:
        st.markdown("""
        **📞 Phone Support**
        - US/Canada: +1 (555) 123-4567
        - UK: +44 20 7123 4567
        - Hours: 24/7 for Enterprise
        - Basic/Pro: Mon-Fri 9AM-6PM EST
        """)
    
    with col3:
        st.markdown("""
        **💬 Live Chat**
        - Available in app (bottom right)
        - Enterprise: 24/7 priority
        - Pro: Mon-Fri 9AM-9PM EST
        - Basic: Mon-Fri 9AM-6PM EST
        """)
    
    # Response Times
    st.subheader("⏱️ Response Times")
    
    response_data = {
        'Plan': ['Basic', 'Pro', 'Enterprise'],
        'Email': ['24-48 hours', '12-24 hours', '< 4 hours'],
        'Live Chat': ['Next business day', '< 2 hours', '< 30 minutes'],
        'Phone': ['Not available', 'By appointment', '24/7 priority'],
        'Critical Issues': ['Next business day', '< 4 hours', '< 1 hour']
    }
    
    import pandas as pd
    df = pd.DataFrame(response_data)
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # System Status
    st.subheader("🟢 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Core Services**
        - 🟢 API: Operational
        - 🟢 Predictions: Operational  
        - 🟢 Live Data: Operational
        - 🟢 Website: Operational
        """)
    
    with col2:
        st.markdown("""
        **External Services**
        - 🟢 ESPN API: Operational
        - 🟢 TheSportsDB: Operational
        - 🟡 SMS Service: Degraded
        - 🟢 Email Service: Operational
        """)
    
    if st.button("View Detailed Status Page"):
        st.info("Opening status.sportsbetpro.com...")
    
    # Knowledge Base
    st.subheader("📚 Knowledge Base")
    
    kb_categories = {
        "Getting Started": [
            "Setting up your account",
            "Understanding predictions",
            "Reading confidence scores",
            "First time betting guide"
        ],
        "Advanced Features": [
            "API integration guide",
            "Custom model training", 
            "Webhook configuration",
            "Data export options"
        ],
        "Troubleshooting": [
            "Login issues",
            "Payment problems",
            "Missing predictions",
            "API errors"
        ]
    }
    
    for category, articles in kb_categories.items():
        with st.expander(f"📂 {category}"):
            for article in articles:
                st.markdown(f"• [{article}](#)")
    
    # Feedback
    st.divider()
    st.subheader("💭 Feedback")
    
    feedback_type = st.radio("Feedback Type", 
                           ["Feature Request", "Bug Report", "General Feedback"])
    
    feedback_text = st.text_area("Your Feedback", 
                                placeholder="Help us improve SportsBet Pro...")
    
    if st.button("Submit Feedback"):
        if feedback_text:
            st.success("Thank you for your feedback! We review all submissions.")
        else:
            st.error("Please enter your feedback.")

if __name__ == "__main__":
    main()