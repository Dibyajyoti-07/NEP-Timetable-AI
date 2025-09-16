import asyncio
from app.db.mongodb import connect_to_mongo, db

async def test_programs():
    await connect_to_mongo()
    programs = await db.db.programs.find({}).to_list(length=10)
    print(f'Found {len(programs)} programs in database')
    
    if programs:
        print('First few programs:')
        for i, program in enumerate(programs[:3]):
            print(f'Program {i+1}: {program}')
    else:
        print('No programs found in database')
        
    # Check collections
    collections = await db.db.list_collection_names()
    print(f'Available collections: {collections}')
    
    # Check if programs collection exists and has documents
    if 'programs' in collections:
        count = await db.db.programs.count_documents({})
        print(f'Total programs count: {count}')
    else:
        print('Programs collection does not exist')

if __name__ == '__main__':
    asyncio.run(test_programs())