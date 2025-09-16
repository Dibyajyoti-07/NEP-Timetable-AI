#!/usr/bin/env python3
"""
Final diagnostic script to identify and fix remaining issues
causing timetable generation failures.
"""

import asyncio
import sys
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import db, connect_to_mongo

PROGRAM_ID = "68b5c517e73858dcb11d37e4"
SEMESTER = 5

async def check_database_state():
    """Check the current state of all database collections"""
    print("🔍 Checking Database State")
    print("=" * 50)
    
    # Check programs
    programs = await db.db.programs.find({}).to_list(None)
    print(f"📚 Programs: {len(programs)}")
    target_program = await db.db.programs.find_one({"_id": ObjectId(PROGRAM_ID)})
    if target_program:
        print(f"   ✅ Target program found: {target_program['name']}")
    else:
        print(f"   ❌ Target program {PROGRAM_ID} not found")
        return False
    
    # Check courses
    courses = await db.db.courses.find({"program_id": ObjectId(PROGRAM_ID), "semester": SEMESTER}).to_list(None)
    print(f"📖 Courses for program {PROGRAM_ID}, semester {SEMESTER}: {len(courses)}")
    if courses:
        total_theory_hours = sum(c.get('theory_hours', 0) for c in courses)
        total_practical_hours = sum(c.get('practical_hours', 0) for c in courses)
        print(f"   📊 Total theory hours: {total_theory_hours}")
        print(f"   📊 Total practical hours: {total_practical_hours}")
        print(f"   📊 Total weekly hours: {total_theory_hours + total_practical_hours}")
        
        # Check faculty assignments
        courses_with_faculty = [c for c in courses if c.get('faculty_id')]
        print(f"   👨‍🏫 Courses with faculty: {len(courses_with_faculty)}/{len(courses)}")
    else:
        print("   ❌ No courses found")
        return False
    
    # Check faculty
    faculty = await db.db.faculty.find({}).to_list(None)
    print(f"👨‍🏫 Faculty: {len(faculty)}")
    if faculty:
        faculty_with_subjects = [f for f in faculty if f.get('subjects')]
        print(f"   📚 Faculty with subjects: {len(faculty_with_subjects)}/{len(faculty)}")
    
    # Check student groups
    student_groups = await db.db.student_groups.find({"program_id": PROGRAM_ID}).to_list(None)
    print(f"👥 Student groups for program: {len(student_groups)}")
    if student_groups:
        for sg in student_groups:
            print(f"   📝 Group: {sg['name']}, Size: {sg.get('size', 'N/A')}, Courses: {len(sg.get('course_ids', []))}")
    
    # Check rooms
    rooms = await db.db.rooms.find({}).to_list(None)
    print(f"🏢 Rooms: {len(rooms)}")
    if rooms:
        lab_rooms = [r for r in rooms if r.get('is_lab', False)]
        regular_rooms = [r for r in rooms if not r.get('is_lab', False)]
        print(f"   🧪 Lab rooms: {len(lab_rooms)}")
        print(f"   📚 Regular rooms: {len(regular_rooms)}")
    
    return True

async def analyze_constraints():
    """Analyze constraint violations"""
    print("\n⚖️ Analyzing Constraints")
    print("=" * 50)
    
    # Get courses and calculate time requirements
    courses = await db.db.courses.find({"program_id": ObjectId(PROGRAM_ID), "semester": SEMESTER}).to_list(None)
    total_hours = sum(c.get('theory_hours', 0) + c.get('practical_hours', 0) for c in courses)
    
    # Calculate available time slots
    working_days = 5  # Mon-Fri
    hours_per_day = 8  # 9 AM to 5 PM with breaks
    available_slots = working_days * hours_per_day
    
    print(f"📊 Total course hours needed: {total_hours}")
    print(f"📊 Available time slots: {available_slots}")
    print(f"📊 Utilization: {(total_hours/available_slots)*100:.1f}%")
    
    if total_hours > available_slots:
        print("❌ CONSTRAINT VIOLATION: Not enough time slots")
        print(f"   Need to reduce hours by: {total_hours - available_slots}")
        return False
    
    # Check room constraints
    rooms = await db.db.rooms.find({}).to_list(None)
    student_groups = await db.db.student_groups.find({"program_id": PROGRAM_ID}).to_list(None)
    
    if len(rooms) < len(student_groups):
        print(f"⚠️  WARNING: More student groups ({len(student_groups)}) than rooms ({len(rooms)})")
    
    # Check faculty workload
    faculty = await db.db.faculty.find({}).to_list(None)
    if faculty:
        avg_hours_per_faculty = total_hours / len(faculty)
        max_hours_per_week = 20  # Reasonable limit
        print(f"📊 Average hours per faculty: {avg_hours_per_faculty:.1f}")
        if avg_hours_per_faculty > max_hours_per_week:
            print(f"❌ CONSTRAINT VIOLATION: Faculty overload (max {max_hours_per_week} hours)")
            return False
    
    return True

async def fix_critical_issues():
    """Fix critical issues that prevent timetable generation"""
    print("\n🔧 Fixing Critical Issues")
    print("=" * 50)
    
    # Ensure all courses have proper hours
    courses = await db.db.courses.find({"program_id": ObjectId(PROGRAM_ID), "semester": SEMESTER}).to_list(None)
    
    for course in courses:
        updates = {}
        
        # Ensure theory_hours and practical_hours exist
        if 'theory_hours' not in course or course['theory_hours'] == 0:
            if course.get('type') == 'Practical':
                updates['theory_hours'] = 0
                updates['practical_hours'] = course.get('practical_hours', 3)
            else:
                updates['theory_hours'] = course.get('theory_hours', 3)
                updates['practical_hours'] = 0
        
        # Ensure faculty assignment
        if 'faculty_id' not in course or not course['faculty_id']:
            # Get a random faculty member
            faculty = await db.db.faculty.find_one({})
            if faculty:
                updates['faculty_id'] = faculty['_id']
        
        if updates:
            await db.db.courses.update_one(
                {"_id": course['_id']},
                {"$set": updates}
            )
            print(f"   ✅ Updated course {course['code']}: {updates}")
    
    # Ensure student groups have proper size
    student_groups = await db.db.student_groups.find({"program_id": PROGRAM_ID}).to_list(None)
    for sg in student_groups:
        if 'size' not in sg:
            await db.db.student_groups.update_one(
                {"_id": sg['_id']},
                {"$set": {"size": 30}}
            )
            print(f"   ✅ Added size to student group {sg['name']}")
    
    print("✅ Critical issues fixed")

async def test_minimal_generation():
    """Test with minimal constraints to see if basic generation works"""
    print("\n🧪 Testing Minimal Generation")
    print("=" * 50)
    
    try:
        from app.services.timetable.advanced_generator import AdvancedTimetableGenerator
        
        # Create minimal generation request
        request_data = {
            "program_id": PROGRAM_ID,
            "semester": SEMESTER,
            "academic_year": "2024-25",
            "working_days": {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": False,
                "sunday": False
            },
            "time_slots": {
                "start_time": "09:00",
                "end_time": "15:00",  # Reduced end time
                "slot_duration": 60,  # Increased slot duration
                "break_duration": 5,  # Reduced break
                "lunch_break": False  # No lunch break
            },
            "constraints": {
                "max_periods_per_day": 6,  # Reduced
                "max_consecutive_hours": 4,  # Increased
                "min_break_between_subjects": 0,  # No break requirement
                "avoid_first_last_slot": False,
                "balance_workload": False,  # Disabled
                "prefer_morning_slots": False
            }
        }
        
        generator = AdvancedTimetableGenerator()
        result = await generator.generate_timetable(request_data)
        
        if result and 'schedule' in result:
            print(f"✅ Minimal generation successful: {len(result['schedule'])} sessions")
            return True
        else:
            print("❌ Minimal generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

async def main():
    print("🚀 Final Diagnostic and Fix Script")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        print("✅ Database connected")
        
        # Check database state
        if not await check_database_state():
            print("❌ Database state check failed")
            return
        
        # Analyze constraints
        if not await analyze_constraints():
            print("❌ Constraint analysis failed")
        
        # Fix critical issues
        await fix_critical_issues()
        
        # Test minimal generation
        success = await test_minimal_generation()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 Diagnostic completed successfully!")
            print("✅ Basic timetable generation is working")
        else:
            print("❌ Issues remain - further debugging needed")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())