#!/usr/bin/env python3
"""
Test the genetic algorithm timetable generation endpoint
"""

import asyncio
import requests
import json
from datetime import datetime

async def test_genetic_endpoint():
    """Test the genetic algorithm timetable generation endpoint"""
    base_url = "http://localhost:8001/api/v1"
    
    # Read admin token
    try:
        with open('admin_token.txt', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("❌ admin_token.txt not found")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔐 Testing genetic algorithm endpoint...")
    print(f"📡 Base URL: {base_url}")
    
    # Get programs first
    try:
        response = requests.get(f"{base_url}/programs", headers=headers)
        if response.status_code == 200:
            programs_response = response.json()
            print(f"📋 Programs response: {programs_response}")
            
            # Handle different response structures
            programs = []
            if isinstance(programs_response, list):
                programs = programs_response
            elif isinstance(programs_response, dict) and 'programs' in programs_response:
                programs = programs_response['programs']
            elif isinstance(programs_response, dict) and 'data' in programs_response:
                programs = programs_response['data']
            
            if programs and len(programs) > 0:
                program = programs[0]
                program_id = program.get('_id') or program.get('id')
                print(f"✅ Found {len(programs)} programs, using: {program_id}")
            else:
                print("❌ No programs found")
                return
        else:
            print(f"❌ Failed to get programs: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting programs: {e}")
        return
    
    # Test genetic algorithm generation
    print("\n🧬 Testing genetic algorithm generation...")
    
    try:
        genetic_data = {
            "program_id": program_id,
            "semester": 5,
            "academic_year": "2025-26",
            "title": "Test Genetic Timetable",
            "population_size": 20,
            "generations": 10,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8
        }
        
        response = requests.post(
            f"{base_url}/genetic-timetable/generate",
            headers=headers,
            json=genetic_data
        )
        
        print(f"📊 Genetic API status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Genetic generation successful!")
            print(f"📋 Timetable ID: {result.get('timetable_id')}")
            print(f"🎯 Fitness Score: {result.get('fitness_score')}")
            print(f"📈 Generation Stats: {result.get('generation_stats')}")
            print(f"📊 Data Summary: {result.get('data_summary')}")
            
            # Check if entries are included in the response
            entries = result.get('entries', [])
            print(f"\n📚 Entries in response: {len(entries)}")
            
            if entries:
                print(f"\n📋 Sample entries from response:")
                for i, entry in enumerate(entries[:3]):
                    time_slot = entry.get('time_slot', {})
                    print(f"   Entry {i+1}: {time_slot.get('day')} {time_slot.get('start_time')}-{time_slot.get('end_time')} - Course: {entry.get('course_id')}")
            else:
                print("❌ No entries found in response")
                
            # Also try to retrieve the timetable separately
            timetable_id = result.get('timetable_id')
            if timetable_id:
                print(f"\n🔍 Also trying to retrieve timetable separately...")
                timetable_response = requests.get(
                    f"{base_url}/timetables/{timetable_id}",
                    headers=headers
                )
                
                if timetable_response.status_code == 200:
                    timetable_data = timetable_response.json()
                    db_entries = timetable_data.get('entries', [])
                    print(f"📚 Retrieved timetable from DB with {len(db_entries)} entries")
                else:
                    print(f"❌ Failed to retrieve timetable from DB: {timetable_response.text}")
            
        else:
            print(f"❌ Genetic generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in genetic generation: {e}")

if __name__ == "__main__":
    asyncio.run(test_genetic_endpoint())