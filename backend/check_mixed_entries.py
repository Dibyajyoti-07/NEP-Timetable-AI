import asyncio
import json
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def check_mixed_entries():
    await connect_to_mongo()
    
    # Get all timetables for the admin user
    timetables = await db.db.timetables.find({'created_by': ObjectId('68b5c493b2adfdb5c89a37c7')}).to_list(None)
    
    print(f"Found {len(timetables)} timetables")
    
    for i, timetable in enumerate(timetables):
        print(f"\n=== Timetable {i+1}: {timetable.get('title', 'No title')} ===")
        print(f"ID: {timetable['_id']}")
        
        entries = timetable.get('entries', [])
        print(f"Entries: {len(entries)}")
        
        if entries:
            first_entry = entries[0]
            print("First entry structure:")
            print(f"  Has course_id: {'course_id' in first_entry}")
            print(f"  Has time_slot: {'time_slot' in first_entry}")
            print(f"  Has course_code: {'course_code' in first_entry}")
            print(f"  Has day: {'day' in first_entry}")
            print(f"  Has start_time: {'start_time' in first_entry}")
            
            if 'course_id' not in first_entry or 'time_slot' not in first_entry:
                print("  ⚠️  OLD STRUCTURE DETECTED!")
                print(f"  Fields: {list(first_entry.keys())}")
                
                # Show a few more entries to see the pattern
                for j in range(min(3, len(entries))):
                    entry = entries[j]
                    has_required = 'course_id' in entry and 'time_slot' in entry
                    print(f"  Entry {j+1}: Required fields = {has_required}")

if __name__ == "__main__":
    asyncio.run(check_mixed_entries())