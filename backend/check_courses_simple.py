import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo, db
from bson import ObjectId

async def check_courses():
    """Check if there are any courses in the database"""
    try:
        print("🔧 Checking courses in database...")
        
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to database")
        
        # Count total courses
        total_courses = await db.db.courses.count_documents({})
        print(f"📚 Total courses in database: {total_courses}")
        
        if total_courses > 0:
            # Get a sample course
            sample_course = await db.db.courses.find_one({})
            print(f"📋 Sample course: {sample_course}")
            
            # Check course structure
            if sample_course:
                print(f"🔍 Course keys: {list(sample_course.keys())}")
                if '_id' in sample_course:
                    print(f"🆔 Course ID: {sample_course['_id']}")
                if 'program_id' in sample_course:
                    print(f"📚 Program ID: {sample_course['program_id']}")
        else:
            print("❌ No courses found in database")
            
        return total_courses
        
    except Exception as e:
        print(f"❌ Error checking courses: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(check_courses())
    if result is not None:
        print(f"\n🎉 Check completed: {result} courses found")
    else:
        print("\n💥 Check failed")