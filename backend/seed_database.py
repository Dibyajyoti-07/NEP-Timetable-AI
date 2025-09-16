#!/usr/bin/env python3
"""
Database seeding script for Timetable AI system.
This script populates the MongoDB database with sample data.
"""

import asyncio
from datetime import datetime, timezone
from bson import ObjectId
from app.db.mongodb import connect_to_mongo, db
from app.core.config import settings

# Sample data
SAMPLE_PROGRAMS = [
    {
        "_id": ObjectId("68b5c517e73858dcb11d37e4"),  # This matches the frontend program_id
        "name": "Computer Science and Engineering - AI & ML",
        "code": "CSE_AI_ML",
        "type": "B.Tech",
        "department": "Computer Science",
        "duration_years": 4,
        "total_semesters": 8,
        "credits_required": 160,
        "description": "Bachelor of Technology in Computer Science with specialization in AI & ML",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "_id": ObjectId("68b5c517e73858dcb11d37e5"),
        "name": "Electronics and Communication Engineering",
        "code": "ECE",
        "type": "B.Tech",
        "department": "Electronics",
        "duration_years": 4,
        "total_semesters": 8,
        "credits_required": 160,
        "description": "Bachelor of Technology in Electronics and Communication Engineering",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "_id": ObjectId("68b5c517e73858dcb11d37e6"),
        "name": "Mechanical Engineering",
        "code": "MECH",
        "type": "B.Tech",
        "department": "Mechanical",
        "duration_years": 4,
        "total_semesters": 8,
        "credits_required": 160,
        "description": "Bachelor of Technology in Mechanical Engineering",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_COURSES = [
    {
        "code": "CS501",
        "name": "Advanced Data Structures",
        "credits": 4,
        "type": "Core",
        "hours_per_week": 4,
        "min_per_session": 60,
        "semester": 5,
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "description": "Advanced concepts in data structures and algorithms",
        "is_lab": False,
        "lab_hours": 0,
        "is_active": True
    },
    {
        "code": "CS502",
        "name": "Machine Learning",
        "credits": 4,
        "type": "Core",
        "hours_per_week": 4,
        "min_per_session": 60,
        "semester": 5,
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "description": "Introduction to machine learning algorithms and techniques",
        "is_lab": False,
        "lab_hours": 0,
        "is_active": True
    },
    {
        "code": "CS503",
        "name": "Database Management Systems",
        "credits": 3,
        "type": "Core",
        "hours_per_week": 3,
        "min_per_session": 60,
        "semester": 5,
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "description": "Database design, implementation, and management",
        "is_lab": False,
        "lab_hours": 0,
        "is_active": True
    },
    {
        "code": "CS504L",
        "name": "Machine Learning Lab",
        "credits": 2,
        "type": "Lab",
        "hours_per_week": 3,
        "min_per_session": 90,
        "semester": 5,
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "description": "Practical implementation of machine learning algorithms",
        "is_lab": True,
        "lab_hours": 3,
        "is_active": True
    },
    {
        "code": "CS505L",
        "name": "Database Lab",
        "credits": 1,
        "type": "Lab",
        "hours_per_week": 2,
        "min_per_session": 90,
        "semester": 5,
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "description": "Hands-on database implementation and queries",
        "is_lab": True,
        "lab_hours": 2,
        "is_active": True
    },
    {
        "code": "CS506",
        "name": "Software Engineering",
        "credits": 3,
        "type": "Core",
        "hours_per_week": 3,
        "min_per_session": 60,
        "semester": 5,
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "description": "Software development lifecycle and methodologies",
        "is_lab": False,
        "lab_hours": 0,
        "is_active": True
    }
]

SAMPLE_ROOMS = [
    {
        "name": "A-101",
        "building": "Academic Block A",
        "floor": 1,
        "capacity": 60,
        "room_type": "Classroom",
        "facilities": ["Projector", "Whiteboard", "AC"],
        "is_lab": False,
        "is_accessible": True,
        "has_projector": True,
        "has_ac": True,
        "has_wifi": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "A-102",
        "building": "Academic Block A",
        "floor": 1,
        "capacity": 50,
        "room_type": "Classroom",
        "facilities": ["Projector", "Whiteboard"],
        "is_lab": False,
        "is_accessible": True,
        "has_projector": True,
        "has_ac": False,
        "has_wifi": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "Lab-301",
        "building": "Academic Block A",
        "floor": 3,
        "capacity": 30,
        "room_type": "Computer Lab",
        "facilities": ["Computers", "Projector", "AC"],
        "is_lab": True,
        "is_accessible": True,
        "has_projector": True,
        "has_ac": True,
        "has_wifi": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "Lab-302",
        "building": "Academic Block A",
        "floor": 3,
        "capacity": 25,
        "room_type": "Computer Lab",
        "facilities": ["Computers", "Projector"],
        "is_lab": True,
        "is_accessible": True,
        "has_projector": True,
        "has_ac": False,
        "has_wifi": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "B-201",
        "building": "Academic Block B",
        "floor": 2,
        "capacity": 80,
        "room_type": "Lecture Hall",
        "facilities": ["Projector", "Microphone", "AC"],
        "is_lab": False,
        "is_accessible": True,
        "has_projector": True,
        "has_ac": True,
        "has_wifi": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_FACULTY = [
    {
        "name": "Dr. Rajesh Kumar",
        "email": "rajesh.kumar@university.edu",
        "department": "Computer Science",
        "designation": "Professor",
        "specialization": ["Data Structures", "Algorithms"],
        "max_hours_per_week": 20,
        "preferred_time_slots": [],
        "unavailable_slots": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "Dr. Priya Sharma",
        "email": "priya.sharma@university.edu",
        "department": "Computer Science",
        "designation": "Associate Professor",
        "specialization": ["Machine Learning", "Artificial Intelligence"],
        "max_hours_per_week": 18,
        "preferred_time_slots": [],
        "unavailable_slots": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "Prof. Amit Singh",
        "email": "amit.singh@university.edu",
        "department": "Computer Science",
        "designation": "Assistant Professor",
        "specialization": ["Database Systems", "Data Mining"],
        "max_hours_per_week": 16,
        "preferred_time_slots": [],
        "unavailable_slots": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "Dr. Neha Gupta",
        "email": "neha.gupta@university.edu",
        "department": "Computer Science",
        "designation": "Assistant Professor",
        "specialization": ["Software Engineering", "Web Development"],
        "max_hours_per_week": 16,
        "preferred_time_slots": [],
        "unavailable_slots": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "Mr. Vikash Yadav",
        "email": "vikash.yadav@university.edu",
        "department": "Computer Science",
        "designation": "Lab Instructor",
        "specialization": ["Programming", "Lab Management"],
        "max_hours_per_week": 25,
        "preferred_time_slots": [],
        "unavailable_slots": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_STUDENT_GROUPS = [
    {
        "name": "CSE AI&ML Semester 5 - Group A",
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "semester": 5,
        "academic_year": "2025-26",
        "section": "A",
        "student_count": 45,
        "max_capacity": 50,
        "type": "regular",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "CSE AI&ML Semester 5 - Group B",
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "semester": 5,
        "academic_year": "2025-26",
        "section": "B",
        "student_count": 42,
        "max_capacity": 50,
        "type": "regular",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "CSE AI&ML Semester 5 - Lab Group A",
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "semester": 5,
        "academic_year": "2025-26",
        "section": "A",
        "student_count": 22,
        "max_capacity": 25,
        "type": "lab",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "name": "CSE AI&ML Semester 5 - Lab Group B",
        "program_id": ObjectId("68b5c517e73858dcb11d37e4"),
        "semester": 5,
        "academic_year": "2025-26",
        "section": "B",
        "student_count": 23,
        "max_capacity": 25,
        "type": "lab",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_TIME_RULES = {
    "name": "Standard Academic Schedule",
    "description": "Standard time slots for academic sessions",
    "time_slots": [
        {"start_time": "11:00", "end_time": "12:00", "duration_minutes": 60},
        {"start_time": "12:00", "end_time": "13:00", "duration_minutes": 60},
        {"start_time": "14:00", "end_time": "15:00", "duration_minutes": 60},
        {"start_time": "15:00", "end_time": "16:00", "duration_minutes": 60},
        {"start_time": "16:00", "end_time": "16:30", "duration_minutes": 30}
    ],
    "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "break_times": [
        {"start_time": "11:00", "end_time": "11:15", "name": "Tea Break"},
        {"start_time": "13:15", "end_time": "14:00", "name": "Lunch Break"}
    ],
    "max_hours_per_day": 7,
    "max_consecutive_hours": 3,
    "is_active": True,
    "created_at": datetime.now(timezone.utc)
}

async def clear_collections():
    """Clear existing data from collections"""
    collections = ['programs', 'courses', 'rooms', 'faculty', 'student_groups', 'time_rules']
    
    for collection_name in collections:
        try:
            result = await db.db[collection_name].delete_many({})
            print(f"✅ Cleared {result.deleted_count} documents from {collection_name}")
        except Exception as e:
            print(f"❌ Error clearing {collection_name}: {e}")

async def seed_programs():
    """Seed programs collection"""
    try:
        result = await db.db.programs.insert_many(SAMPLE_PROGRAMS)
        print(f"✅ Inserted {len(result.inserted_ids)} programs")
        return True
    except Exception as e:
        print(f"❌ Error seeding programs: {e}")
        return False

async def seed_courses():
    """Seed courses collection"""
    try:
        result = await db.db.courses.insert_many(SAMPLE_COURSES)
        print(f"✅ Inserted {len(result.inserted_ids)} courses")
        return True
    except Exception as e:
        print(f"❌ Error seeding courses: {e}")
        return False

async def seed_rooms():
    """Seed rooms collection"""
    try:
        result = await db.db.rooms.insert_many(SAMPLE_ROOMS)
        print(f"✅ Inserted {len(result.inserted_ids)} rooms")
        return True
    except Exception as e:
        print(f"❌ Error seeding rooms: {e}")
        return False

async def seed_faculty():
    """Seed faculty collection"""
    try:
        result = await db.db.faculty.insert_many(SAMPLE_FACULTY)
        print(f"✅ Inserted {len(result.inserted_ids)} faculty members")
        return True
    except Exception as e:
        print(f"❌ Error seeding faculty: {e}")
        return False

async def seed_student_groups():
    """Seed student_groups collection"""
    try:
        # Get course IDs from database
        courses = await db.db.courses.find({"program_id": ObjectId("68b5c517e73858dcb11d37e4"), "semester": 5}).to_list(length=None)
        theory_course_ids = [c["_id"] for c in courses if not c.get("is_lab", False)]
        lab_course_ids = [c["_id"] for c in courses if c.get("is_lab", False)]
        
        # Update student groups with course assignments
        updated_groups = []
        for group in SAMPLE_STUDENT_GROUPS:
            group_copy = group.copy()
            if group["type"] == "regular":
                group_copy["course_ids"] = theory_course_ids
            elif group["type"] == "lab":
                group_copy["course_ids"] = lab_course_ids
            updated_groups.append(group_copy)
        
        result = await db.db.student_groups.insert_many(updated_groups)
        print(f"✅ Inserted {len(result.inserted_ids)} student groups")
        print(f"📚 Theory courses assigned: {len(theory_course_ids)}")
        print(f"🧪 Lab courses assigned: {len(lab_course_ids)}")
        return True
    except Exception as e:
        print(f"❌ Error seeding student groups: {e}")
        return False

async def seed_time_rules():
    """Seed time_rules collection"""
    try:
        result = await db.db.time_rules.insert_one(SAMPLE_TIME_RULES)
        print(f"✅ Inserted time rules with ID: {result.inserted_id}")
        return True
    except Exception as e:
        print(f"❌ Error seeding time rules: {e}")
        return False

async def verify_data():
    """Verify that data was inserted correctly"""
    collections = {
        'programs': SAMPLE_PROGRAMS,
        'courses': SAMPLE_COURSES,
        'rooms': SAMPLE_ROOMS,
        'faculty': SAMPLE_FACULTY,
        'student_groups': SAMPLE_STUDENT_GROUPS
    }
    
    print("\n📊 Verification Results:")
    for collection_name, sample_data in collections.items():
        try:
            count = await db.db[collection_name].count_documents({})
            expected = len(sample_data)
            status = "✅" if count == expected else "❌"
            print(f"{status} {collection_name}: {count}/{expected} documents")
        except Exception as e:
            print(f"❌ Error verifying {collection_name}: {e}")
    
    # Check time_rules separately
    try:
        count = await db.db.time_rules.count_documents({})
        status = "✅" if count >= 1 else "❌"
        print(f"{status} time_rules: {count}/1 documents")
    except Exception as e:
        print(f"❌ Error verifying time_rules: {e}")

async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print(f"📍 MongoDB URL: {settings.MONGODB_URL[:50]}...")
    print(f"📍 Database: {settings.DATABASE_NAME}")
    
    # Connect to database
    await connect_to_mongo()
    
    if db.db is None:
        print("❌ Failed to connect to database")
        return
    
    print("\n🗑️ Clearing existing data...")
    await clear_collections()
    
    print("\n📝 Seeding new data...")
    success = True
    success &= await seed_programs()
    success &= await seed_courses()
    success &= await seed_rooms()
    success &= await seed_faculty()
    success &= await seed_student_groups()
    success &= await seed_time_rules()
    
    if success:
        print("\n✅ Database seeding completed successfully!")
        await verify_data()
        print("\n🎯 You can now test the constraint-based timetable generation.")
        print("   Program ID: 68b5c517e73858dcb11d37e4")
        print("   Semester: 5")
        print("   Academic Year: 2025-26")
    else:
        print("\n❌ Database seeding completed with errors.")

if __name__ == "__main__":
    asyncio.run(main())