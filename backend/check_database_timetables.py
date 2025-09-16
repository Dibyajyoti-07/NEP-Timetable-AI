import asyncio
import requests
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mongodb import db
from bson import ObjectId
import json

async def check_database_timetables():
    """Check what timetables are actually stored in the database"""
    
    # Initialize database connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    db.db = database
    
    print("Checking database for timetables...")
    
    # Get all timetables
    timetables = await db.db.timetables.find({}).to_list(None)
    print(f"Found {len(timetables)} timetables in database")
    
    for i, timetable in enumerate(timetables):
        print(f"\nTimetable {i+1}:")
        print(f"  - ID: {timetable['_id']}")
        print(f"  - Title: {timetable.get('title', 'N/A')}")
        print(f"  - Program ID: {timetable.get('program_id', 'N/A')}")
        print(f"  - Semester: {timetable.get('semester', 'N/A')}")
        print(f"  - Academic Year: {timetable.get('academic_year', 'N/A')}")
        print(f"  - Created by: {timetable.get('created_by', 'N/A')}")
        print(f"  - Entries count: {len(timetable.get('entries', []))}")
        print(f"  - Created at: {timetable.get('created_at', 'N/A')}")
        
        if timetable.get('entries'):
            print(f"  - Sample entry: {timetable['entries'][0]}")
        else:
            print("  - No entries found")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(check_database_timetables())