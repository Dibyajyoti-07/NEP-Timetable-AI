import requests
import json

# Read token
with open('admin_token.txt', 'r') as f:
    token = f.read().strip()

# Test programs API
response = requests.get(
    'http://localhost:8000/api/v1/programs/',
    headers={'Authorization': f'Bearer {token}'}
)

print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'Number of programs: {len(data)}')
    
    if data:
        first_program = data[0]
        print(f'First program has id field: {"id" in first_program}')
        print(f'First program has _id field: {"_id" in first_program}')
        print(f'First program keys: {list(first_program.keys())}')
        print(f'First program: {json.dumps(first_program, indent=2, default=str)}')
else:
    print(f'Error: {response.text}')