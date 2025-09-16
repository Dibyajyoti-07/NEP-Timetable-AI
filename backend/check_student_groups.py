import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import db, connect_to_mongo, close_mongo_connection
from bson import ObjectId

async def check_student_groups():
    """Check student groups data format"""
    try:
        print("🔍 Checking Student Groups Data...")
        
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Check all student groups
        groups = await db.db.student_groups.find({}).to_list(None)
        print(f"\n👥 All Student Groups ({len(groups)}):")
        for group in groups:
            print(f"   - ID: {group['_id']}")
            print(f"     Name: {group.get('name', 'N/A')}")
            print(f"     Program ID: {group.get('program_id', 'N/A')} (Type: {type(group.get('program_id', 'N/A'))})")
            print(f"     Year: {group.get('year', 'N/A')}")
            print(f"     Semester: {group.get('semester', 'N/A')}")
            print(f"     Section: {group.get('section', 'N/A')}")
            print(f"     Strength: {group.get('student_strength', 'N/A')}")
            print()
        
        # Test different query formats
        target_program_id = "68b5c517e73858dcb11d37e4"
        
        print(f"🎯 Testing queries for Program ID: {target_program_id}")
        
        # Query with string
        groups_string = await db.db.student_groups.find({"program_id": target_program_id}).to_list(None)
        print(f"   String query result: {len(groups_string)} groups")
        
        # Query with ObjectId
        groups_objectid = await db.db.student_groups.find({"program_id": ObjectId(target_program_id)}).to_list(None)
        print(f"   ObjectId query result: {len(groups_objectid)} groups")
        
        # Check if any groups have this program_id in any format
        print(f"\n🔍 Groups that might match:")
        for group in groups:
            program_id_val = group.get('program_id')
            if str(program_id_val) == target_program_id:
                print(f"   - Found match: {group.get('name', 'N/A')} (program_id: {program_id_val})")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()
        print("🔌 Disconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(check_student_groups())