import asyncio
from app.db.mongodb import connect_to_mongo, db
from datetime import datetime

async def fix_programs_data():
    await connect_to_mongo()
    
    # Get all programs
    programs = await db.db.programs.find({}).to_list(length=None)
    print(f'Found {len(programs)} programs to check')
    
    for program in programs:
        update_data = {}
        
        # Add missing 'type' field
        if 'type' not in program:
            # Default to B.Tech for engineering programs
            if 'engineering' in program.get('name', '').lower() or 'tech' in program.get('name', '').lower():
                update_data['type'] = 'B.Tech'
            else:
                update_data['type'] = 'B.Tech'  # Default fallback
            print(f"Adding type 'B.Tech' to program: {program.get('name')}")
        
        # Add missing 'total_semesters' field
        if 'total_semesters' not in program:
            # Calculate based on duration_years (assuming 2 semesters per year)
            duration_years = program.get('duration_years', 4)
            update_data['total_semesters'] = duration_years * 2
            print(f"Adding total_semesters {duration_years * 2} to program: {program.get('name')}")
        
        # Add missing 'description' field if not present
        if 'description' not in program:
            update_data['description'] = f"Academic program in {program.get('department', 'General')}"
            print(f"Adding description to program: {program.get('name')}")
        
        # Update the program if there are changes
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            await db.db.programs.update_one(
                {'_id': program['_id']}, 
                {'$set': update_data}
            )
            print(f"Updated program: {program.get('name')} with {update_data}")
    
    # Verify the fix
    print("\nVerifying fixes...")
    updated_programs = await db.db.programs.find({}).to_list(length=None)
    for program in updated_programs:
        missing_fields = []
        required_fields = ['type', 'total_semesters', 'name', 'code', 'department', 'duration_years', 'credits_required']
        
        for field in required_fields:
            if field not in program:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Program {program.get('name')} still missing: {missing_fields}")
        else:
            print(f"✅ Program {program.get('name')} has all required fields")
    
    print("\nPrograms data fix completed!")

if __name__ == '__main__':
    asyncio.run(fix_programs_data())