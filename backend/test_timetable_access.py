import requests

def test_timetable_access():
    """Test timetable access with admin credentials"""
    
    # Login with admin credentials
    login_data = {
        'username': 'admin@example.com',
        'password': 'admin123'
    }
    
    print("Testing login...")
    response = requests.post('http://localhost:8001/api/v1/auth/login', data=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"Token received: {bool(token)}")
        
        if token:
            # Test timetable access
            timetable_id = '68c8552e01625d573970cce7'  # Latest timetable ID
            print(f"\nTesting access to timetable {timetable_id}...")
            
            timetable_response = requests.get(
                f'http://localhost:8001/api/v1/timetables/{timetable_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            print(f"Timetable access status: {timetable_response.status_code}")
            
            if timetable_response.status_code == 200:
                print("Success - timetable found and accessible!")
                timetable_data = timetable_response.json()
                print(f"Timetable title: {timetable_data.get('title', 'N/A')}")
                print(f"Entries count: {len(timetable_data.get('entries', []))}")
            else:
                print(f"Error: {timetable_response.text}")
    else:
        print(f"Login failed: {response.text}")

if __name__ == "__main__":
    test_timetable_access()