import asyncio
import requests
import json
from datetime import datetime

async def test_timetable_generation():
    """Test timetable generation and check the response structure"""
    
    # API base URL
    base_url = "http://localhost:8000/api/v1"
    
    # First, get an admin token
    try:
        with open('admin_token.txt', 'r') as f:
            token = f.read().strip()
        print(f"Using admin token: {token[:20]}...")
    except FileNotFoundError:
        print("Admin token file not found")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get programs to find a valid program_id
    print("\n1. Getting programs...")
    try:
        response = requests.get(f"{base_url}/programs/", headers=headers)
        print(f"Programs API status: {response.status_code}")
        
        if response.status_code == 200:
            programs = response.json()
            print(f"Found {len(programs)} programs")
            if programs:
                program_id = programs[0]['id']
                print(f"Using program_id: {program_id}")
            else:
                print("No programs found")
                return
        else:
            print(f"Failed to get programs: {response.text}")
            return
    except Exception as e:
        print(f"Error getting programs: {e}")
        return
    
    # Generate simple timetable first
    print("\n2. Generating simple timetable...")
    
    try:
        response = requests.post(
            f"{base_url}/timetable/generate",
            headers=headers,
            json={
                "program_id": program_id,
                "semester": 5,
                "academic_year": "2025-2026"
            }
        )
        print(f"Generation API status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Generation successful!")
            print(f"Timetable ID: {result.get('timetable_id')}")
            
            # Print the full response to debug
            print(f"\nFull API response: {json.dumps(result, indent=2)}")
            
            # Check the timetable structure
            entries = result.get('entries', [])
            print(f"\n3. Timetable structure analysis:")
            print(f"   - Total entries: {len(entries)}")
            
            if entries:
                print(f"   - First entry structure:")
                first_entry = entries[0]
                for key, value in first_entry.items():
                    print(f"     {key}: {value}")
                
                print(f"\n   - Sample entries:")
                for i, entry in enumerate(entries[:3]):
                    if 'time_slot' in entry:
                        time_slot = entry['time_slot']
                        print(f"     Entry {i+1}: {time_slot.get('day')} {time_slot.get('start_time')}-{time_slot.get('end_time')} - Course: {entry.get('course_id')}")
                    else:
                        print(f"     Entry {i+1}: {entry}")
            else:
                print("   - No entries found in timetable!")
                print(f"   - Available keys in response: {list(result.keys())}")
            
        else:
            print(f"Generation failed: {response.text}")
            
    except Exception as e:
        print(f"Error generating timetable: {e}")

if __name__ == "__main__":
    asyncio.run(test_timetable_generation())