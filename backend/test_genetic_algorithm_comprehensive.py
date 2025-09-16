#!/usr/bin/env python3
"""
Comprehensive test for the genetic algorithm timetable generation system.
This test validates the complete workflow from data collection to timetable generation.
"""

import asyncio
import sys
import os
from datetime import datetime
import json
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.genetic_algorithm.genetic_timetable_generator import GeneticTimetableGenerator
from app.services.genetic_algorithm.data_collector import TimetableDataCollector
from app.db.mongodb import db, connect_to_mongo, close_mongo_connection
from bson import ObjectId

class GeneticAlgorithmTester:
    """Comprehensive tester for genetic algorithm timetable generation"""
    
    def __init__(self):
        self.generator = GeneticTimetableGenerator()
        self.data_collector = TimetableDataCollector()
        self.test_results = {}
        
    async def setup_test_data(self) -> Dict[str, str]:
        """Setup test data in the database if not exists"""
        print("\n=== Setting up test data ===")
        
        # Create test program
        test_program = {
            "name": "Computer Science Engineering",
            "code": "CSE",
            "duration_years": 4,
            "credits_required": 160,
            "department": "Computer Science",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        # Check if program exists
        existing_program = await db.db.programs.find_one({"code": "CSE"})
        if not existing_program:
            result = await db.db.programs.insert_one(test_program)
            program_id = str(result.inserted_id)
            print(f"Created test program with ID: {program_id}")
        else:
            program_id = str(existing_program["_id"])
            print(f"Using existing program with ID: {program_id}")
        
        # Create test courses
        test_courses = [
            {
                "name": "Data Structures and Algorithms",
                "code": "CSE201",
                "credits": 4,
                "semester": 3,
                "course_type": "theory",
                "hours_per_week": 4,
                "min_session_duration": 1,
                "max_session_duration": 2,
                "program_id": ObjectId(program_id),
                "prerequisites": [],
                "is_active": True
            },
            {
                "name": "Database Management Systems",
                "code": "CSE301",
                "credits": 3,
                "semester": 3,
                "course_type": "theory",
                "hours_per_week": 3,
                "min_session_duration": 1,
                "max_session_duration": 2,
                "program_id": ObjectId(program_id),
                "prerequisites": [],
                "is_active": True
            },
            {
                "name": "Computer Networks Lab",
                "code": "CSE302L",
                "credits": 2,
                "semester": 3,
                "course_type": "lab",
                "hours_per_week": 3,
                "min_session_duration": 2,
                "max_session_duration": 3,
                "program_id": ObjectId(program_id),
                "prerequisites": [],
                "is_active": True
            }
        ]
        
        # Insert courses if they don't exist
        for course in test_courses:
            existing_course = await db.db.courses.find_one({"code": course["code"]})
            if not existing_course:
                await db.db.courses.insert_one(course)
                print(f"Created course: {course['code']}")
        
        # Create test faculty
        test_faculty = [
            {
                "name": "Dr. Alice Johnson",
                "email": "alice.johnson@university.edu",
                "department": "Computer Science",
                "subjects_taught": ["CSE201", "CSE301"],
                "max_hours_per_week": 20,
                "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "specialization": "Algorithms and Data Structures",
                "experience_years": 10
            },
            {
                "name": "Prof. Bob Smith",
                "email": "bob.smith@university.edu",
                "department": "Computer Science",
                "subjects_taught": ["CSE301", "CSE302L"],
                "max_hours_per_week": 18,
                "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "specialization": "Database Systems",
                "experience_years": 8
            }
        ]
        
        for faculty in test_faculty:
            existing_faculty = await db.db.faculty.find_one({"email": faculty["email"]})
            if not existing_faculty:
                await db.db.faculty.insert_one(faculty)
                print(f"Created faculty: {faculty['name']}")
        
        # Create test student groups
        test_groups = [
            {
                "name": "CSE-3A",
                "program_id": program_id,
                "semester": "3",
                "year": 2,
                "section": "A",
                "type": "regular",
                "student_strength": 45,
                "course_ids": ["CSE201", "CSE301", "CSE302L"]
            },
            {
                "name": "CSE-3B",
                "program_id": program_id,
                "semester": "3",
                "year": 2,
                "section": "B",
                "type": "regular",
                "student_strength": 42,
                "course_ids": ["CSE201", "CSE301", "CSE302L"]
            }
        ]
        
        for group in test_groups:
            existing_group = await db.db.student_groups.find_one({"name": group["name"]})
            if not existing_group:
                await db.db.student_groups.insert_one(group)
                print(f"Created student group: {group['name']}")
        
        # Create test rooms
        test_rooms = [
            {
                "name": "Room 101",
                "room_number": "101",
                "type": "classroom",
                "capacity": 50,
                "facilities": ["projector", "whiteboard", "ac"],
                "location": "Block A",
                "floor": 1,
                "building": "Main Building",
                "is_active": True
            },
            {
                "name": "Lab 201",
                "room_number": "201",
                "type": "lab",
                "capacity": 30,
                "facilities": ["computers", "projector", "ac"],
                "location": "Block B",
                "floor": 2,
                "building": "Lab Building",
                "is_active": True
            },
            {
                "name": "Room 102",
                "room_number": "102",
                "type": "classroom",
                "capacity": 45,
                "facilities": ["projector", "whiteboard"],
                "location": "Block A",
                "floor": 1,
                "building": "Main Building",
                "is_active": True
            }
        ]
        
        for room in test_rooms:
            existing_room = await db.db.rooms.find_one({"room_number": room["room_number"]})
            if not existing_room:
                await db.db.rooms.insert_one(room)
                print(f"Created room: {room['name']}")
        
        print("Test data setup completed!")
        return {"program_id": program_id}
    
    async def test_data_collection(self, program_id: str) -> bool:
        """Test the data collection functionality"""
        print("\n=== Testing Data Collection ===")
        
        try:
            # Test individual data collection methods
            academic_setup = await self.data_collector.collect_academic_setup(program_id, 3, "2024-25")
            print(f"✓ Academic Setup: {academic_setup['program_name']}")
            
            courses = await self.data_collector.collect_courses(program_id, 3)
            print(f"✓ Courses collected: {len(courses)} courses")
            
            faculty = await self.data_collector.collect_faculty()
            print(f"✓ Faculty collected: {len(faculty)} faculty members")
            
            student_groups = await self.data_collector.collect_student_groups(program_id, 3)
            print(f"✓ Student Groups collected: {len(student_groups)} groups")
            
            rooms = await self.data_collector.collect_rooms()
            print(f"✓ Rooms collected: {len(rooms)} rooms")
            
            time_rules = self.data_collector.collect_time_and_rules()
            print(f"✓ Time rules collected")
            
            # Test complete data collection
            all_data = await self.data_collector.collect_all_data(program_id, 3, "2024-25")
            print(f"✓ Complete data collection successful")
            
            # Test data validation
            is_valid = await self.data_collector.validate_collected_data(all_data)
            print(f"✓ Data validation: {'PASSED' if is_valid else 'FAILED'}")
            
            # Test data summary
            summary = await self.data_collector.get_data_summary(all_data)
            print(f"✓ Data summary: {summary}")
            
            self.test_results['data_collection'] = {
                'status': 'PASSED',
                'courses_count': len(courses),
                'faculty_count': len(faculty),
                'groups_count': len(student_groups),
                'rooms_count': len(rooms),
                'validation_passed': is_valid,
                'summary': summary
            }
            
            return True
            
        except Exception as e:
            print(f"✗ Data collection failed: {str(e)}")
            self.test_results['data_collection'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    async def test_genetic_algorithm_components(self) -> bool:
        """Test individual genetic algorithm components"""
        print("\n=== Testing Genetic Algorithm Components ===")
        
        try:
            # Test time slot generation
            time_slots = self.generator.generate_time_slots()
            print(f"✓ Time slots generated: {len(time_slots)} slots")
            
            # Test chromosome creation (with mock data)
            mock_data = {
                'courses': [{'id': '1', 'hours_per_week': 4, 'course_type': 'theory'}],
                'faculty': [{'id': '1', 'max_hours_per_week': 20}],
                'student_groups': [{'id': '1', 'course_ids': ['1']}],
                'rooms': [{'id': '1', 'capacity': 50, 'type': 'classroom'}]
            }
            
            chromosome = self.generator.create_chromosome(mock_data, time_slots)
            print(f"✓ Chromosome created with {len(chromosome)} genes")
            
            # Test fitness calculation
            fitness = self.generator.calculate_fitness(chromosome, mock_data)
            print(f"✓ Fitness calculated: {fitness}")
            
            # Test genetic operators
            parent1 = chromosome
            parent2 = self.generator.create_chromosome(mock_data, time_slots)
            
            offspring1, offspring2 = self.generator.crossover(parent1, parent2)
            print(f"✓ Crossover successful")
            
            mutated = self.generator.mutate(chromosome.copy(), mock_data, time_slots)
            print(f"✓ Mutation successful")
            
            self.test_results['genetic_components'] = {
                'status': 'PASSED',
                'time_slots_count': len(time_slots),
                'chromosome_genes': len(chromosome),
                'fitness_score': fitness
            }
            
            return True
            
        except Exception as e:
            print(f"✗ Genetic algorithm components test failed: {str(e)}")
            self.test_results['genetic_components'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    async def test_complete_generation(self, program_id: str) -> bool:
        """Test complete timetable generation"""
        print("\n=== Testing Complete Timetable Generation ===")
        
        try:
            start_time = datetime.now()
            
            # Set small parameters for testing
            self.generator.population_size = 20
            self.generator.generations = 10
            self.generator.mutation_rate = 0.1
            self.generator.crossover_rate = 0.8
            
            # Generate timetable with small parameters for testing
            result = await self.generator.generate_timetable(
                program_id=program_id,
                semester=3,
                academic_year="2024-25"
            )
            
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            print(f"✓ Timetable generation completed in {generation_time:.2f} seconds")
            print(f"✓ Best fitness achieved: {result.get('best_fitness_score', 'N/A')}")
            print(f"✓ Total generations: {result.get('generations_completed', 'N/A')}")
            print(f"✓ Timetable entries: {len(result.get('timetable_entries', []))}")
            
            # Validate the generated timetable
            timetable = result.get('timetable_entries', [])
            if timetable:
                print(f"✓ Sample timetable entry: {timetable[0]}")
            
            self.test_results['complete_generation'] = {
                'status': 'PASSED',
                'generation_time_seconds': generation_time,
                'best_fitness': result.get('best_fitness_score'),
                'generations_completed': result.get('generations_completed'),
                'timetable_entries_count': len(timetable),
                'sample_entry': timetable[0] if timetable else None
            }
            
            return True
            
        except Exception as e:
            print(f"✗ Complete generation test failed: {str(e)}")
            self.test_results['complete_generation'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("\n" + "="*60)
        print("    GENETIC ALGORITHM TIMETABLE GENERATION TEST")
        print("="*60)
        
        try:
            # Setup test data
            test_data = await self.setup_test_data()
            program_id = test_data['program_id']
            
            # Run individual tests
            data_collection_passed = await self.test_data_collection(program_id)
            components_passed = await self.test_genetic_algorithm_components()
            generation_passed = await self.test_complete_generation(program_id)
            
            # Overall results
            all_passed = data_collection_passed and components_passed and generation_passed
            
            self.test_results['overall'] = {
                'status': 'PASSED' if all_passed else 'FAILED',
                'data_collection': 'PASSED' if data_collection_passed else 'FAILED',
                'genetic_components': 'PASSED' if components_passed else 'FAILED',
                'complete_generation': 'PASSED' if generation_passed else 'FAILED',
                'test_timestamp': datetime.now().isoformat()
            }
            
            print("\n" + "="*60)
            print("                    TEST RESULTS SUMMARY")
            print("="*60)
            print(f"Data Collection:      {self.test_results['overall']['data_collection']}")
            print(f"Genetic Components:   {self.test_results['overall']['genetic_components']}")
            print(f"Complete Generation:  {self.test_results['overall']['complete_generation']}")
            print(f"Overall Status:       {self.test_results['overall']['status']}")
            print("="*60)
            
            return self.test_results
            
        except Exception as e:
            print(f"\n✗ Test suite failed: {str(e)}")
            self.test_results['overall'] = {
                'status': 'FAILED',
                'error': str(e),
                'test_timestamp': datetime.now().isoformat()
            }
            return self.test_results

async def main():
    """Main test function"""
    tester = GeneticAlgorithmTester()
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB successfully!")
        
        # Run all tests
        results = await tester.run_all_tests()
        
        # Save results to file
        results_file = f"genetic_algorithm_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed test results saved to: {results_file}")
        
        # Return appropriate exit code
        if results['overall']['status'] == 'PASSED':
            print("\n🎉 All tests PASSED! Genetic algorithm is working correctly.")
            return 0
        else:
            print("\n❌ Some tests FAILED. Check the results for details.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        return 1
    finally:
        # Close database connection
        await close_mongo_connection()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)