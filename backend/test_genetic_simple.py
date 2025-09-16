#!/usr/bin/env python3
"""
Simple test for the Genetic Algorithm Timetable Generator
Tests the genetic algorithm by calling the API endpoint directly
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb import connect_to_mongo, close_mongo_connection, db
from app.services.genetic_algorithm.genetic_timetable_generator import GeneticTimetableGenerator
from bson import ObjectId

async def test_genetic_algorithm():
    """
    Test the genetic algorithm timetable generator
    """
    print("\n🧬 Testing Genetic Algorithm Timetable Generator")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB successfully!")
        
        # Test parameters
        program_id = "68b5c517e73858dcb11d37e4"
        semester = 5
        academic_year = "2024-25"
        
        print(f"\n📋 Test Parameters:")
        print(f"   • Program ID: {program_id}")
        print(f"   • Semester: {semester}")
        print(f"   • Academic Year: {academic_year}")
        
        # Verify program exists
        program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
        if not program:
            print(f"❌ Program not found: {program_id}")
            return False
        
        print(f"✅ Program found: {program.get('name', 'N/A')}")
        
        # Check available data directly from database
        courses = await db.db.courses.find({
            "program_id": ObjectId(program_id),
            "semester": semester,
            "is_active": True
        }).to_list(None)
        
        faculty = await db.db.faculty.find({}).to_list(None)
        rooms = await db.db.rooms.find({"is_active": True}).to_list(None)
        groups = await db.db.student_groups.find({
            "program_id": ObjectId(program_id)
        }).to_list(None)
        
        print(f"\n📊 Available Data:")
        print(f"   • Courses: {len(courses)}")
        print(f"   • Faculty: {len(faculty)}")
        print(f"   • Rooms: {len(rooms)}")
        print(f"   • Student Groups: {len(groups)}")
        
        if len(courses) == 0:
            print("❌ No courses found for the specified program and semester")
            return False
        
        if len(faculty) == 0:
            print("❌ No faculty found")
            return False
        
        if len(rooms) == 0:
            print("❌ No rooms found")
            return False
        
        # Create genetic algorithm generator with small parameters for testing
        print("\n🚀 Initializing Genetic Algorithm Generator...")
        generator = GeneticTimetableGenerator(
            population_size=20,  # Small for testing
            generations=10,      # Small for testing
            mutation_rate=0.15,
            crossover_rate=0.8
        )
        
        print(f"   • Population Size: {generator.population_size}")
        print(f"   • Generations: {generator.generations}")
        print(f"   • Mutation Rate: {generator.mutation_rate}")
        print(f"   • Crossover Rate: {generator.crossover_rate}")
        
        # Generate timetable
        print("\n⚡ Starting timetable generation...")
        start_time = datetime.now()
        
        result = await generator.generate_timetable(
            program_id=program_id,
            semester=semester,
            academic_year=academic_year
        )
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"\n📈 Generation Results:")
        print(f"   • Success: {result.get('success', False)}")
        print(f"   • Generation Time: {generation_time:.2f} seconds")
        print(f"   • Best Fitness Score: {result.get('best_fitness_score', 'N/A')}")
        print(f"   • Generations Completed: {result.get('generations_completed', 'N/A')}")
        print(f"   • Timetable Entries: {len(result.get('timetable_entries', []))}")
        print(f"   • Total Classes Scheduled: {result.get('total_classes_scheduled', 'N/A')}")
        
        if result.get('success'):
            print("\n✅ GENETIC ALGORITHM TEST PASSED!")
            
            # Show sample timetable entries
            timetable_entries = result.get('timetable_entries', [])
            if timetable_entries:
                print(f"\n📋 Sample Timetable Entries (first 3):")
                for i, entry in enumerate(timetable_entries[:3]):
                    print(f"   {i+1}. Course: {entry.get('course_id', 'N/A')[:8]}...")
                    print(f"      Faculty: {entry.get('faculty_id', 'N/A')[:8]}...")
                    print(f"      Room: {entry.get('room_id', 'N/A')[:8]}...")
                    print(f"      Time: {entry.get('time_slot', {}).get('day', 'N/A')} {entry.get('time_slot', {}).get('start_time', 'N/A')}-{entry.get('time_slot', {}).get('end_time', 'N/A')}")
                    print(f"      Type: {entry.get('session_type', 'N/A')}")
                    print()
            
            # Save detailed results
            results_file = f"genetic_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"📄 Detailed results saved to: {results_file}")
            return True
        else:
            print("\n❌ GENETIC ALGORITHM TEST FAILED!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n💥 Test crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await close_mongo_connection()
        print("\n🔌 Database connection closed.")

async def main():
    """
    Main test function
    """
    print("🧬 Starting Simple Genetic Algorithm Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_genetic_algorithm()
    
    if success:
        print(f"\n🎉 GENETIC ALGORITHM TEST COMPLETED SUCCESSFULLY! ✅")
        print("The genetic algorithm timetable generator is working correctly.")
        return 0
    else:
        print(f"\n❌ GENETIC ALGORITHM TEST FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)