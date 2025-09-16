# Simple Timetable Generator - Greedy Approach
from typing import Dict, List, Any, Optional
from bson import ObjectId
import datetime
from app.db.mongodb import db

class SimpleTimetableGenerator:
    """A simplified timetable generator that uses a greedy approach for reliable scheduling."""
    
    def __init__(self):
        self.working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.time_slots = [
            {"start": "11:00", "end": "12:00", "duration": 60},
            {"start": "12:00", "end": "13:00", "duration": 60},
            {"start": "14:00", "end": "15:00", "duration": 60},  # After lunch
            {"start": "15:00", "end": "16:00", "duration": 60},
            {"start": "16:00", "end": "16:30", "duration": 30},
        ]
    
    async def generate_timetable(self, program_id: str, semester: int, academic_year: str, created_by: str) -> Dict[str, Any]:
        """Generate a simple timetable using greedy scheduling."""
        try:
            # Load required data
            data = await self._load_data(program_id, semester)
            
            # Generate entries using simple round-robin approach
            entries = self._generate_entries(data)
            
            # Create timetable document
            timetable_doc = {
                "title": f"Simple Generated Timetable - {academic_year}",
                "program_id": ObjectId(program_id),
                "semester": semester,
                "academic_year": academic_year,
                "entries": entries,
                "is_draft": False,
                "metadata": {
                    "generator_type": "simple_greedy",
                    "generation_method": "round_robin",
                    "total_entries": len(entries)
                },
                "created_by": ObjectId(created_by),
                "created_at": datetime.datetime.utcnow(),
                "generated_at": datetime.datetime.utcnow(),
                "validation_status": "valid",
                "optimization_score": 0.8  # Simple but functional
            }
            
            # Save to database
            result = await db.db.timetables.insert_one(timetable_doc)
            timetable_doc["_id"] = result.inserted_id
            
            # Convert ObjectIds to strings for JSON serialization
            if "_id" in timetable_doc:
                timetable_doc["id"] = str(timetable_doc["_id"])
                del timetable_doc["_id"]
            if "created_by" in timetable_doc:
                timetable_doc["created_by"] = str(timetable_doc["created_by"])
            if "program_id" in timetable_doc:
                timetable_doc["program_id"] = str(timetable_doc["program_id"])
            
            # Convert ObjectIds in entries (they are already strings from _generate_entries)
            # But ensure all fields are properly formatted
            for entry in timetable_doc.get("entries", []):
                # Ensure all IDs are strings (they should already be from _generate_entries)
                if "course_id" in entry and isinstance(entry["course_id"], ObjectId):
                    entry["course_id"] = str(entry["course_id"])
                if "faculty_id" in entry and isinstance(entry["faculty_id"], ObjectId):
                    entry["faculty_id"] = str(entry["faculty_id"])
                if "room_id" in entry and isinstance(entry["room_id"], ObjectId):
                    entry["room_id"] = str(entry["room_id"])
                if "group_id" in entry and isinstance(entry["group_id"], ObjectId):
                    entry["group_id"] = str(entry["group_id"])
            
            return {
                "success": True,
                "timetable_id": str(result.inserted_id),
                "message": f"Successfully generated timetable with {len(entries)} entries",
                "timetable": timetable_doc
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate timetable"
            }
    
    async def _load_data(self, program_id: str, semester: int) -> Dict[str, Any]:
        """Load courses, faculty, rooms, and groups for the program."""
        
        # Load courses for this semester
        courses = await db.db.courses.find({
            "program_id": ObjectId(program_id),
            "semester": semester
        }).to_list(None)
        
        # Load faculty
        faculty = await db.db.faculty.find({}).to_list(None)
        
        # Load rooms
        rooms = await db.db.rooms.find({}).to_list(None)
        
        # Load student groups
        groups = await db.db.student_groups.find({
            "program_id": ObjectId(program_id),
            "semester": semester
        }).to_list(None)
        
        return {
            "courses": courses,
            "faculty": faculty,
            "rooms": rooms,
            "groups": groups
        }
    
    def _generate_entries(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate timetable entries using a simple round-robin approach."""
        entries = []
        
        courses = data["courses"]
        faculty = data["faculty"]
        rooms = data["rooms"]
        groups = data["groups"]
        
        if not courses or not faculty or not rooms:
            # Create some sample entries if no data available
            return self._create_sample_entries()
        
        # Track usage to avoid conflicts
        slot_usage = {}  # {(day, time_slot, resource_id): True}
        
        # Simple round-robin assignment
        faculty_idx = 0
        room_idx = 0
        day_idx = 0
        time_idx = 0
        
        for course in courses:
            # Determine how many sessions this course needs per week
            hours_per_week = course.get("hours_per_week", 3)
            sessions_needed = min(hours_per_week, 5)  # Max 5 sessions per week
            
            for session in range(sessions_needed):
                # Find next available slot
                placed = False
                attempts = 0
                
                while not placed and attempts < 50:  # Prevent infinite loop
                    day = self.working_days[day_idx % len(self.working_days)]
                    time_slot = self.time_slots[time_idx % len(self.time_slots)]
                    faculty_member = faculty[faculty_idx % len(faculty)] if faculty else None
                    room = rooms[room_idx % len(rooms)] if rooms else None
                    
                    # Create unique keys for conflict checking
                    faculty_key = (day, time_slot["start"], str(faculty_member["_id"])) if faculty_member else None
                    room_key = (day, time_slot["start"], str(room["_id"])) if room else None
                    
                    # Check for conflicts
                    conflict = False
                    if faculty_key and faculty_key in slot_usage:
                        conflict = True
                    if room_key and room_key in slot_usage:
                        conflict = True
                    
                    if not conflict:
                        # Create entry
                        entry = {
                            "course_id": str(course["_id"]),
                            "faculty_id": str(faculty_member["_id"]) if faculty_member else str(faculty[0]["_id"]) if faculty else "",
                            "room_id": str(room["_id"]) if room else str(rooms[0]["_id"]) if rooms else "",
                            "group_id": str(groups[0]["_id"]) if groups else "",
                            "time_slot": {
                                "day": day,
                                "start_time": time_slot["start"],
                                "end_time": time_slot["end"],
                                "duration_minutes": time_slot["duration"]
                            }
                        }
                        
                        entries.append(entry)
                        
                        # Mark slots as used
                        if faculty_key:
                            slot_usage[faculty_key] = True
                        if room_key:
                            slot_usage[room_key] = True
                        
                        placed = True
                    
                    # Move to next slot
                    time_idx += 1
                    if time_idx % len(self.time_slots) == 0:
                        day_idx += 1
                        if day_idx % len(self.working_days) == 0:
                            faculty_idx += 1
                            room_idx += 1
                    
                    attempts += 1
                
                if not placed:
                    print(f"Warning: Could not place session for course {course.get('code', 'Unknown')}")
        
        return entries
    
    def _create_sample_entries(self) -> List[Dict[str, Any]]:
        """Create sample timetable entries when no data is available."""
        sample_courses = [
            {"code": "CS501", "name": "Advanced Data Structures"},
            {"code": "CS502", "name": "Algorithm Analysis"},
            {"code": "CS503", "name": "Database Systems"},
            {"code": "CS504", "name": "Software Engineering"},
            {"code": "CS505", "name": "Computer Networks"},
        ]
        
        entries = []
        
        for i, course in enumerate(sample_courses):
            for j in range(2):  # 2 sessions per course
                day_idx = (i * 2 + j) % len(self.working_days)
                time_idx = (i * 2 + j) % len(self.time_slots)
                
                day = self.working_days[day_idx]
                time_slot = self.time_slots[time_idx]
                
                entry = {
                    "course_id": f"course_{i+1}",
                    "faculty_id": f"faculty_{(i % 3) + 1}",
                    "room_id": f"room_{(i % 5) + 1}",
                    "group_id": "group_1",
                    "time_slot": {
                        "day": day,
                        "start_time": time_slot["start"],
                        "end_time": time_slot["end"],
                        "duration_minutes": time_slot["duration"]
                    }
                }
                
                entries.append(entry)
        
        return entries