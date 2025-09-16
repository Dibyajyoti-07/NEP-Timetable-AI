#!/usr/bin/env python3
"""
Direct backend test - bypassing API authentication
Tests the advanced generator service directly with database data
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator, SchedulingRules
from app.db.mongodb import db, connect_to_mongo, close_mongo_connection
from bson import ObjectId

async def test_direct_generation():
    """Test the advanced generator directly with database data"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("[INFO] Connected to MongoDB")
        
        # Get a program from database
        programs = await db.db.programs.find().to_list(length=10)
        if not programs:
            print("[ERROR] No programs found in database")
            return False
            
        program = programs[0]
        program_id = str(program['_id'])
        print(f"[INFO] Using program: {program.get('name', 'Unknown')} (ID: {program_id})")
        
        # Create academic setup (similar to API defaults)
        academic_setup = {
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
                "start_time": "08:00",
                "end_time": "17:00", 
                "slot_duration": 50,
                "break_duration": 10,
                "lunch_break": True,
                "lunch_start": "13:00",
                "lunch_end": "14:00"
            },
            "constraints": {
                "max_periods_per_day": 8,
                "max_consecutive_hours": 3,
                "min_break_between_subjects": 1,
                "avoid_first_last_slot": False,
                "balance_workload": True,
                "prefer_morning_slots": False
            }
        }
        
        print("[INFO] Creating scheduling rules from database...")
        rules = await SchedulingRules.from_database_with_setup(program_id, academic_setup)
        
        print("[INFO] Starting advanced timetable generation...")
        generator = AdvancedTimetableGenerator(rules)
        
        # Setup the courses and resources (this loads the data)
        generator.setup_cse_ai_ml_courses()
        generator.setup_groups_and_resources()
        
        print(f"[INFO] Found {len(generator.courses)} courses")
        print(f"[INFO] Found {len(generator.rooms)} rooms")
        print(f"[INFO] Found {len(generator.faculty)} faculty members")
        print(f"[INFO] Found {len(generator.groups)} student groups")
        
        if not generator.courses:
            print("[ERROR] No courses found for this program")
            return False
            
        result = generator.generate_timetable()
        
        if result['success']:
            print(f"[SUCCESS] Generated timetable with {len(result['schedule'])} sessions")
            print(f"[INFO] Score: {result.get('score', 'N/A')}")
            
            # Show first few sessions
            print("\n[INFO] Sample sessions:")
            for i, session in enumerate(result['schedule'][:5]):
                print(f"  {i+1}. {session['course_code']} - {session['day']} {session['time_slot']} - Room: {session['room_id']}")
            
            if len(result['schedule']) > 5:
                print(f"  ... and {len(result['schedule']) - 5} more sessions")
                
            return True
        else:
            print(f"[ERROR] Generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_mongo_connection()
        print("[INFO] Database connection closed")

if __name__ == "__main__":
    success = asyncio.run(test_direct_generation())
    print(f"\n[RESULT] Backend test {'PASSED' if success else 'FAILED'}")