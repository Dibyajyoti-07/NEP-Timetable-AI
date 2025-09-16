from typing import List, Dict, Any, Optional
from app.db.mongodb import db
from bson import ObjectId
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

class TimetableDataCollector:
    """Collects data from all six tabs for genetic algorithm timetable generation"""
    
    def __init__(self):
        pass
    
    async def collect_all_data(self, program_id: str, semester: int, academic_year: str) -> Dict[str, Any]:
        """Collect data from all six tabs for timetable generation"""
        try:
            data = {
                "academic_setup": await self.collect_academic_setup(program_id, semester, academic_year),
                "courses": await self.collect_courses(program_id, semester),
                "faculty": await self.collect_faculty(),
                "student_groups": await self.collect_student_groups(program_id, semester),
                "rooms": await self.collect_rooms(),
                "time_rules": self.collect_time_and_rules()
            }
            
            logger.info(f"Successfully collected data for program {program_id}, semester {semester}")
            return data
            
        except Exception as e:
            logger.error(f"Error collecting timetable data: {str(e)}")
            raise
    
    async def collect_academic_setup(self, program_id: str, semester: int, academic_year: str) -> Dict[str, Any]:
        """Collect Academic Setup data"""
        try:
            program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
            if not program:
                raise ValueError(f"Program with ID {program_id} not found")
            
            # Default working days configuration (can be customized)
            working_days = {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": False,
                "sunday": False
            }
            
            return {
                "program_id": program_id,
                "program_name": program.get("name"),
                "semester": semester,
                "academic_year": academic_year,
                "duration_years": program.get("duration_years"),
                "credits_required": program.get("credits_required"),
                "department": program.get("department"),
                "working_days": working_days,
                "total_working_days": sum(working_days.values())
            }
            
        except Exception as e:
            logger.error(f"Error collecting academic setup data: {str(e)}")
            raise
    
    async def collect_courses(self, program_id: str, semester: int) -> List[Dict[str, Any]]:
        """Collect Courses data"""
        try:
            # Get courses for the program and semester
            courses_cursor = db.db.courses.find({
                "program_id": ObjectId(program_id),
                "semester": semester,
                "is_active": True
            })
            courses = await courses_cursor.to_list(length=None)
            
            course_data = []
            for course in courses:
                course_info = {
                    "id": str(course["_id"]),
                    "code": course.get("code"),
                    "name": course.get("name"),
                    "credits": course.get("credits"),
                    "course_type": course.get('course_type', 'theory'),  # theory/lab/practical
                    "hours_per_week": course.get('hours_per_week', course.get("credits")),
                    "min_session_duration": course.get('min_session_duration', 1),  # hours
                    "max_session_duration": course.get('max_session_duration', 2),  # hours
                    "prerequisites": course.get("prerequisites", []),
                    "semester": semester,
                    "program_id": program_id
                }
                course_data.append(course_info)
            
            logger.info(f"Collected {len(course_data)} courses for program {program_id}, semester {semester}")
            return course_data
            
        except Exception as e:
            logger.error(f"Error collecting courses data: {str(e)}")
            raise
    
    async def collect_faculty(self) -> List[Dict[str, Any]]:
        """Collect Faculty data"""
        try:
            faculty_cursor = db.db.faculty.find({})
            faculty_members = await faculty_cursor.to_list(length=None)
            
            faculty_data = []
            for faculty in faculty_members:
                # Parse available days (assuming stored as comma-separated string or list)
                available_days = faculty.get('available_days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
                if isinstance(available_days, str):
                    available_days = [day.strip().lower() for day in available_days.split(',')]
                
                faculty_info = {
                    "id": str(faculty["_id"]),
                    "name": faculty.get("name"),
                    "email": faculty.get('email', ''),
                    "department": faculty.get('department', ''),
                    "subjects_taught": faculty.get('subjects_taught', []),
                    "max_hours_per_week": faculty.get('max_hours_per_week', 20),
                    "available_days": available_days,
                    "preferred_time_slots": faculty.get('preferred_time_slots', []),
                    "unavailable_time_slots": faculty.get('unavailable_time_slots', []),
                    "specialization": faculty.get('specialization', ''),
                    "experience_years": faculty.get('experience_years', 0)
                }
                faculty_data.append(faculty_info)
            
            logger.info(f"Collected {len(faculty_data)} faculty members")
            return faculty_data
            
        except Exception as e:
            logger.error(f"Error collecting faculty data: {str(e)}")
            raise
    
    async def collect_student_groups(self, program_id: str, semester: int) -> List[Dict[str, Any]]:
        """Collect Student Groups data"""
        try:
            groups_cursor = db.db.student_groups.find({
                "program_id": ObjectId(program_id)
            })
            student_groups = await groups_cursor.to_list(length=None)
            
            # Get all courses for this program and semester to assign to groups
            courses_cursor = db.db.courses.find({
                "program_id": ObjectId(program_id),
                "semester": semester,
                "is_active": True
            })
            courses = await courses_cursor.to_list(length=None)
            course_ids = [str(course["_id"]) for course in courses]
            
            group_data = []
            for group in student_groups:
                group_info = {
                    "id": str(group["_id"]),
                    "name": group.get("name"),
                    "program_id": program_id,
                    "semester": semester,
                    "year": group.get('year', 1),
                    "section": group.get('section', 'A'),
                    "type": group.get('type', 'regular'),  # regular/honors/special
                    "student_strength": group.get('student_strength', 30),
                    "course_ids": course_ids,  # Assign all courses to the group
                    "preferred_time_slots": group.get('preferred_time_slots', []),
                    "unavailable_time_slots": group.get('unavailable_time_slots', [])
                }
                group_data.append(group_info)
            
            logger.info(f"Collected {len(group_data)} student groups for program {program_id}, semester {semester}")
            return group_data
            
        except Exception as e:
            logger.error(f"Error collecting student groups data: {str(e)}")
            raise
    
    async def collect_rooms(self) -> List[Dict[str, Any]]:
        """Collect Rooms data"""
        try:
            rooms_cursor = db.db.rooms.find({"is_active": True})
            rooms = await rooms_cursor.to_list(length=None)
            
            room_data = []
            for room in rooms:
                room_info = {
                    "id": str(room["_id"]),
                    "name": room.get("name"),
                    "room_number": room.get('room_number', room.get("name")),
                    "type": room.get('type', 'classroom'),  # classroom/lab/auditorium/seminar
                    "capacity": room.get("capacity"),
                    "facilities": room.get('facilities', []),
                    "location": room.get('location', ''),
                    "floor": room.get('floor', 1),
                    "building": room.get('building', ''),
                    "equipment": room.get('equipment', []),
                    "availability": room.get('availability', {}),  # day-wise availability
                    "maintenance_slots": room.get('maintenance_slots', [])  # unavailable time slots
                }
                room_data.append(room_info)
            
            logger.info(f"Collected {len(room_data)} rooms")
            return room_data
            
        except Exception as e:
            logger.error(f"Error collecting rooms data: {str(e)}")
            raise
    
    def collect_time_and_rules(self) -> Dict[str, Any]:
        """Collect Time and Rules configuration"""
        try:
            # Default time and rules configuration (can be customized from database)
            time_rules = {
                "college_start_time": "09:00",
                "college_end_time": "17:00",
                "lunch_start_time": "12:30",
                "lunch_end_time": "13:30",
                "lunch_break": {
                    "start_time": "12:30",
                    "end_time": "13:30"
                },
                "class_duration": 60,  # minutes
                "break_duration": 10,  # minutes between classes
                "max_continuous_hours": 3,  # maximum continuous hours for a subject
                "max_classes_per_day": 8,
                "max_lab_classes_per_day": 2,
                "max_class_repeats_per_day": 2,  # same subject max repeats
                "time_slots": self._generate_time_slots(),
                "constraints": {
                    "no_back_to_back_labs": True,
                    "faculty_travel_time": 15,  # minutes between classes in different buildings
                    "student_break_required": True,
                    "weekend_classes": False,
                    "evening_classes": False,
                    "balance_daily_load": True
                }
            }
            
            logger.info("Collected time and rules configuration")
            return time_rules
            
        except Exception as e:
            logger.error(f"Error collecting time and rules data: {str(e)}")
            raise
    
    def _generate_time_slots(self) -> List[Dict[str, str]]:
        """Generate time slots based on college timings"""
        time_slots = []
        
        # Morning slots
        morning_slots = [
            {"id": "slot_1", "start_time": "11:00", "end_time": "12:00", "period": 1},
            {"id": "slot_2", "start_time": "12:00", "end_time": "13:00", "period": 2}
        ]
        
        # Afternoon slots (after lunch)
        afternoon_slots = [
            {"id": "slot_3", "start_time": "14:00", "end_time": "15:00", "period": 3},
            {"id": "slot_4", "start_time": "15:00", "end_time": "16:00", "period": 4},
            {"id": "slot_5", "start_time": "16:00", "end_time": "16:30", "period": 5}
        ]
        
        time_slots.extend(morning_slots)
        time_slots.extend(afternoon_slots)
        
        return time_slots
    
    async def validate_collected_data(self, data: Dict[str, Any]) -> bool:
        """Validate the collected data for completeness"""
        try:
            required_sections = ["academic_setup", "courses", "faculty", "student_groups", "rooms", "time_rules"]
            
            for section in required_sections:
                if section not in data:
                    logger.error(f"Missing required section: {section}")
                    return False
            
            # Validate minimum data requirements
            if not data["courses"]:
                logger.error("No courses found for the specified program and semester")
                return False
            
            if not data["faculty"]:
                logger.error("No faculty members found")
                return False
            
            if not data["student_groups"]:
                logger.error("No student groups found for the specified program and semester")
                return False
            
            if not data["rooms"]:
                logger.error("No rooms found")
                return False
            
            logger.info("Data validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating collected data: {str(e)}")
            return False
    
    async def get_data_summary(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Get summary statistics of collected data"""
        return {
            "total_courses": len(data.get("courses", [])),
            "total_faculty": len(data.get("faculty", [])),
            "total_student_groups": len(data.get("student_groups", [])),
            "total_rooms": len(data.get("rooms", [])),
            "total_time_slots": len(data.get("time_rules", {}).get("time_slots", [])),
            "working_days": data.get("academic_setup", {}).get("total_working_days", 0)
        }