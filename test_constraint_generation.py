import pymongo
import requests
import json

# Connect to MongoDB Atlas
client = pymongo.MongoClient('mongodb+srv://dibyajyotisarkar07:Dibyajyoti2004@cluster0.zbf2c.mongodb.net')
db = client['timetable_db']

# Get the first program
program = db.programs.find_one()
if program:
    program_id = str(program['_id'])
    print(f"Program ID: {program_id}")
    
    # Test constraint-based timetable generation
    try:
        # Read admin token
        with open('admin_token.txt', 'r') as f:
            token = f.read().strip()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        BASE_URL = "http://localhost:8000"
        print(f"Testing constraint-based timetable generation at {BASE_URL}")
        
        response = requests.post(
            f'{BASE_URL}/api/v1/timetable/generate-constraint-based',
            json={
                'program_id': program_id, 
                'semester': 1,
                'academic_year': '2024-25'
            },
            headers=headers,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:1000]}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No programs found in database")