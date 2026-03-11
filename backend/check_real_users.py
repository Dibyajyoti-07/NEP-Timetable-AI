import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

async def check_users():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client['timetable_db']
    
    print("=== Checking Users in Database ===")
    users = await db.users.find({}, {'_id': 1, 'email': 1, 'full_name': 1, 'is_admin': 1}).to_list(10)
    
    if users:
        print(f"\nFound {len(users)} users:")
        for user in users:
            print(f"  - ID: {user.get('_id')}")
            print(f"    Email: {user.get('email')}")
            print(f"    Name: {user.get('full_name')}")
            print(f"    Admin: {user.get('is_admin')}")
            print()
    else:
        print("No users found in database")
    
    # Check who created the timetables
    print("\n=== Checking Timetable Creators ===")
    timetables = await db.timetables.find({}, {'created_by': 1, 'title': 1}).limit(5).to_list(5)
    if timetables:
        creator_ids = set(str(t.get('created_by')) for t in timetables if t.get('created_by'))
        print(f"Timetables created by user IDs: {creator_ids}")
    
    client.close()

asyncio.run(check_users())
