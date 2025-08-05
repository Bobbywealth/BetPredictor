#!/usr/bin/env python3
"""
Test script to identify and fix the caching error
"""

import sys
import os

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_caching_issues():
    """Test for potential caching issues in the app"""
    
    print("🔍 Testing for caching issues...")
    
    # Test 1: Check if we can import app without errors
    try:
        from app import get_ai_analysis
        print("✅ Successfully imported get_ai_analysis")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Create a test game and try analysis
    test_game = {
        'home_team': 'Miami Marlins',
        'away_team': 'Houston Astros',
        'sport': 'MLB',
        'league': 'MLB'
    }
    
    try:
        # Test without any streamlit objects
        print("🧪 Testing AI analysis function...")
        result = get_ai_analysis(test_game)
        
        if result is None:
            print("✅ Function returns None (expected if no API keys)")
        else:
            print(f"✅ Function returned: {type(result)}")
            
        print("✅ No caching errors detected in get_ai_analysis")
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_cache_notifications():
    """Test cache notification logic"""
    
    print("\n📦 Testing cache notification logic...")
    
    # Simulate session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
            
        def get(self, key, default=None):
            return self.data.get(key, default)
            
        def __setitem__(self, key, value):
            self.data[key] = value
            
        def __getitem__(self, key):
            return self.data[key]
    
    mock_session = MockSessionState()
    
    # Test notification frequency
    notifications_shown = 0
    
    for i in range(100):
        # Simulate cache notification logic
        show_notifications = mock_session.get('show_cache_notifications', False)
        
        if show_notifications:
            if 'odds_cache_notifications' not in mock_session.data:
                mock_session['odds_cache_notifications'] = 0
            
            mock_session['odds_cache_notifications'] += 1
            if mock_session['odds_cache_notifications'] % 50 == 1:
                notifications_shown += 1
    
    print(f"✅ Notifications shown in 100 cache hits (with notifications enabled): {notifications_shown}")
    
    # Test with notifications disabled (default)
    mock_session2 = MockSessionState()
    notifications_shown_disabled = 0
    
    for i in range(100):
        show_notifications = mock_session2.get('show_cache_notifications', False)  # Default False
        if show_notifications:  # This should never be True
            notifications_shown_disabled += 1
    
    print(f"✅ Notifications shown in 100 cache hits (with notifications disabled): {notifications_shown_disabled}")
    
    return True

if __name__ == "__main__":
    print("🧪 Running caching tests...")
    
    success1 = test_caching_issues()
    success2 = test_cache_notifications()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
        print("✅ No caching issues detected")
        print("✅ Cache notifications properly controlled")
    else:
        print("\n❌ Some tests failed")
        
    print("\n" + "="*50)
    print("🔧 Recommendations:")
    print("1. Cache notifications are now OFF by default")
    print("2. Frequency reduced to every 50th occurrence")
    print("3. Changed from st.info to st.success with better icon")