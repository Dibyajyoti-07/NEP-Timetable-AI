#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import db, connect_to_mongo
from app.services.timetable.generator import TimetableGenerator
from app.services.timetable.simple_generator import SimpleTimetableGenerator
from bson import ObjectId

async def test_ai_generation():
    """Test AI timetable generation with detailed error reporting"""
    try:
        await connect_to_mongo()
        print("Connected to database")
        
        program_id = "68b5c517e73858dcb11d37e4"
        semester = 1
        academic_year = "2024-25"
        created_by = "68b5c493b2adfdb5c89a37c7"  # admin user ID
        
        print(f"\n🧪 Testing AI Timetable Generation")
        print(f"Program ID: {program_id}")
        print(f"Semester: {semester}")
        print(f"Academic Year: {academic_year}")
        
        # Test 1: Simple Generator
        print("\n🔧 Testing Simple Generator...")
        try:
            simple_generator = SimpleTimetableGenerator()
            simple_result = await simple_generator.generate_timetable(
                program_id=program_id,
                semester=semester,
                academic_year=academic_year,
                created_by=created_by
            )
            
            if simple_result["success"]:
                print("✅ Simple Generator: SUCCESS")
                print(f"   Timetable ID: {simple_result['timetable_id']}")
                print(f"   Message: {simple_result['message']}")
            else:
                print("❌ Simple Generator: FAILED")
                print(f"   Error: {simple_result['error']}")
                
        except Exception as e:
            print(f"❌ Simple Generator: EXCEPTION - {str(e)}")
        
        # Test 2: Advanced Generator
        print("\n🤖 Testing Advanced Generator...")
        try:
            generator = TimetableGenerator()
            result = await generator.generate_timetable(
                program_id=program_id,
                semester=semester,
                academic_year=academic_year,
                created_by=created_by
            )
            
            print("✅ Advanced Generator: SUCCESS")
            print(f"   Timetable ID: {result.get('_id', 'N/A')}")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Entries: {len(result.get('entries', []))}")
            
        except Exception as e:
            print(f"❌ Advanced Generator: EXCEPTION - {str(e)}")
            print("\n🔍 Detailed Error Analysis:")
            
            # Check data availability
            courses = await db.db.courses.find({"program_id": ObjectId(program_id)}).to_list(length=None)
            faculty = await db.db.faculty.find({}).to_list(length=None)
            rooms = await db.db.rooms.find({}).to_list(length=None)
            groups = await db.db.student_groups.find({"program_id": ObjectId(program_id)}).to_list(length=None)
            
            print(f"   📚 Courses available: {len(courses)}")
            print(f"   👨‍🏫 Faculty available: {len(faculty)}")
            print(f"   🏫 Rooms available: {len(rooms)}")
            print(f"   👥 Student groups: {len(groups)}")
            
            if len(groups) == 0:
                print("\n⚠️  ISSUE FOUND: No student groups for this program!")
                print("   This is likely causing the generation failure.")
                
                # Create a sample student group
                print("\n🔧 Creating sample student group...")
                group_doc = {
                    "name": "CSE AI-ML Batch 2024",
                    "program_id": ObjectId(program_id),
                    "semester": semester,
                    "size": 60,
                    "type": "main",
                    "is_active": True,
                    "created_at": datetime.datetime.utcnow()
                }
                
                result = await db.db.student_groups.insert_one(group_doc)
                print(f"   ✅ Created group with ID: {result.inserted_id}")
                
                # Try generation again
                print("\n🔄 Retrying generation with student group...")
                try:
                    result = await generator.generate_timetable(
                        program_id=program_id,
                        semester=semester,
                        academic_year=academic_year,
                        created_by=created_by
                    )
                    
                    print("✅ Advanced Generator (Retry): SUCCESS")
                    print(f"   Timetable ID: {result.get('_id', 'N/A')}")
                    print(f"   Title: {result.get('title', 'N/A')}")
                    print(f"   Entries: {len(result.get('entries', []))}")
                    
                except Exception as retry_error:
                    print(f"❌ Advanced Generator (Retry): STILL FAILED - {str(retry_error)}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import datetime
    asyncio.run(test_ai_generation())