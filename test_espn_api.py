import requests
import json
from datetime import datetime, timedelta

def test_espn_api():
    print("Testing ESPN API...")
    
    # Test current NBA games
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'events' in data:
                events = data['events']
                print(f"Number of events: {len(events)}")
                
                if len(events) > 0:
                    print("\nFirst event details:")
                    event = events[0]
                    print(f"Event keys: {list(event.keys())}")
                    print(f"Event ID: {event.get('id')}")
                    print(f"Event name: {event.get('name')}")
                    print(f"Event date: {event.get('date')}")
                    
                    if 'competitions' in event:
                        comp = event['competitions'][0]
                        print(f"Competition keys: {list(comp.keys())}")
                        
                        if 'competitors' in comp:
                            teams = comp['competitors']
                            print(f"Teams: {len(teams)}")
                            for team in teams:
                                team_info = team.get('team', {})
                                print(f"  {team_info.get('displayName', 'Unknown')} - {team.get('score', 0)}")
                else:
                    print("No events found")
            else:
                print("No 'events' key in response")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"Error: {e}")

    # Test with specific date
    print("\n" + "="*50)
    print("Testing with today's date...")
    
    today = datetime.now().strftime('%Y%m%d')
    url_with_date = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today}"
    
    try:
        response = requests.get(url_with_date, timeout=10)
        print(f"Status Code with date: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'events' in data:
                print(f"Events with date filter: {len(data['events'])}")
        
    except Exception as e:
        print(f"Error with date: {e}")

if __name__ == "__main__":
    test_espn_api()