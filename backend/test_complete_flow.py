#!/usr/bin/env python3
"""
Comprehensive test script to verify the complete timetable generation flow
with the updated frontend configuration and fixed database data.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
PROGRAM_ID = "68b5c517e73858dcb11d37e4"
SEMESTER = 5
ACADEMIC_YEAR = "2024-25"

def read_admin_token():
    """Read admin token from file"""
    try:
        with open('admin_token.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ admin_token.txt not found")
        return None

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        print(f"📡 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                print(f"   Result: {len(result)} items")
                if result:
                    print(f"   First item keys: {list(result[0].keys()) if isinstance(result[0], dict) else 'Not a dict'}")
            else:
                print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            return True, result
        else:
            print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False, None

def test_timetable_generation(headers):
    """Test the complete timetable generation with frontend-like data"""
    print("\n🎯 Testing Timetable Generation with Frontend Configuration")
    
    # Frontend-like generation request
    generation_data = {
        "program_id": PROGRAM_ID,
        "semester": SEMESTER,
        "academic_year": ACADEMIC_YEAR,
        "title": f"AI Generated Timetable - {ACADEMIC_YEAR}",
        
        # Working days (frontend default)
        "working_days": {
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": False,
            "sunday": False
        },
        
        # Time slots (frontend default)
        "time_slots": {
            "start_time": "11:00",
            "end_time": "16:30",
            "slot_duration": 50,
            "break_duration": 10,
            "lunch_break": True,
            "lunch_start": "13:00",
            "lunch_end": "14:00"
        },
        
        # Constraints (frontend default)
        "constraints": {
            "max_periods_per_day": 8,
            "max_consecutive_hours": 3,
            "min_break_between_subjects": 1,
            "avoid_first_last_slot": False,
            "balance_workload": True,
            "prefer_morning_slots": False
        }
    }
    
    print(f"📤 Sending generation request:")
    print(f"   Program ID: {PROGRAM_ID}")
    print(f"   Semester: {SEMESTER}")
    print(f"   Academic Year: {ACADEMIC_YEAR}")
    
    success, result = test_api_endpoint(
        "/timetable/generate-advanced",
        method="POST",
        data=generation_data,
        headers=headers
    )
    
    if success:
        print("✅ Timetable generation successful!")
        if 'schedule' in result:
            print(f"   📚 Sessions scheduled: {len(result['schedule'])}")
        if 'validation' in result:
            validation = result['validation']
            print(f"   ✅ Validation errors: {len(validation.get('errors', []))}")
            print(f"   ⚠️  Validation warnings: {len(validation.get('warnings', []))}")
        return True
    else:
        print("❌ Timetable generation failed")
        return False

def main():
    print("🚀 Starting Complete Timetable Generation Flow Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Read admin token
    token = read_admin_token()
    if not token:
        print("❌ Cannot proceed without admin token")
        sys.exit(1)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 Using admin token: {token[:20]}...")
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints")
    test_api_endpoint("/programs/", headers=headers)
    test_api_endpoint(f"/programs/{PROGRAM_ID}/courses?semester={SEMESTER}", headers=headers)
    test_api_endpoint("/faculty/", headers=headers)
    test_api_endpoint("/student-groups/", headers=headers)
    test_api_endpoint("/rooms/", headers=headers)
    
    # Test timetable generation
    success = test_timetable_generation(headers)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Complete flow test PASSED!")
        print("✅ Frontend should now be able to generate timetables successfully")
    else:
        print("❌ Complete flow test FAILED")
        print("🔧 Additional debugging may be needed")
    
    print(f"📅 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()