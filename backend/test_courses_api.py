import requests
import json

# Read the admin token
with open('admin_token.txt', 'r') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Test courses API
response = requests.get('http://localhost:8000/api/v1/courses/', headers=headers)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Number of courses: {len(data)}")
    
    if data:
        first_course = data[0]
        print(f"First course has id field: {'id' in first_course}")
        print(f"First course has _id field: {'_id' in first_course}")
        print(f"First course keys: {list(first_course.keys())}")
        print(f"First course: {json.dumps(first_course, indent=2)}")
    else:
        print("No courses found")
else:
    print(f"Error: {response.text}")