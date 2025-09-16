import asyncio
from app.services.timetable.simple_generator import SimpleTimetableGenerator
from bson import ObjectId
from app.db.mongodb import db
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def debug_simple_generator():
    """Debug the simple timetable generator to see what data it's loading"""
    
    # Initialize database connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    db.db = database
    
    # Get a program ID
    programs = await db.db.programs.find({}).to_list(None)
    if not programs:
        print("No programs found")
        return
    
    program_id = str(programs[0]["_id"])
    semester = 5
    
    print(f"Testing with program_id: {program_id}, semester: {semester}")
    
    # Create generator and test data loading
    generator = SimpleTimetableGenerator()
    
    # Test the _load_data method directly
    print("\n1. Loading data...")
    data = await generator._load_data(program_id, semester)
    
    print(f"   - Courses found: {len(data['courses'])}")
    print(f"   - Faculty found: {len(data['faculty'])}")
    print(f"   - Rooms found: {len(data['rooms'])}")
    print(f"   - Groups found: {len(data['groups'])}")
    
    if data['courses']:
        print(f"   - Sample course: {data['courses'][0]}")
    
    if data['faculty']:
        print(f"   - Sample faculty: {data['faculty'][0]}")
    
    if data['rooms']:
        print(f"   - Sample room: {data['rooms'][0]}")
    
    if data['groups']:
        print(f"   - Sample group: {data['groups'][0]}")
    
    # Test entry generation
    print("\n2. Generating entries...")
    entries = generator._generate_entries(data)
    print(f"   - Generated entries: {len(entries)}")
    
    if entries:
        print(f"   - Sample entry: {entries[0]}")
    else:
        print("   - No entries generated!")
        
        # Check if it's falling back to sample entries
        print("\n3. Testing sample entries fallback...")
        sample_entries = generator._create_sample_entries()
        print(f"   - Sample entries: {len(sample_entries)}")
        if sample_entries:
            print(f"   - Sample entry: {sample_entries[0]}")

if __name__ == "__main__":
    asyncio.run(debug_simple_generator())