import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import httpx
import json

async def test_advanced_generation():
    """Test the advanced generation API endpoint"""
    try:
        print("🔍 Testing Advanced Generation API...")
        
        # Test data matching frontend request with actual database values
        request_data = {
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
                "end_time": "17:00",
                "break_duration": 60,
                "lunch_start": "13:00",
                "lunch_end": "14:00"
            },
            "constraints": {
                "max_periods_per_day": 6,
                "max_continuous_periods": 3,
                "min_break_between_periods": 10
            }
        }
        
        print(f"📤 Sending request to: http://localhost:8000/api/v1/timetable/generate-advanced")
        print(f"📋 Request data: {json.dumps(request_data, indent=2)}")
        
        # Make the API request
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/timetable/generate-advanced",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTk0NzMxODAsInN1YiI6IjY4YjVjNDkzYjJhZGZkYjVjODlhMzdjNyJ9.C5pk43MkvWb6wRNMhvWPXU36C-Z4myXdv0gEwqR_qM0"
                }
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Generated timetable with {len(result.get('schedule', []))} entries")
                print(f"📊 Statistics: {result.get('statistics', {})}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📋 Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📋 Raw error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_advanced_generation())
    if success:
        print("\n🎉 Advanced generation test PASSED!")
    else:
        print("\n💥 Advanced generation test FAILED!")