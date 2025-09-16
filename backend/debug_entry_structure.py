import asyncio
import json
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def debug_entry_structure():
    await connect_to_mongo()
    
    # Get one specific timetable that was failing
    timetable = await db.db.timetables.find_one({'_id': ObjectId('68c29887be83a0ef37d33b89')})
    
    if timetable:
        print(f"Timetable: {timetable.get('title', 'No title')}")
        entries = timetable.get('entries', [])
        print(f"Total entries: {len(entries)}")
        
        if entries:
            print("\nFirst entry structure:")
            first_entry = entries[0]
            print(json.dumps(first_entry, indent=2, default=str))
            
            print("\nTime slot details:")
            time_slot = first_entry.get('time_slot')
            print(f"Time slot type: {type(time_slot)}")
            print(f"Time slot value: {time_slot}")
            
            if isinstance(time_slot, dict):
                print("Time slot fields:")
                for key, value in time_slot.items():
                    print(f"  {key}: {value} ({type(value)})")
    else:
        print("Timetable not found")

if __name__ == "__main__":
    asyncio.run(debug_entry_structure())