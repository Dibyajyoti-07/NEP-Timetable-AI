#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo
from app.services.timetable.advanced_generator import AdvancedTimetableGenerator

async def test_generation():
    """Test timetable generation with debug output"""
    print("🔧 Testing Advanced Timetable Generation with Debug Output")
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
        },
        "constraints": {
            "max_periods_per_day": 8,
            "max_consecutive_hours": 3,
            "min_break_between_subjects": 1,
            "avoid_first_last_slot": False,
            "balance_workload": True,
            "faculty_preferences": True
        }
    }
    
    try:
        # Create generator instance
        generator = AdvancedTimetableGenerator()
        
        # Load data from database
        print("\n📊 Loading data from database...")
        await generator.load_from_database_with_setup(program_id, semester, academic_setup)
        
        # Initialize occupancy tracking
        print("\n⚙️ Initializing occupancy tracking...")
        generator.initialize_occupancy_tracking()
        
        # Generate timetable
        print("\n🚀 Starting timetable generation...")
        result = generator.generate_timetable()
        
        if result["success"]:
            print("\n✅ TIMETABLE GENERATION SUCCESSFUL!")
            print(f"📊 Optimization Score: {result['score']}")
            
            # Display statistics
            stats = result["statistics"]
            print(f"\n📈 STATISTICS:")
            print(f"   • Total Sessions: {stats['total_sessions']}")
            print(f"   • Lab Sessions: {stats['lab_sessions']}")
            print(f"   • Theory Sessions: {stats['theory_sessions']}")
            print(f"   • Total Hours: {stats['total_hours']:.1f}")
        else:
            print("\n❌ TIMETABLE GENERATION FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())