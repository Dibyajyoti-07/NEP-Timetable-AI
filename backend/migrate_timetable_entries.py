import asyncio
import json
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def migrate_old_entries():
    await connect_to_mongo()
    
    # Get all timetables for the admin user
    timetables = await db.db.timetables.find({'created_by': ObjectId('68b5c493b2adfdb5c89a37c7')}).to_list(None)
    
    print(f"Found {len(timetables)} timetables")
    
    updated_count = 0
    
    for i, timetable in enumerate(timetables):
        timetable_id = timetable['_id']
        entries = timetable.get('entries', [])
        
        if not entries:
            continue
            
        # Check if this timetable has string time_slot (needs migration)
        first_entry = entries[0]
        has_string_time_slot = 'time_slot' in first_entry and isinstance(first_entry['time_slot'], str)
        has_missing_required = ('course_id' not in first_entry or 'time_slot' not in first_entry) and 'course_code' in first_entry
        
        has_old_structure = has_string_time_slot or has_missing_required
        
        if has_old_structure:
            print(f"\nMigrating timetable {i+1}: {timetable.get('title', 'No title')}")
            print(f"  ID: {timetable_id}")
            print(f"  Entries: {len(entries)}")
            
            # Transform entries from old to new structure
            new_entries = []
            
            for j, entry in enumerate(entries):
                # Calculate duration in minutes
                start_time = entry.get('start_time', '09:00')
                end_time = entry.get('end_time', '10:00')
                duration = entry.get('duration', 60)
                
                # Create TimeSlot object
                time_slot = {
                    'day': entry.get('day', 'Monday'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_minutes': duration
                }
                
                # Create new entry with required fields
                new_entry = {
                    'course_id': entry.get('course_id', entry.get('faculty_id', '')),  # Keep existing course_id or use faculty_id
                    'faculty_id': entry.get('faculty_id', ''),
                    'room_id': entry.get('room_id', ''),
                    'group_id': entry.get('group_id'),
                    'time_slot': time_slot,
                    # Keep all existing fields as well
                    **{k: v for k, v in entry.items() if k not in ['time_slot']}  # Exclude old time_slot
                }
                new_entries.append(new_entry)
                
                # Debug first entry
                if j == 0:
                    print(f"  Original time_slot: {entry.get('time_slot')} (type: {type(entry.get('time_slot'))})")
                    print(f"  New time_slot: {time_slot} (type: {type(time_slot)})")
            
            # Update the timetable in database
            try:
                result = await db.db.timetables.update_one(
                    {'_id': timetable_id},
                    {'$set': {'entries': new_entries}}
                )
                
                if result.modified_count > 0:
                    print(f"  ✅ Successfully updated {len(new_entries)} entries")
                    updated_count += 1
                else:
                    print(f"  ❌ Failed to update - matched: {result.matched_count}, modified: {result.modified_count}")
            except Exception as e:
                print(f"  ❌ Error during update: {e}")
        else:
            print(f"Skipping timetable {i+1}: Already has new structure")
    
    print(f"\n🎉 Migration complete! Updated {updated_count} timetables.")

if __name__ == "__main__":
    asyncio.run(migrate_old_entries())