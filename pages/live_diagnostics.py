"""
Live Diagnostics Page - Debug production issues
"""

import streamlit as st
import os
from datetime import datetime, date
import sys

def show_live_diagnostics():
    """Show live diagnostics for production debugging"""
    
    st.title("🔧 Live System Diagnostics")
    st.markdown("**Real-time debugging for production issues**")
    
    # Warning about sensitive info
    st.warning("⚠️ **Admin Only**: This page shows system configuration. Do not share screenshots.")
    
    # Basic system info
    st.markdown("## 📊 System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    with col2:
        st.metric("Streamlit Version", st.__version__)
    
    with col3:
        st.metric("Current Time", datetime.now().strftime("%H:%M:%S"))
    
    # Environment Variables Check
    st.markdown("## 🔑 Environment Variables Status")
    
    # Database credentials
    st.markdown("### 🗄️ Database Configuration")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if supabase_url:
            st.success(f"✅ SUPABASE_URL: {supabase_url[:30]}...{supabase_url[-15:]}")
        else:
            st.error("❌ SUPABASE_URL: Not configured")
    
    with col2:
        if supabase_key:
            st.success(f"✅ SUPABASE_ANON_KEY: {supabase_key[:15]}...{supabase_key[-15:]}")
        else:
            st.error("❌ SUPABASE_ANON_KEY: Not configured")
    
    # AI API Keys
    st.markdown("### 🤖 AI API Configuration")
    openai_key = os.environ.get("OPENAI_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    odds_key = os.environ.get("ODDS_API_KEY")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if openai_key:
            st.success(f"✅ OpenAI: sk-...{openai_key[-8:]}")
        else:
            st.error("❌ OpenAI: Not configured")
    
    with col2:
        if google_key:
            st.success(f"✅ Gemini: ...{google_key[-8:]}")
        else:
            st.error("❌ Gemini: Not configured")
    
    with col3:
        if odds_key:
            st.success(f"✅ Odds API: ...{odds_key[-8:]}")
        else:
            st.error("❌ Odds API: Not configured")
    
    # Live Connection Tests
    st.markdown("## 🧪 Live Connection Tests")
    
    # Test Database Connection
    st.markdown("### 📡 Database Connection Test")
    
    if st.button("🔍 Test Database Connection", type="primary"):
        if supabase_url and supabase_key:
            try:
                from supabase import create_client, Client
                
                with st.spinner("Testing database connection..."):
                    supabase: Client = create_client(supabase_url, supabase_key)
                    
                    # Test basic connection
                    result = supabase.table('users').select("count", count='exact').execute()
                    st.success(f"✅ Database Connected! Users table has {result.count} records")
                    
                    # Test other tables
                    pred_result = supabase.table('predictions').select("count", count='exact').execute()
                    st.info(f"📊 Predictions: {pred_result.count} records")
                    
                    api_result = supabase.table('api_usage').select("count", count='exact').execute()
                    st.info(f"💰 API Usage: {api_result.count} records")
                    
                    # Test insert capability
                    test_record = {
                        "provider": "Test Connection",
                        "tokens_used": 1,
                        "cost": 0.001,
                        "success": True
                    }
                    
                    insert_result = supabase.table('api_usage').insert(test_record).execute()
                    st.success("✅ Database write test successful")
                    
                    # Clean up test record
                    supabase.table('api_usage').delete().eq('provider', 'Test Connection').execute()
                    st.info("🧹 Test record cleaned up")
                    
            except Exception as e:
                st.error(f"❌ Database connection failed: {str(e)}")
        else:
            st.error("❌ Cannot test - database credentials not configured")
    
    # Test AI APIs
    st.markdown("### 🤖 AI API Test")
    
    if st.button("🧠 Test AI Predictions", type="secondary"):
        if openai_key or google_key:
            try:
                # Import the AI function
                sys.path.append('.')
                from app import get_ai_analysis
                
                # Create test game
                test_game = {
                    'home_team': 'Miami Marlins',
                    'away_team': 'Houston Astros',
                    'sport': 'MLB',
                    'league': 'MLB',
                    'game_date': date.today(),
                    'time': '7:00 PM'
                }
                
                with st.spinner("Testing AI prediction..."):
                    analysis = get_ai_analysis(test_game)
                    
                    if analysis:
                        st.success("✅ AI Analysis is working!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Predicted Winner", analysis.get('predicted_winner', 'Unknown'))
                        with col2:
                            confidence = analysis.get('confidence', 0)
                            st.metric("Confidence", f"{confidence:.1%}")
                        with col3:
                            st.metric("AI Provider", analysis.get('provider', 'Unknown'))
                        
                        # Show analysis details
                        if 'reasoning' in analysis:
                            st.info(f"📝 Analysis: {analysis['reasoning'][:200]}...")
                            
                    else:
                        st.error("❌ AI Analysis returned None - check API keys or function")
                        
            except Exception as e:
                st.error(f"❌ AI test failed: {str(e)}")
                st.code(str(e))
        else:
            st.error("❌ Cannot test - no AI API keys configured")
    
    # Mock Data Detection
    st.markdown("### 🎭 Mock Data Detection")
    
    if st.button("🔍 Check for Mock Data", type="secondary"):
        try:
            sys.path.append('.')
            from app import get_games_for_date
            
            with st.spinner("Checking game data source..."):
                games = get_games_for_date(date.today(), ['MLB', 'NBA'])
                
                if games:
                    st.success(f"✅ Found {len(games)} games")
                    
                    # Check if games look like mock data
                    sample_game = games[0]
                    
                    # Mock data indicators
                    mock_indicators = []
                    
                    if 'Mock' in str(sample_game.get('home_team', '')):
                        mock_indicators.append("Team names contain 'Mock'")
                    
                    if sample_game.get('sport') == 'TEST':
                        mock_indicators.append("Sport is 'TEST'")
                    
                    if len(set(str(g.get('home_team', '')) for g in games[:5])) < 3:
                        mock_indicators.append("Too few unique team names")
                    
                    if mock_indicators:
                        st.warning("🎭 **Mock data detected!**")
                        for indicator in mock_indicators:
                            st.write(f"• {indicator}")
                    else:
                        st.success("✅ Data appears to be real ESPN/API data")
                        
                        # Show sample games
                        st.markdown("**Sample Games:**")
                        for i, game in enumerate(games[:3]):
                            home = game.get('home_team', 'Unknown')
                            away = game.get('away_team', 'Unknown')
                            sport = game.get('sport', 'Unknown')
                            st.write(f"{i+1}. {away} @ {home} ({sport})")
                else:
                    st.warning("⚠️ No games found - this might indicate an issue")
                    
        except Exception as e:
            st.error(f"❌ Mock data check failed: {str(e)}")
    
    # Configuration Recommendations
    st.markdown("## 💡 Configuration Recommendations")
    
    issues = []
    
    if not (supabase_url and supabase_key):
        issues.append("🗄️ **Database not configured** - Add SUPABASE_URL and SUPABASE_ANON_KEY to Streamlit Cloud secrets")
    
    if not (openai_key or google_key):
        issues.append("🤖 **No AI APIs configured** - Add OPENAI_API_KEY or GOOGLE_API_KEY to Streamlit Cloud secrets")
    
    if not issues:
        st.success("🎉 **All configurations look good!**")
        st.balloons()
    else:
        st.markdown("**Issues to fix:**")
        for issue in issues:
            st.write(issue)
        
        st.markdown("**How to fix:**")
        st.code("""
1. Go to your Streamlit Cloud app
2. Click Settings → Secrets
3. Add the missing environment variables:

SUPABASE_URL = "https://wyelnpltrgdxticiadrt.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
OPENAI_API_KEY = "sk-your-openai-key"
GOOGLE_API_KEY = "your-google-key"
        """)
    
    # Raw Environment Dump (for debugging)
    if st.checkbox("🔍 Show Raw Environment Variables (Debug)"):
        st.markdown("### 🗂️ All Environment Variables")
        
        env_vars = dict(os.environ)
        
        # Filter sensitive ones
        filtered_vars = {}
        for key, value in env_vars.items():
            if any(sensitive in key.upper() for sensitive in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                if len(value) > 10:
                    filtered_vars[key] = f"{value[:8]}...{value[-4:]}"
                else:
                    filtered_vars[key] = "***"
            else:
                filtered_vars[key] = value
        
        st.json(filtered_vars)

if __name__ == "__main__":
    show_live_diagnostics()