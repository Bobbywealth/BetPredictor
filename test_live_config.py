"""
Test script to check the actual live configuration in Streamlit environment
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_live_configuration():
    """Test the actual live configuration that Streamlit would use"""
    
    print("🔍 Testing Live Spizo Configuration...")
    print("=" * 50)
    
    # Test 1: Check actual environment variables
    print("\n1. Environment Variables Check:")
    
    # Check if we're running in Streamlit context
    try:
        import streamlit as st
        print("   📱 Streamlit imported successfully")
        
        # Initialize session state like the app does
        if not hasattr(st, 'session_state'):
            print("   ⚠️  Running outside Streamlit - using os.environ")
            env_source = "os.environ"
        else:
            print("   ✅ Streamlit session available")
            env_source = "streamlit"
            
    except Exception as e:
        print(f"   ⚠️  Streamlit context issue: {e}")
        env_source = "os.environ"
    
    # Check database credentials
    print(f"\n   Database Configuration ({env_source}):")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")
    
    if supabase_url:
        print(f"   ✅ SUPABASE_URL: {supabase_url[:30]}...{supabase_url[-10:]}")
    else:
        print("   ❌ SUPABASE_URL: Not found")
        
    if supabase_key:
        print(f"   ✅ SUPABASE_ANON_KEY: {supabase_key[:20]}...{supabase_key[-10:]}")
    else:
        print("   ❌ SUPABASE_ANON_KEY: Not found")
    
    # Check AI API keys
    print(f"\n   AI API Configuration ({env_source}):")
    openai_key = os.environ.get("OPENAI_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    odds_key = os.environ.get("ODDS_API_KEY")
    
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY: sk-...{openai_key[-10:]}")
    else:
        print("   ❌ OPENAI_API_KEY: Not found")
        
    if google_key:
        print(f"   ✅ GOOGLE_API_KEY: ...{google_key[-10:]}")
    else:
        print("   ❌ GOOGLE_API_KEY: Not found")
        
    if odds_key:
        print(f"   ✅ ODDS_API_KEY: ...{odds_key[-10:]}")
    else:
        print("   ❌ ODDS_API_KEY: Not found")
    
    # Test 2: Direct database connection test
    print("\n2. Direct Database Connection Test:")
    try:
        from supabase import create_client, Client
        
        if supabase_url and supabase_key:
            print("   🔌 Attempting direct connection...")
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Test connection
            result = supabase.table('users').select("count", count='exact').execute()
            print(f"   ✅ SUCCESS: Database connected! Found {result.count} users")
            
            # Test predictions table
            pred_result = supabase.table('predictions').select("count", count='exact').execute()
            print(f"   📊 Predictions table: {pred_result.count} records")
            
            # Test API usage table
            api_result = supabase.table('api_usage').select("count", count='exact').execute()
            print(f"   💰 API usage table: {api_result.count} records")
            
        else:
            print("   ❌ Cannot test - missing database credentials")
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
    
    # Test 3: Test AI API functionality
    print("\n3. AI API Functionality Test:")
    if openai_key or google_key:
        print("   🤖 Testing AI predictions with sample game...")
        
        # Create a sample game for testing
        sample_game = {
            'home_team': 'Miami Marlins',
            'away_team': 'Houston Astros', 
            'sport': 'MLB',
            'league': 'MLB',
            'game_date': date.today(),
            'time': '7:00 PM'
        }
        
        try:
            from app import get_ai_analysis
            
            print("   📝 Calling get_ai_analysis...")
            analysis = get_ai_analysis(sample_game)
            
            if analysis:
                confidence = analysis.get('confidence', 0)
                pick = analysis.get('predicted_winner', 'Unknown')
                print(f"   ✅ AI Analysis SUCCESS!")
                print(f"   🎯 Prediction: {pick}")
                print(f"   📊 Confidence: {confidence:.1%}")
            else:
                print("   ⚠️  AI analysis returned None - check API keys or game data")
                
        except Exception as e:
            print(f"   ❌ AI analysis failed: {str(e)}")
    else:
        print("   ❌ Cannot test AI - no API keys found")
    
    # Test 4: Check if we can generate daily picks
    print("\n4. Daily Picks Generation Test:")
    if openai_key or google_key:
        try:
            from app import generate_daily_top_picks
            
            print("   🏆 Testing daily picks generation...")
            daily_picks = generate_daily_top_picks(target_date=date.today(), min_confidence=0.6)
            
            if daily_picks and len(daily_picks) > 0:
                print(f"   ✅ SUCCESS: Generated {len(daily_picks)} daily picks")
                for i, pick in enumerate(daily_picks[:2]):
                    home = pick.get('home_team', 'Unknown')
                    away = pick.get('away_team', 'Unknown') 
                    conf = pick.get('ai_analysis', {}).get('confidence', 0)
                    print(f"   🎯 Pick {i+1}: {away} vs {home} ({conf:.1%})")
            else:
                print("   ⚠️  No daily picks generated - might be normal if no high-confidence games")
                
        except Exception as e:
            print(f"   ❌ Daily picks generation failed: {str(e)}")
    else:
        print("   ❌ Cannot test daily picks - no AI API keys")
    
    print("\n" + "=" * 50)
    print("🏁 Live Configuration Test Complete!")
    
    # Summary
    has_db = bool(supabase_url and supabase_key)
    has_ai = bool(openai_key or google_key)
    
    print(f"\n📋 Summary:")
    print(f"   Database: {'✅ Configured' if has_db else '❌ Missing'}")
    print(f"   AI APIs: {'✅ Configured' if has_ai else '❌ Missing'}")
    
    if has_db and has_ai:
        print("   🚀 Your Spizo app should be fully functional!")
    elif has_db:
        print("   ⚠️  Database ready, but need AI API keys for predictions")
    elif has_ai:
        print("   ⚠️  AI ready, but need database for persistence")
    else:
        print("   ❌ Missing both database and AI configuration")

if __name__ == "__main__":
    test_live_configuration()