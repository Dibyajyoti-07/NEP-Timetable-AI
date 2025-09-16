#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo
from app.services.timetable.advanced_generator import AdvancedTimetableGenerator

async def test_full_generation():
    """Test the complete timetable generation process"""
    print("🔧 Testing Full Timetable Generation")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    # Test parameters
    program_id = "68b5c517e73858dcb11d37e4"
    semester = 5
    academic_setup = {
        "working_days": {
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": False,
            "saturday": False,
            "sunday": False
        },
        "time_settings": {
            "start_time": "09:00",
            "end_time": "17:00",
            "slot_duration": 50,
            "break_duration": 10,
            "lunch_break": True,
            "lunch_start": "13:00",
            "lunch_end": "14:00"
        }
    }
    
    try:
        # Create generator instance
        generator = AdvancedTimetableGenerator()
        
        # Load data from database
        print("\n📊 Loading data from database...")
        await generator.load_from_database_with_setup(program_id, semester, academic_setup)
        
        # Show loaded data summary
        lab_courses = [c for c in generator.courses if c.is_lab]
        theory_courses = [c for c in generator.courses if not c.is_lab]
        print(f"\n📚 Loaded: {len(theory_courses)} theory courses, {len(lab_courses)} lab courses")
        
        # Show course details
        print("\nTheory courses:")
        for course in theory_courses:
            sessions = course.get_session_structure()
            print(f"  {course.code}: {course.hours_per_week}h/week -> {sessions}")
        
        print("\nLab courses:")
        for course in lab_courses:
            sessions = course.get_session_structure()
            print(f"  {course.code}: {course.hours_per_week}h/week -> {sessions}")
        
        # Test the full generation process
        print("\n🚀 Starting full timetable generation...")
        result = generator.generate_timetable(program_id, semester)
        
        print(f"\n📋 Generation Result:")
        print(f"  Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"  Score: {result.get('score', 'N/A')}")
            print(f"  Total sessions: {len(result.get('schedule', []))}")
            print(f"  Attempts made: {result.get('attempts_made', 'N/A')}")
            
            # Show validation results
            validation = result.get('validation', {})
            errors = validation.get('errors', [])
            warnings = validation.get('warnings', [])
            
            print(f"\n✅ Validation:")
            print(f"  Errors: {len(errors)}")
            print(f"  Warnings: {len(warnings)}")
            
            if errors:
                print("\n❌ Errors:")
                for error in errors:
                    print(f"    - {error}")
            
            if warnings:
                print("\n⚠️ Warnings:")
                for warning in warnings:
                    print(f"    - {warning}")
            
            # Show first few schedule entries
            schedule = result.get('schedule', [])
            if schedule:
                print(f"\n📅 First 10 schedule entries:")
                for i, entry in enumerate(schedule[:10]):
                    print(f"  {i+1}. {entry['day']} {entry['start_time']}-{entry['end_time']}: {entry['course_code']} ({entry['group']}) in {entry['room']}")
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"  Error: {error_msg}")
        
        # Write results to file
        with open('full_generation_results.txt', 'w') as f:
            f.write(f"Success: {result.get('success', False)}\n")
            f.write(f"Theory courses: {len(theory_courses)}\n")
            f.write(f"Lab courses: {len(lab_courses)}\n")
            
            if result.get('success'):
                f.write(f"Score: {result.get('score', 'N/A')}\n")
                f.write(f"Total sessions: {len(result.get('schedule', []))}\n")
                
                schedule = result.get('schedule', [])
                f.write("\nSchedule:\n")
                for entry in schedule:
                    f.write(f"  {entry['day']} {entry['start_time']}-{entry['end_time']}: {entry['course_code']} ({entry['group']}) in {entry['room']}\n")
            else:
                f.write(f"Error: {result.get('error', 'Unknown error')}\n")
        
        print("\nResults written to full_generation_results.txt")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_generation())