import asyncio
import sys
sys.path.append('.')

from app.api.v1.endpoints.timetable import get_timetables
from app.services.auth import get_current_user
from app.db.mongodb import db, connect_to_mongo
from app.models.user import User
from bson import ObjectId

async def test_timetable_endpoint():
    try:
        await connect_to_mongo()
        print('✅ MongoDB connected successfully')
        
        # Get the user directly from database
        user_id = "68b5c493b2adfdb5c89a37c7"
        user_doc = await db.db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            print(f'❌ User not found: {user_id}')
            return
            
        # Convert to User model
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        current_user = User(**user_doc)
        
        print(f'✅ User loaded: {current_user.email}')
        
        # Test the timetable endpoint directly
        print('🔍 Testing timetable endpoint...')
        
        try:
            timetables = await get_timetables(
                skip=0,
                limit=100,
                program_id=None,
                semester=None,
                academic_year=None,
                is_draft=None,
                current_user=current_user
            )
            
            print(f'✅ Timetables retrieved successfully: {len(timetables)} found')
            if timetables:
                print(f'📊 First timetable: {timetables[0].get("title", "No title")}')
                
        except Exception as e:
            print(f'❌ Timetable endpoint error: {e}')
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_timetable_endpoint())