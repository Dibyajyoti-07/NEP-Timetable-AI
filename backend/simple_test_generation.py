import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.timetable.advanced_generator import AdvancedTimetableGenerator, SchedulingRules
from app.db.mongodb import db, connect_to_mongo
from bson import ObjectId

async def simple_test():
    # Connect to database
    await connect_to_mongo()
    
    # Use the known program ID and semester from previous debug
    program_id = "68b5c517e73858dcb11d37e4"
    semester = 5
    
    print(f"Testing generation for Program {program_id}, Semester {semester}")
    
    # Create academic setup
    academic_setup = {
        "working_days": {
            "Monday": True,
            "Tuesday": True,
            "Wednesday": True,
            "Thursday": True,
            "Friday": True,
            "Saturday": False,
            "Sunday": False
        },
        "time_slots": {
            "start_time": "09:00",
            "end_time": "17:00",
            "break_duration": 60,
            "lunch_start": "13:00",
            "lunch_end": "14:00"
        },
        "constraints": {
            "max_periods_per_day": 6,
            "max_continuous_periods": 3,
            "min_break_between_periods": 10
        }
    }
    
    try:
        print("Creating scheduling rules...")
        rules = await SchedulingRules.from_database_with_setup(program_id, academic_setup)
        print("Rules created successfully")
        
        print("Creating generator...")
        generator = AdvancedTimetableGenerator(rules)
        print("Generator created successfully")
        
        print("Loading data from database...")
        await generator.load_from_database_with_setup(program_id, semester, academic_setup)
        print(f"Data loaded: {len(generator.courses)} courses, {len(generator.groups)} groups, {len(generator.rooms)} rooms, {len(generator.faculty)} faculty")
        
        print("Starting generation...")
        result = generator.generate_timetable(program_id, semester)
        
        print(f"Generation result: Success = {result['success']}")
        if result['success']:
            print(f"Generated {len(result['schedule'])} schedule entries with score {result['score']}")
            
            # Write result to file
            with open('generation_result.txt', 'w') as f:
                f.write(f"Success: {result['success']}\n")
                f.write(f"Score: {result['score']}\n")
                f.write(f"Schedule entries: {len(result['schedule'])}\n")
                f.write(f"Attempts made: {result.get('attempts_made', 'Unknown')}\n")
                f.write(f"Message: {result.get('message', 'No message')}\n")
                
                f.write("\nFirst 5 schedule entries:\n")
                for i, entry in enumerate(result['schedule'][:5]):
                    f.write(f"{i+1}. {entry}\n")
                    
        else:
            print(f"Generation failed: {result['error']}")
            with open('generation_result.txt', 'w') as f:
                f.write(f"Success: {result['success']}\n")
                f.write(f"Error: {result['error']}\n")
                
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        
        with open('generation_result.txt', 'w') as f:
            f.write(f"Exception: {str(e)}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
    
    print("Test complete. Check generation_result.txt for details.")

if __name__ == "__main__":
    asyncio.run(simple_test())