import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo, db
from bson import ObjectId

async def debug_courses_endpoint():
    """Debug the courses endpoint issue"""
    try:
        print("🔧 Debugging courses endpoint...")
        
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to database")
        
        # Test program ID
        program_id = "68b5c517e73858dcb11d37e4"
        semester = 5
        
        print(f"🔍 Testing program ID: {program_id}")
        print(f"🔍 Testing semester: {semester}")
        
        # Check if program exists
        try:
            program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
            if program:
                print(f"✅ Program found: {program.get('name', 'Unknown')}")
            else:
                print("❌ Program not found")
                return
        except Exception as e:
            print(f"❌ Error checking program: {e}")
            return
        
        # Build filter query for courses
        filter_query = {"program_id": ObjectId(program_id)}
        if semester is not None:
            filter_query["semester"] = semester
        
        print(f"🔍 Filter query: {filter_query}")
        
        # Query courses from database
        try:
            courses = await db.db.courses.find(filter_query).to_list(length=None)
            print(f"📚 Found {len(courses)} courses")
            
            if courses:
                print("📋 Sample course:")
                sample = courses[0].copy()
                if "_id" in sample:
                    sample["_id"] = str(sample["_id"])
                if "program_id" in sample:
                    sample["program_id"] = str(sample["program_id"])
                print(f"   {sample}")
            
            # Test the conversion process
            for course in courses:
                if "_id" in course:
                    course["id"] = str(course["_id"])
                    del course["_id"]
                if "program_id" in course and isinstance(course["program_id"], ObjectId):
                    course["program_id"] = str(course["program_id"])
            
            print(f"✅ Successfully processed {len(courses)} courses")
            return courses
            
        except Exception as e:
            print(f"❌ Error querying courses: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(debug_courses_endpoint())
    if result is not None:
        print(f"\n🎉 Debug completed successfully with {len(result)} courses")
    else:
        print("\n💥 Debug failed")