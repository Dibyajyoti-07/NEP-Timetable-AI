import asyncio
import jwt
from app.core.config import settings
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def test_auth():
    try:
        await connect_to_mongo()
        print('✅ MongoDB connected successfully')
        
        # Test JWT token from frontend
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTk2MjE4NzMsInN1YiI6IjY4YjVjNDkzYjJhZGZkYjVjODlhMzdjNyJ9.6HfFGYcwpO4WL65UaYV2yQ-CzCqvtYpyEnrZc0gB9F0"
        
        print(f'🔍 Testing JWT token: {token[:50]}...')
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print(f'✅ JWT payload decoded: {payload}')
            
            user_id = payload.get("sub")
            print(f'🔍 User ID from token: {user_id}')
            
            # Check if user exists
            user = await db.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                print(f'✅ User found: {user["email"]} - Active: {user.get("is_active", False)}')
            else:
                print(f'❌ User not found in database')
                
        except jwt.ExpiredSignatureError:
            print('❌ JWT token has expired')
        except jwt.InvalidTokenError as e:
            print(f'❌ Invalid JWT token: {e}')
        except Exception as e:
            print(f'❌ JWT decode error: {e}')
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_auth())