import asyncio
import json
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def check_timetable_structure():
    await connect_to_mongo()
    
    # Get one timetable to examine its structure
    timetable = await db.db.timetables.find_one({'_id': ObjectId('68c1ac9eae44603ece6571d1')})
    
    if timetable:
        print("Timetable structure:")
        print(json.dumps(timetable, indent=2, default=str))
        
        if 'entries' in timetable:
            print("\n=== ENTRIES STRUCTURE ===")
            print(f"Number of entries: {len(timetable['entries'])}")
            if timetable['entries']:
                print("\nFirst entry structure:")
                print(json.dumps(timetable['entries'][0], indent=2, default=str))
    else:
        print("Timetable not found")
    
    # No disconnect method needed

if __name__ == "__main__":
    asyncio.run(check_timetable_structure())