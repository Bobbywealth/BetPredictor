import streamlit as st
import json

def main():
    st.set_page_config(
        page_title="SportsBet Pro - API Documentation",
        page_icon="🔧",
        layout="wide"
    )
    
    # Check if user has API access
    if not st.session_state.get('subscription_active') or st.session_state.get('subscription_plan') != 'enterprise':
        st.error("🔒 API Access - Enterprise Subscription Required")
        st.info("Upgrade to Enterprise to access our powerful REST API.")
        if st.button("View Pricing"):
            st.switch_page("pages/2_Pricing.py")
        return
    
    st.title("🔧 SportsBet Pro API Documentation")
    st.markdown("### Enterprise REST API for developers")
    
    # API Overview
    st.subheader("📋 Overview")
    st.markdown("""
    The SportsBet Pro API provides programmatic access to:
    - Real-time sports predictions
    - Historical performance data
    - Live game information
    - Betting recommendations
    - Analytics and statistics
    """)
    
    # Authentication
    st.subheader("🔐 Authentication")
    st.code("""
# All API requests require your API key in the header
headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
    """, language='python')
    
    # Base URL
    st.markdown("**Base URL:** `https://api.sportsbetpro.com/v1`")
    
    # API Key Management
    st.subheader("🗝️ API Key Management")
    
    if 'api_key' not in st.session_state:
        if st.button("Generate API Key"):
            import secrets
            st.session_state.api_key = f"sbp_{secrets.token_urlsafe(32)}"
            st.success("API Key generated!")
    
    if 'api_key' in st.session_state:
        st.code(st.session_state.api_key, language='text')
        st.warning("Keep your API key secure! Do not share it publicly.")
    
    st.divider()
    
    # Endpoints Documentation
    st.subheader("🛠️ API Endpoints")
    
    # Predictions Endpoint
    with st.expander("📊 GET /predictions - Get Predictions"):
        st.markdown("""
        **Description:** Retrieve AI-generated predictions for upcoming games.
        
        **Parameters:**
        - `sport` (optional): Filter by sport (soccer, basketball, baseball)
        - `date` (optional): Filter by date (YYYY-MM-DD)
        - `confidence_min` (optional): Minimum confidence threshold (0-100)
        """)
        
        st.code("""
# Example Request
curl -X GET "https://api.sportsbetpro.com/v1/predictions?sport=basketball&confidence_min=80" \\
     -H "Authorization: Bearer YOUR_API_KEY"
        """, language='bash')
        
        st.code("""
# Example Response
{
  "predictions": [
    {
      "id": "pred_123",
      "game_id": "nba_lal_vs_gsw_20250727",
      "sport": "basketball",
      "home_team": "Golden State Warriors",
      "away_team": "Los Angeles Lakers",
      "prediction_type": "spread",
      "prediction": "Lakers +5.5",
      "confidence": 87.3,
      "expected_value": 1.12,
      "created_at": "2025-07-27T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1
}
        """, language='json')
    
    # Live Games Endpoint
    with st.expander("🏟️ GET /games/live - Get Live Games"):
        st.markdown("""
        **Description:** Get real-time information about live and upcoming games.
        
        **Parameters:**
        - `sport` (optional): Filter by sport
        - `status` (optional): Filter by status (live, upcoming, finished)
        """)
        
        st.code("""
# Example Request
curl -X GET "https://api.sportsbetpro.com/v1/games/live?sport=soccer&status=live" \\
     -H "Authorization: Bearer YOUR_API_KEY"
        """, language='bash')
        
        st.code("""
# Example Response
{
  "games": [
    {
      "game_id": "epl_che_vs_ars_20250727",
      "sport": "soccer",
      "league": "Premier League",
      "home_team": {
        "name": "Arsenal",
        "score": 1
      },
      "away_team": {
        "name": "Chelsea", 
        "score": 2
      },
      "status": "live",
      "period": "87'",
      "venue": {
        "name": "Emirates Stadium",
        "city": "London"
      }
    }
  ]
}
        """, language='json')
    
    # Analytics Endpoint
    with st.expander("📈 GET /analytics - Get Performance Analytics"):
        st.markdown("""
        **Description:** Retrieve historical performance and analytics data.
        
        **Parameters:**
        - `start_date` (required): Start date (YYYY-MM-DD)
        - `end_date` (required): End date (YYYY-MM-DD)
        - `metric` (optional): Specific metric (win_rate, roi, units)
        """)
        
        st.code("""
# Example Response
{
  "analytics": {
    "period": {
      "start": "2025-06-01",
      "end": "2025-07-27"
    },
    "metrics": {
      "total_predictions": 156,
      "win_rate": 73.5,
      "roi": 24.8,
      "units_won": 18.5,
      "avg_confidence": 81.2
    },
    "daily_performance": [
      {
        "date": "2025-07-27",
        "predictions": 5,
        "wins": 4,
        "units": 2.3
      }
    ]
  }
}
        """, language='json')
    
    # Webhooks
    st.subheader("🔗 Webhooks")
    st.markdown("""
    Configure webhooks to receive real-time notifications when:
    - New predictions are generated
    - Game results are updated
    - Prediction outcomes are determined
    """)
    
    with st.expander("⚙️ Configure Webhooks"):
        webhook_url = st.text_input("Webhook URL", placeholder="https://your-app.com/webhook")
        
        events = st.multiselect(
            "Select Events",
            ["prediction.created", "game.updated", "prediction.settled"],
            default=["prediction.created"]
        )
        
        if st.button("Save Webhook Configuration"):
            st.success("Webhook configured successfully!")
            st.json({
                "webhook_id": "wh_123456",
                "url": webhook_url,
                "events": events,
                "status": "active"
            })
    
    # Rate Limits
    st.subheader("⚡ Rate Limits")
    st.markdown("""
    **Enterprise Plan Limits:**
    - 10,000 requests per hour
    - 100,000 requests per day
    - No concurrent request limits
    
    **Rate limit headers included in responses:**
    - `X-RateLimit-Limit`: Requests allowed per window
    - `X-RateLimit-Remaining`: Requests remaining in window
    - `X-RateLimit-Reset`: UTC timestamp when window resets
    """)
    
    # SDKs
    st.subheader("📚 SDKs and Libraries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Python SDK**")
        st.code("""
pip install sportsbetpro-python

from sportsbetpro import Client

client = Client(api_key="YOUR_API_KEY")
predictions = client.predictions.list(sport="basketball")
        """, language='python')
    
    with col2:
        st.markdown("**JavaScript SDK**")
        st.code("""
npm install sportsbetpro-js

import { SportsBetPro } from 'sportsbetpro-js';

const client = new SportsBetPro('YOUR_API_KEY');
const predictions = await client.predictions.list({
  sport: 'basketball'
});
        """, language='javascript')
    
    # Support
    st.subheader("💬 API Support")
    st.markdown("""
    **Enterprise Support Channels:**
    - 📧 Email: api-support@sportsbetpro.com
    - 💬 Slack: #enterprise-api-support
    - 📞 Phone: +1 (555) 123-4567
    - 🎫 Priority ticket system
    
    **Response Times:**
    - Critical issues: < 1 hour
    - General inquiries: < 4 hours
    """)

if __name__ == "__main__":
    main()