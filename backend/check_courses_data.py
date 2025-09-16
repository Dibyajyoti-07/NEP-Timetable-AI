import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import db, connect_to_mongo, close_mongo_connection
from bson import ObjectId

async def check_courses_data():
    """Check what courses exist in the database"""
    try:
        print("🔍 Checking Courses Data...")
        
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Check all programs
        programs = await db.db.programs.find({}).to_list(None)
        print(f"\n📋 Available Programs ({len(programs)}):")
        for program in programs:
            print(f"   - ID: {program['_id']} | Name: {program.get('name', 'N/A')} | Code: {program.get('code', 'N/A')}")
        
        # Check all courses
        courses = await db.db.courses.find({}).to_list(None)
        print(f"\n📚 Available Courses ({len(courses)}):")
        for course in courses:
            print(f"   - ID: {course['_id']} | Code: {course.get('code', 'N/A')} | Name: {course.get('name', 'N/A')}")
            print(f"     Program ID: {course.get('program_id', 'N/A')} | Semester: {course.get('semester', 'N/A')}")
        
        # Check specific program courses
        target_program_id = "68b5c517e73858dcb11d37e4"
        print(f"\n🎯 Courses for Program ID {target_program_id}:")
        program_courses = await db.db.courses.find({"program_id": target_program_id}).to_list(None)
        print(f"   Total courses for this program: {len(program_courses)}")
        
        if program_courses:
            semester_counts = {}
            for course in program_courses:
                semester = course.get('semester', 'Unknown')
                if semester not in semester_counts:
                    semester_counts[semester] = 0
                semester_counts[semester] += 1
                print(f"   - {course.get('code', 'N/A')}: {course.get('name', 'N/A')} (Semester {semester})")
            
            print(f"\n📊 Courses by Semester:")
            for semester, count in sorted(semester_counts.items()):
                print(f"   - Semester {semester}: {count} courses")
        
        # Check if courses have different program_id format
        print(f"\n🔍 Checking for courses with ObjectId format...")
        try:
            object_id_courses = await db.db.courses.find({"program_id": ObjectId(target_program_id)}).to_list(None)
            print(f"   Courses with ObjectId format: {len(object_id_courses)}")
            for course in object_id_courses:
                print(f"   - {course.get('code', 'N/A')}: {course.get('name', 'N/A')} (Semester {course.get('semester', 'N/A')})")
        except Exception as e:
            print(f"   Error checking ObjectId format: {e}")
        
        # Check student groups
        student_groups = await db.db.student_groups.find({"program_id": target_program_id}).to_list(None)
        print(f"\n👥 Student Groups for Program ID {target_program_id}: {len(student_groups)}")
        for group in student_groups:
            print(f"   - {group.get('name', 'N/A')} (Year {group.get('year', 'N/A')}, Semester {group.get('semester', 'N/A')})")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()
        print("🔌 Disconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(check_courses_data())