import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

async def reset_admin_password():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client['timetable_db']
    
    # Hash the new password using bcrypt directly
    new_password = "admin123"
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update the admin user
    result = await db.users.update_one(
        {"email": "admin@example.com"},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    if result.modified_count > 0:
        print(f"✓ Successfully reset password for admin@example.com to: {new_password}")
        print(f"✓ You can now login with:")
        print(f"  Email: admin@example.com")
        print(f"  Password: {new_password}")
    else:
        print("✗ Failed to update password (user might not exist)")
    
    client.close()

asyncio.run(reset_admin_password())
