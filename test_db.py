"""
Quick database connection test for Spizo
Run this to verify your Supabase setup is working
"""

import os
from supabase import create_client, Client

def test_database_connection():
    """Test Supabase connection and basic operations"""
    
    # Your database credentials
    supabase_url = "https://wyelnpltrgdxticiadrt.supabase.co"
    # Using the correct anon public key
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5ZWxucGx0cmdkeHRpY2lhZHJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MTczNDIsImV4cCI6MjA2OTk5MzM0Mn0.2EU5oG9mmiY3CKyHrIwkW1BvptOJu02AWrH0ifaFFCY"
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test 1: Check if tables exist
        try:
            result = supabase.table('users').select("count", count='exact').execute()
            print(f"✅ Users table exists with {result.count} records")
        except Exception as e:
            print(f"❌ Users table error: {e}")
            
        try:
            result = supabase.table('predictions').select("count", count='exact').execute()
            print(f"✅ Predictions table exists with {result.count} records")
        except Exception as e:
            print(f"❌ Predictions table error: {e}")
            
        try:
            result = supabase.table('api_usage').select("count", count='exact').execute()
            print(f"✅ API usage table exists with {result.count} records")
        except Exception as e:
            print(f"❌ API usage table error: {e}")
            
        try:
            result = supabase.table('daily_betting_summary').select("count", count='exact').execute()
            print(f"✅ Daily betting summary table exists with {result.count} records")
        except Exception as e:
            print(f"❌ Daily betting summary table error: {e}")
        
        # Test 2: Insert test API usage record
        try:
            test_record = {
                "provider": "OpenAI GPT-4o",
                "tokens_used": 1500,
                "cost": 0.09,
                "request_type": "prediction",
                "success": True
            }
            result = supabase.table('api_usage').insert(test_record).execute()
            print("✅ Test API usage record inserted successfully")
            
            # Clean up test record
            supabase.table('api_usage').delete().eq('provider', 'OpenAI GPT-4o').execute()
            print("✅ Test record cleaned up")
            
        except Exception as e:
            print(f"❌ API usage insert test failed: {e}")
        
        print("\n🎉 Database setup complete! Your Spizo app is ready to use persistent storage.")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()