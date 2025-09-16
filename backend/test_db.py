import asyncio
from app.db.mongodb import db, connect_to_mongo

async def test_connection():
    try:
        await connect_to_mongo()
        print('✅ MongoDB connected successfully')
        
        # Test a simple query
        test_doc = await db.db.timetables.find_one()
        print(f'📊 Test query result: {test_doc}')
        
        # Count documents
        count = await db.db.timetables.count_documents({})
        print(f'📈 Total timetables in database: {count}')
        
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_connection())