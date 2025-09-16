#!/usr/bin/env python3
"""
Test script for the Genetic Algorithm Timetable Generator
Tests the genetic algorithm-based scheduling with CSE AI & ML course requirements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.timetable.genetic_generator import GeneticTimetableGenerator
import json
from datetime import datetime
import time

def test_genetic_generator():
    """
    Test the genetic algorithm timetable generator
    """
    print("\n🧬 Testing Genetic Algorithm Timetable Generator")
    print("=" * 60)
    
    # Create generator with test parameters
    generator = GeneticTimetableGenerator(
        population_size=20,  # Smaller for testing
        generations=30,      # Fewer generations for testing
        mutation_rate=0.15,
        crossover_rate=0.8,
        elite_size=3,
        tournament_size=3
    )
    
    print("\n⚙️ Generator Parameters:")
    print(f"   • Population Size: {generator.population_size}")
    print(f"   • Generations: {generator.generations}")
    print(f"   • Mutation Rate: {generator.mutation_rate}")
    print(f"   • Crossover Rate: {generator.crossover_rate}")
    print(f"   • Elite Size: {generator.elite_size}")
    print(f"   • Tournament Size: {generator.tournament_size}")
    
    print("\n🚀 Starting genetic algorithm timetable generation...")
    start_time = time.time()
    
    result = generator.generate_timetable()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    if result["success"]:
        print("\n✅ GENETIC ALGORITHM GENERATION SUCCESSFUL!")
        print(f"🧬 Final Fitness Score: {result['fitness']:.2f}")
        print(f"⚠️ Constraint Violations: {result['constraint_violations']}")
        print(f"🔄 Generations Run: {result['generations_run']}")
        print(f"⏱️ Total Time: {total_time:.2f} seconds")
        print(f"⏱️ Algorithm Time: {result['time_taken']:.2f} seconds")
        
        # Display statistics
        stats = result["statistics"]
        print(f"\n📈 STATISTICS:")
        print(f"   • Total Sessions: {stats['total_sessions']}")
        print(f"   • Lab Sessions: {stats['lab_sessions']}")
        print(f"   • Theory Sessions: {stats['theory_sessions']}")
        print(f"   • Total Hours: {stats['total_hours']:.1f}")
        
        if "sessions_per_day" in stats:
            print(f"   • Sessions per day: {stats['sessions_per_day']}")
        
        # Display validation results
        validation = result["validation"]
        print(f"\n✅ VALIDATION RESULTS:")
        print(f"   • Valid: {validation['valid']}")
        if validation["errors"]:
            print(f"   • Errors: {len(validation['errors'])}")
            for error in validation["errors"][:5]:  # Show first 5 errors
                print(f"     - {error}")
            if len(validation["errors"]) > 5:
                print(f"     ... and {len(validation['errors']) - 5} more errors")
        if validation["warnings"]:
            print(f"   • Warnings: {len(validation['warnings'])}")
            for warning in validation["warnings"][:3]:  # Show first 3 warnings
                print(f"     - {warning}")
            if len(validation["warnings"]) > 3:
                print(f"     ... and {len(validation['warnings']) - 3} more warnings")
        
        # Display evolution statistics
        if "generation_stats" in result and result["generation_stats"]:
            print(f"\n📊 EVOLUTION PROGRESS:")
            gen_stats = result["generation_stats"]
            
            # Show first, middle, and last generations
            key_generations = []
            if len(gen_stats) > 0:
                key_generations.append(gen_stats[0])  # First
            if len(gen_stats) > 2:
                key_generations.append(gen_stats[len(gen_stats)//2])  # Middle
            if len(gen_stats) > 1:
                key_generations.append(gen_stats[-1])  # Last
            
            for gen_stat in key_generations:
                gen_num = gen_stat['generation']
                best_fit = gen_stat['best_fitness']
                avg_fit = gen_stat['avg_fitness']
                violations = gen_stat['best_violations']
                print(f"   • Gen {gen_num:3d}: Best={best_fit:6.1f}, Avg={avg_fit:6.1f}, Violations={violations}")
            
            if len(gen_stats) > 3:
                print(f"   ... (showing {len(key_generations)} of {len(gen_stats)} generations)")
        
        # Display sample schedule
        print(f"\n📅 SAMPLE SCHEDULE (first 10 sessions):")
        schedule = result["schedule"]
        
        if schedule:
            print(f"{'Day':<10} {'Time':<12} {'Course':<15} {'Type':<8} {'Room':<10} {'Group':<8}")
            print("-" * 75)
            
            for i, session in enumerate(schedule[:10]):
                day = session["day"]
                time_str = f"{session['start_time']}-{session['end_time']}"
                course = session["course_code"]
                session_type = "LAB" if session.get("is_lab", False) else "THEORY"
                room = session["room"]
                group = session["group"]
                
                print(f"{day:<10} {time_str:<12} {course:<15} {session_type:<8} {room:<10} {group:<8}")
            
            if len(schedule) > 10:
                print(f"... and {len(schedule) - 10} more sessions")
        else:
            print("   No sessions generated")
        
        # Performance comparison
        sessions_per_second = len(schedule) / total_time if total_time > 0 else 0
        print(f"\n⚡ PERFORMANCE:")
        print(f"   • Sessions per second: {sessions_per_second:.1f}")
        print(f"   • Fitness improvement: {result['generation_stats'][-1]['best_fitness'] - result['generation_stats'][0]['best_fitness']:.1f}" if result.get('generation_stats') else "   • No evolution data")
        
        return True
    else:
        print("\n❌ GENETIC ALGORITHM GENERATION FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Show evolution stats even on failure
        if "generation_stats" in result and result["generation_stats"]:
            print(f"\n📊 EVOLUTION PROGRESS (before failure):")
            for gen_stat in result["generation_stats"][-5:]:  # Last 5 generations
                gen_num = gen_stat['generation']
                best_fit = gen_stat['best_fitness']
                avg_fit = gen_stat['avg_fitness']
                violations = gen_stat['best_violations']
                print(f"   • Gen {gen_num:3d}: Best={best_fit:6.1f}, Avg={avg_fit:6.1f}, Violations={violations}")
        
        return False

def compare_algorithms():
    """
    Compare genetic algorithm with the basic advanced generator
    """
    print("\n🔬 ALGORITHM COMPARISON")
    print("=" * 60)
    
    # Test genetic algorithm
    print("\n🧬 Testing Genetic Algorithm...")
    genetic_start = time.time()
    
    genetic_generator = GeneticTimetableGenerator(
        population_size=30,
        generations=50,
        mutation_rate=0.15,
        crossover_rate=0.8
    )
    genetic_result = genetic_generator.generate_timetable()
    genetic_time = time.time() - genetic_start
    
    # Test basic advanced generator
    print("\n🔧 Testing Basic Advanced Algorithm...")
    from app.services.timetable.advanced_generator import AdvancedTimetableGenerator
    
    basic_start = time.time()
    basic_generator = AdvancedTimetableGenerator()
    basic_result = basic_generator.generate_timetable()
    basic_time = time.time() - basic_start
    
    # Compare results
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"{'Metric':<25} {'Genetic':<15} {'Basic':<15} {'Winner':<10}")
    print("-" * 70)
    
    # Success rate
    genetic_success = genetic_result["success"]
    basic_success = basic_result["success"]
    success_winner = "Genetic" if genetic_success and not basic_success else "Basic" if basic_success and not genetic_success else "Tie"
    print(f"{'Success':<25} {str(genetic_success):<15} {str(basic_success):<15} {success_winner:<10}")
    
    if genetic_success and basic_success:
        # Score comparison
        genetic_score = genetic_result.get('fitness', 0)
        basic_score = basic_result.get('score', 0)
        score_winner = "Genetic" if genetic_score > basic_score else "Basic" if basic_score > genetic_score else "Tie"
        print(f"{'Score/Fitness':<25} {genetic_score:<15.1f} {basic_score:<15.1f} {score_winner:<10}")
        
        # Sessions scheduled
        genetic_sessions = len(genetic_result["schedule"])
        basic_sessions = len(basic_result["schedule"])
        sessions_winner = "Genetic" if genetic_sessions > basic_sessions else "Basic" if basic_sessions > genetic_sessions else "Tie"
        print(f"{'Sessions Scheduled':<25} {genetic_sessions:<15} {basic_sessions:<15} {sessions_winner:<10}")
        
        # Constraint violations
        genetic_violations = genetic_result.get('constraint_violations', 0)
        basic_violations = len(basic_result["validation"].get("errors", []))
        violations_winner = "Genetic" if genetic_violations < basic_violations else "Basic" if basic_violations < genetic_violations else "Tie"
        print(f"{'Constraint Violations':<25} {genetic_violations:<15} {basic_violations:<15} {violations_winner:<10}")
    
    # Time comparison
    time_winner = "Genetic" if genetic_time < basic_time else "Basic" if basic_time < genetic_time else "Tie"
    print(f"{'Generation Time (s)':<25} {genetic_time:<15.2f} {basic_time:<15.2f} {time_winner:<10}")
    
    print(f"\n🏆 OVERALL WINNER: ", end="")
    if genetic_success and not basic_success:
        print("🧬 Genetic Algorithm (only successful method)")
    elif basic_success and not genetic_success:
        print("🔧 Basic Advanced Algorithm (only successful method)")
    elif genetic_success and basic_success:
        genetic_total_score = (genetic_score if genetic_score > basic_score else 0) + \
                            (1 if genetic_sessions >= basic_sessions else 0) + \
                            (1 if genetic_violations <= basic_violations else 0)
        basic_total_score = (1 if basic_score >= genetic_score else 0) + \
                          (1 if basic_sessions >= genetic_sessions else 0) + \
                          (1 if basic_violations <= genetic_violations else 0)
        
        if genetic_total_score > basic_total_score:
            print("🧬 Genetic Algorithm (better overall performance)")
        elif basic_total_score > genetic_total_score:
            print("🔧 Basic Advanced Algorithm (better overall performance)")
        else:
            print("🤝 Tie (both algorithms performed similarly)")
    else:
        print("❌ Both algorithms failed")

def main():
    """
    Main test function
    """
    print("🧬 Starting Genetic Algorithm Timetable Generator Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Genetic algorithm generation
        success = test_genetic_generator()
        
        if success:
            print(f"\n🎉 GENETIC ALGORITHM TEST PASSED! ✅")
            
            # Test 2: Algorithm comparison
            compare_algorithms()
            
            print(f"\n🎉 ALL TESTS COMPLETED! ✅")
            print("The genetic algorithm timetable generator is working correctly.")
        else:
            print(f"\n❌ GENETIC ALGORITHM TEST FAILED!")
            return 1
            
    except Exception as e:
        print(f"\n💥 TEST CRASHED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)