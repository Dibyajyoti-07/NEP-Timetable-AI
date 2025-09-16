import asyncio
import requests
import json

async def test_simple_generation():
    """Test with minimal constraints to get basic generation working"""
    
    # Simplified request with minimal constraints
    test_data = {
        "program_id": "68b5c517e73858dcb11d37e4",
        "semester": 5,
        "academic_year": "2024-25",
        "working_days": {
            "Monday": True,
            "Tuesday": True,
            "Wednesday": True,
            "Thursday": True,
            "Friday": True,
            "Saturday": False,
            "Sunday": False
        },
        "time_slots": {
            "start_time": "09:00",
            "end_time": "16:00",  # Reduced end time
            "break_duration": 30,   # Reduced break
            "lunch_start": "12:30",
            "lunch_end": "13:30"
        },
        "constraints": {
            "max_periods_per_day": 8,    # Increased max periods
            "max_continuous_periods": 4, # Increased continuous periods
            "min_break_between_periods": 5  # Reduced break time
        }
    }
    
    print("🔍 Testing Simple Generation API...")
    print(f"📤 Sending request to: http://localhost:8000/api/v1/timetable/generate-advanced")
    print(f"📋 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Read admin token
        with open('admin_token.txt', 'r') as f:
            admin_token = f.read().strip()
        
        headers = {
            'Authorization': f'Bearer {admin_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/timetable/generate-advanced",
            json=test_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📋 Response: {json.dumps(result, indent=2)[:500]}...")
            
            # Save the result
            with open('successful_generation.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("💾 Saved result to successful_generation.json")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📋 Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📋 Error text: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🚫 Request failed: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_generation())