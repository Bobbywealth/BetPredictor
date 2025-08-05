"""
Test script to verify game generation is working properly
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_game_generation():
    """Test all the main game generation functions"""
    
    print("🧪 Testing Spizo Game Generation Functions...")
    print("=" * 50)
    
    # Test 1: Basic ESPN API functionality
    print("\n1. Testing ESPN API Integration...")
    try:
        from utils.live_games import LiveGamesManager
        
        games_manager = LiveGamesManager()
        today = date.today()
        
        print(f"   📅 Testing games for today: {today}")
        games_df = games_manager.get_upcoming_games_all_sports(target_date=today)
        
        if games_df is not None and len(games_df) > 0:
            print(f"   ✅ SUCCESS: Found {len(games_df)} games from ESPN API")
            
            # Show sample games
            for i, (idx, game) in enumerate(games_df.head(3).iterrows()):
                home_team = game.get('home_team', {})
                away_team = game.get('away_team', {})
                league = game.get('league', 'Unknown')
                
                if isinstance(home_team, dict):
                    home_name = home_team.get('name', 'Unknown')
                else:
                    home_name = str(home_team)
                    
                if isinstance(away_team, dict):
                    away_name = away_team.get('name', 'Unknown')
                else:
                    away_name = str(away_team)
                
                print(f"   📊 Game {i+1}: {away_name} @ {home_name} ({league})")
        else:
            print("   ⚠️  No games found for today, testing tomorrow...")
            tomorrow = today + timedelta(days=1)
            games_df = games_manager.get_upcoming_games_all_sports(target_date=tomorrow)
            
            if games_df is not None and len(games_df) > 0:
                print(f"   ✅ SUCCESS: Found {len(games_df)} games for tomorrow")
            else:
                print("   ❌ WARNING: No games found for today or tomorrow")
                
    except Exception as e:
        print(f"   ❌ ERROR: ESPN API test failed: {str(e)}")
    
    # Test 2: App.py game generation
    print("\n2. Testing App.py Game Generation...")
    try:
        # Import the main app functions
        from app import get_games_for_date
        
        today = date.today()
        sports = ['NFL', 'NBA', 'MLB', 'WNBA']
        
        print(f"   📅 Testing get_games_for_date for: {sports}")
        games = get_games_for_date(today, sports)
        
        if games and len(games) > 0:
            print(f"   ✅ SUCCESS: get_games_for_date returned {len(games)} games")
            
            # Show sample games
            for i, game in enumerate(games[:3]):
                home_team = game.get('home_team', 'Unknown')
                away_team = game.get('away_team', 'Unknown')
                sport = game.get('sport', 'Unknown')
                print(f"   📊 Game {i+1}: {away_team} vs {home_team} ({sport})")
        else:
            print("   ⚠️  No games from get_games_for_date, this might be normal if no games today")
            
    except Exception as e:
        print(f"   ❌ ERROR: App.py game generation test failed: {str(e)}")
    
    # Test 3: Daily predictions generation
    print("\n3. Testing Daily Predictions Generation...")
    try:
        from app import generate_daily_top_picks
        
        print("   🤖 Testing generate_daily_top_picks...")
        
        # Test with lower confidence to see if we get any results
        daily_picks = generate_daily_top_picks(target_date=today, min_confidence=0.5)
        
        if daily_picks and len(daily_picks) > 0:
            print(f"   ✅ SUCCESS: Generated {len(daily_picks)} daily picks")
            
            for i, pick in enumerate(daily_picks[:3]):
                home_team = pick.get('home_team', 'Unknown')
                away_team = pick.get('away_team', 'Unknown')
                confidence = pick.get('ai_analysis', {}).get('confidence', 0)
                print(f"   🎯 Pick {i+1}: {away_team} vs {home_team} (Confidence: {confidence:.1%})")
        else:
            print("   ⚠️  No daily picks generated - this might be due to:")
            print("      - No API keys configured")
            print("      - No games available")
            print("      - All predictions below confidence threshold")
            
    except Exception as e:
        print(f"   ❌ ERROR: Daily predictions test failed: {str(e)}")
    
    # Test 4: API Configuration Check
    print("\n4. Testing API Configuration...")
    try:
        import os
        
        openai_key = os.environ.get("OPENAI_API_KEY")
        google_key = os.environ.get("GOOGLE_API_KEY")
        odds_key = os.environ.get("ODDS_API_KEY")
        
        print(f"   🔑 OpenAI API Key: {'✅ Configured' if openai_key else '❌ Missing'}")
        print(f"   🔑 Google Gemini Key: {'✅ Configured' if google_key else '❌ Missing'}")
        print(f"   🔑 Odds API Key: {'✅ Configured' if odds_key else '❌ Missing'}")
        
        if not openai_key and not google_key:
            print("   ⚠️  WARNING: No AI API keys configured - predictions won't work")
        
    except Exception as e:
        print(f"   ❌ ERROR: API configuration check failed: {str(e)}")
    
    # Test 5: Database Connection
    print("\n5. Testing Database Connection...")
    try:
        from app import init_supabase
        
        supabase = init_supabase()
        if supabase:
            print("   ✅ SUCCESS: Database connection established")
            
            # Test a simple query
            try:
                result = supabase.table('users').select("count", count='exact').execute()
                print(f"   📊 Database has {result.count} users")
            except Exception as e:
                print(f"   ⚠️  Database connected but query failed: {str(e)}")
        else:
            print("   ❌ WARNING: Database connection failed - check Supabase credentials")
            
    except Exception as e:
        print(f"   ❌ ERROR: Database test failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Game Generation Test Complete!")
    print("\n💡 Tips:")
    print("   - If no games found, try checking during sports seasons")
    print("   - Configure API keys in environment variables for full functionality")
    print("   - Database features require Supabase configuration")

if __name__ == "__main__":
    test_game_generation()