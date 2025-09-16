import asyncio
from app.db.mongodb import db, connect_to_mongo

async def check_programs():
    # Initialize database connection
    await connect_to_mongo()
    
    # Check all programs in the database
    programs = await db.db.programs.find({}).to_list(length=None)
    print(f'Found {len(programs)} programs in database')
    
    for i, program in enumerate(programs):
        print(f'Program {i+1}: {program.get("code", "N/A")} - {program.get("name", "N/A")} - Active: {program.get("is_active", "N/A")}')
        print(f'  ID: {program.get("_id", "N/A")}')
        print(f'  Department: {program.get("department", "N/A")}')
        print(f'  Type: {program.get("type", "N/A")}')
        print()

if __name__ == '__main__':
    asyncio.run(check_programs())