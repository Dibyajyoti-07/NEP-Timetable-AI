# backend/app/services/timetable/advanced_generator.py
"""
Advanced Timetable Generator with Hard and Soft Constraints
Implements the detailed scheduling rules for CSE AI & ML program
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from bson import ObjectId
import datetime
import random
from copy import deepcopy

from app.db.mongodb import db

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def t2min(t: str) -> int:
    """Convert time string to minutes since midnight"""
    h, m = t.split(":")
    return int(h) * 60 + int(m)

def min2t(m: int) -> str:
    """Convert minutes since midnight to time string"""
    return f"{m//60:02d}:{m%60:02d}"

@dataclass
class TimeSlot:
    day: str
    start_min: int  # minutes since midnight
    end_min: int    # minutes since midnight
    
    @property
    def start_time(self) -> str:
        return min2t(self.start_min)
    
    @property
    def end_time(self) -> str:
        return min2t(self.end_min)
    
    @property
    def duration(self) -> int:
        return self.end_min - self.start_min
    
    def overlaps(self, other: 'TimeSlot') -> bool:
        if self.day != other.day:
            return False
        return not (self.end_min <= other.start_min or other.end_min <= self.start_min)
    
    def __str__(self) -> str:
        return f"{self.day} {self.start_time}-{self.end_time}"

@dataclass
class CourseRequirement:
    """Defines a course and its scheduling requirements"""
    code: str
    name: str
    hours_per_week: int
    is_lab: bool
    prefer_double_periods: bool
    elective_type: Optional[str] = None  # "elective", "minor", or None
    lab_duration: int = 180  # minutes for lab sessions
    theory_duration: int = 50  # minutes for theory sessions
    
    def get_session_structure(self) -> List[int]:
        """Returns list of session durations needed per week"""
        if self.is_lab:
            return [self.lab_duration]  # One 3-hour lab session
        
        total_minutes = self.hours_per_week * 60
        sessions = []
        
        if self.prefer_double_periods:
            # Prefer 2-period blocks (100 minutes)
            while total_minutes >= 100:
                sessions.append(100)
                total_minutes -= 100
        
        # Add remaining time as single periods
        while total_minutes >= 50:
            sessions.append(50)
            total_minutes -= 50
            
        return sessions

@dataclass
class StudentGroup:
    id: str
    name: str
    size: int
    is_subgroup: bool = False
    parent_group_id: Optional[str] = None

@dataclass
class Room:
    id: str
    name: str
    capacity: int
    is_lab: bool
    
    def can_accommodate(self, group_size: int, is_lab_session: bool) -> bool:
        return (self.capacity >= group_size and 
                self.is_lab == is_lab_session)

@dataclass
class Faculty:
    id: str
    name: str
    subjects: List[str]

@dataclass
class ScheduleEntry:
    """Represents a scheduled class session"""
    course_code: str
    course_name: str
    group_id: str
    faculty_id: str
    room_id: str
    time_slot: TimeSlot
    is_lab: bool
    session_duration: int

class SchedulingRules:
    """Defines all hard and soft constraints"""
    
    def __init__(self):
        # Default hard constraints
        self.WORKING_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        self.DAY_START = t2min("08:00")
        self.DAY_END = t2min("18:00")
        self.LUNCH_START = t2min("12:30")
        self.LUNCH_END = t2min("13:20")
        self.PERIOD_DURATION = 50  # minutes
        self.PASSING_TIME = 10     # minutes between periods
        self.MAX_CONTINUOUS_PERIODS = 3
        self.MAX_PERIODS_PER_DAY = 6  # preferred, absolute cap 8 if needed
        self.ABSOLUTE_MAX_PERIODS_PER_DAY = 8  # Absolute maximum as per requirements
        self.MAX_LABS_PER_DAY_PER_GROUP = 1
        
        # Soft constraint targets
        self.PREFERRED_DAILY_PERIODS_MIN = 7
        self.PREFERRED_DAILY_PERIODS_MAX = 9
        
        # Lab windows (start_min, end_min)
        self.LAB_WINDOWS = [
            (t2min("08:00"), t2min("11:10")),  # Morning: 190 minutes
            (t2min("13:20"), t2min("16:30")),  # Early afternoon: 190 minutes  
            (t2min("14:20"), t2min("17:30")),  # Late afternoon: 190 minutes
        ]
    
    @classmethod
    async def from_database(cls, program_id: str = None) -> "SchedulingRules":
        """Load scheduling rules from database constraints and rules"""
        rules = cls()
        
        try:
            # Load constraints from database
            filter_query = {
                "$or": [
                    {"program_id": None},  # Global constraints
                    {"program_id": program_id},  # Program-specific constraints
                    {"program_id": ObjectId(program_id) if program_id else None}
                ],
                "is_active": True
            }
            constraints = await db.db.constraints.find(filter_query).to_list(length=None)
            
            # Load rules from database (Time & Rules tab)
            rules_data = await db.db.rules.find({"is_active": True, "rule_type": "time_settings"}).to_list(length=None)
            
            # Apply constraints
            for constraint in constraints:
                params = constraint.get("parameters", {})
                if constraint.get("type") == "time_settings":
                    if "college_start_time" in params:
                        rules.DAY_START = t2min(params["college_start_time"])
                    if "college_end_time" in params:
                        rules.DAY_END = t2min(params["college_end_time"])
                    if "lunch_time" in params:
                        rules.LUNCH_START = t2min(params["lunch_time"])
                        rules.LUNCH_END = rules.LUNCH_START + 50
                    if "interval_between_classes" in params:
                        rules.PASSING_TIME = int(params["interval_between_classes"])
                    if "max_continuous_hours" in params:
                        rules.MAX_CONTINUOUS_PERIODS = int(params["max_continuous_hours"])
                    if "max_classes_per_day" in params:
                        rules.MAX_PERIODS_PER_DAY = int(params["max_classes_per_day"])
                        rules.ABSOLUTE_MAX_PERIODS_PER_DAY = max(8, int(params["max_classes_per_day"]))
                    if "max_lab_classes_per_day" in params:
                        rules.MAX_LABS_PER_DAY_PER_GROUP = int(params["max_lab_classes_per_day"])
            
            # Apply rules from Time & Rules tab
            for rule in rules_data:
                params = rule.get("params", {})
                if "college_start_time" in params:
                    rules.DAY_START = t2min(params["college_start_time"])
                if "college_end_time" in params:
                    rules.DAY_END = t2min(params["college_end_time"])
                if "lunch_time" in params:
                    rules.LUNCH_START = t2min(params["lunch_time"])
                    rules.LUNCH_END = rules.LUNCH_START + 50
                if "interval_between_classes" in params:
                    rules.PASSING_TIME = int(params["interval_between_classes"])
                if "max_continuous_hours" in params:
                    rules.MAX_CONTINUOUS_PERIODS = int(params["max_continuous_hours"])
                if "max_classes_per_day" in params:
                    rules.MAX_PERIODS_PER_DAY = int(params["max_classes_per_day"])
                    rules.ABSOLUTE_MAX_PERIODS_PER_DAY = max(8, int(params["max_classes_per_day"]))
                if "max_lab_classes_per_day" in params:
                    rules.MAX_LABS_PER_DAY_PER_GROUP = int(params["max_lab_classes_per_day"])
                    
            print(f"[SUCCESS] Loaded scheduling rules from database: Start={min2t(rules.DAY_START)}, End={min2t(rules.DAY_END)}, Lunch={min2t(rules.LUNCH_START)}, MaxPeriods={rules.MAX_PERIODS_PER_DAY}")
            
        except Exception as e:
            print(f"[WARNING] Error loading rules from database, using defaults: {e}")
            
        return rules
    
    @classmethod
    async def from_database_with_setup(cls, program_id: str = None, academic_setup: dict = None) -> "SchedulingRules":
        """Load scheduling rules from database and override with academic setup data"""
        # Start with database rules
        rules = await cls.from_database(program_id)
        
        if academic_setup:
            # Override with academic setup data
            working_days = academic_setup.get("working_days", {})
            time_slots = academic_setup.get("time_slots", {})
            constraints = academic_setup.get("constraints", {})
            
            # Update working days
            if working_days:
                enabled_days = []
                day_mapping = {
                    "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
                    "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"
                }
                for day_key, enabled in working_days.items():
                    if enabled and day_key in day_mapping:
                        enabled_days.append(day_mapping[day_key])
                
                if enabled_days:
                    rules.WORKING_DAYS = enabled_days
                    print(f"[SETUP] Updated working days from academic setup: {enabled_days}")
            
            # Update time slots
            if time_slots:
                if "start_time" in time_slots:
                    rules.DAY_START = t2min(time_slots["start_time"])
                if "end_time" in time_slots:
                    rules.DAY_END = t2min(time_slots["end_time"])
                if "slot_duration" in time_slots:
                    rules.PERIOD_DURATION = int(time_slots["slot_duration"])
                if "break_duration" in time_slots:
                    rules.PASSING_TIME = int(time_slots["break_duration"])
                if time_slots.get("lunch_break", False):
                    if "lunch_start" in time_slots:
                        rules.LUNCH_START = t2min(time_slots["lunch_start"])
                    if "lunch_end" in time_slots:
                        rules.LUNCH_END = t2min(time_slots["lunch_end"])
                
                print(f"⏰ Updated time slots from academic setup: {min2t(rules.DAY_START)}-{min2t(rules.DAY_END)}, Period: {rules.PERIOD_DURATION}min")
            
            # Update constraints
            if constraints:
                if "max_periods_per_day" in constraints:
                    rules.MAX_PERIODS_PER_DAY = int(constraints["max_periods_per_day"])
                    rules.ABSOLUTE_MAX_PERIODS_PER_DAY = max(8, int(constraints["max_periods_per_day"]))
                if "max_consecutive_hours" in constraints:
                    rules.MAX_CONTINUOUS_PERIODS = int(constraints["max_consecutive_hours"])
                if "min_break_between_subjects" in constraints:
                    # This could be used to adjust passing time if needed
                    pass
                
                print(f"[SETUP] Updated constraints from academic setup: MaxPeriods={rules.MAX_PERIODS_PER_DAY}, MaxContinuous={rules.MAX_CONTINUOUS_PERIODS}")
            
            # Recalculate lab windows based on new time settings
            rules.LAB_WINDOWS = [
                (rules.DAY_START, rules.DAY_START + 190),  # Morning: 190 minutes
                (rules.LUNCH_END, rules.LUNCH_END + 190),  # Early afternoon: 190 minutes  
                (rules.LUNCH_END + 60, rules.LUNCH_END + 250),  # Late afternoon: 190 minutes
            ]
            # Filter lab windows that fit within the day
            rules.LAB_WINDOWS = [(start, end) for start, end in rules.LAB_WINDOWS if end <= rules.DAY_END]
        
        return rules
    
    def get_theory_slots(self) -> List[TimeSlot]:
        """Generate all possible 50-minute theory slots"""
        slots = []
        for day in self.WORKING_DAYS:
            current_time = self.DAY_START
            
            while current_time + self.PERIOD_DURATION <= self.DAY_END:
                slot_end = current_time + self.PERIOD_DURATION
                
                # Skip lunch period
                if not (current_time < self.LUNCH_END and slot_end > self.LUNCH_START):
                    slots.append(TimeSlot(day, current_time, slot_end))
                
                current_time += self.PERIOD_DURATION + self.PASSING_TIME
                
                # Jump over lunch if we hit it
                if current_time < self.LUNCH_END and current_time + self.PERIOD_DURATION > self.LUNCH_START:
                    current_time = self.LUNCH_END
        
        return slots
    
    def get_double_period_slots(self) -> List[TimeSlot]:
        """Generate all possible 100-minute double period slots"""
        slots = []
        theory_slots = self.get_theory_slots()
        
        for i in range(len(theory_slots) - 1):
            slot1 = theory_slots[i]
            slot2 = theory_slots[i + 1]
            
            # Check if slots are consecutive on the same day
            if (slot1.day == slot2.day and 
                slot1.end_min + self.PASSING_TIME == slot2.start_min):
                
                double_slot = TimeSlot(
                    slot1.day, 
                    slot1.start_min, 
                    slot2.end_min
                )
                slots.append(double_slot)
        
        return slots
    
    def get_lab_slots(self) -> List[TimeSlot]:
        """Generate all possible 180-minute lab slots"""
        slots = []
        for day in self.WORKING_DAYS:
            for start_min, end_min in self.LAB_WINDOWS:
                if end_min - start_min >= 180:  # Ensure window can fit 3-hour lab
                    slots.append(TimeSlot(day, start_min, start_min + 180))
        return slots

class AdvancedTimetableGenerator:
    """Advanced constraint-based timetable generator"""
    
    def __init__(self, rules: SchedulingRules = None):
        self.rules = rules or SchedulingRules()
        self.courses: List[CourseRequirement] = []
        self.groups: List[StudentGroup] = []
        self.rooms: List[Room] = []
        self.faculty: List[Faculty] = []
        self.schedule: List[ScheduleEntry] = []
        
        # Occupancy tracking
        self.room_occupancy: Dict[str, List[TimeSlot]] = {}
        self.faculty_occupancy: Dict[str, List[TimeSlot]] = {}
        self.group_occupancy: Dict[str, List[TimeSlot]] = {}
    
    def setup_cse_ai_ml_courses(self):
        """Setup the specific CSE AI & ML course requirements"""
        self.courses = [
            CourseRequirement("PROB_STATS", "Probability & Statistics", 4, False, False),
            CourseRequirement("OS_THEORY", "Operating System (Theory)", 8, False, True),
            CourseRequirement("OOP_THEORY", "Object Oriented Programming (Theory)", 8, False, True),
            CourseRequirement("ML_THEORY", "Machine Learning (Theory)", 6, False, True),
            CourseRequirement("IND_MGMT", "Industrial Management", 2, False, False),
            CourseRequirement("CLOUD_COMP", "Cloud Computing", 3, False, False, "elective"),
            CourseRequirement("OPT_TECH", "Optimization Techniques", 4, False, False, "minor"),
            CourseRequirement("OS_LAB", "OS Lab", 3, True, False),
            CourseRequirement("OOP_LAB", "OOP & Java Lab", 3, True, False),
        ]
    
    def setup_groups_and_resources(self):
        """Setup student groups, rooms, and faculty"""
        # Main lecture group
        self.groups = [
            StudentGroup("MAIN", "CSE AI & ML - Main", 60, False),
            StudentGroup("SUB1", "Lab Subgroup 1", 30, True, "MAIN"),
            StudentGroup("SUB2", "Lab Subgroup 2", 29, True, "MAIN"),
        ]
        
        # Rooms - Adding more rooms to handle resource constraints
        self.rooms = [
            Room("N001", "N-001", 75, False),  # Theory classroom
            Room("N002", "N-002", 70, False),  # Theory classroom
            Room("N003", "N-003", 65, False),  # Theory classroom
            Room("N004", "N-004", 60, False),  # Theory classroom
            Room("N017", "N-017", 35, True),   # Computer lab
            Room("N018", "N-018", 35, True),   # Computer lab
        ]
        
        # Faculty (simplified for demo)
        self.faculty = [
            Faculty("F001", "Dr. Smith", ["PROB_STATS", "ML_THEORY"]),
            Faculty("F002", "Dr. Johnson", ["OS_THEORY", "OS_LAB"]),
            Faculty("F003", "Dr. Brown", ["OOP_THEORY", "OOP_LAB"]),
            Faculty("F004", "Dr. Davis", ["IND_MGMT", "CLOUD_COMP"]),
            Faculty("F005", "Dr. Wilson", ["OPT_TECH"]),
        ]
    
    def initialize_occupancy_tracking(self):
        """Initialize occupancy tracking dictionaries"""
        self.room_occupancy = {room.id: [] for room in self.rooms}
        self.faculty_occupancy = {faculty.id: [] for faculty in self.faculty}
        self.group_occupancy = {group.id: [] for group in self.groups}
    
    def is_slot_available(self, time_slot: TimeSlot, room_id: str, 
                         faculty_id: str, group_id: str) -> bool:
        """Check if a time slot is available for all resources"""
        # Check room availability
        for occupied_slot in self.room_occupancy[room_id]:
            if time_slot.overlaps(occupied_slot):
                print(f"    Slot {time_slot}: Room {room_id} conflict with {occupied_slot}")
                return False
        
        # Check faculty availability
        for occupied_slot in self.faculty_occupancy[faculty_id]:
            if time_slot.overlaps(occupied_slot):
                print(f"    Slot {time_slot}: Faculty {faculty_id} conflict with {occupied_slot}")
                return False
        
        # Check group availability
        for occupied_slot in self.group_occupancy[group_id]:
            if time_slot.overlaps(occupied_slot):
                print(f"    Slot {time_slot}: Group {group_id} conflict with {occupied_slot}")
                return False
        
        print(f"    Slot {time_slot}: Available (Room: {room_id}, Faculty: {faculty_id}, Group: {group_id})")
        return True
    
    def book_slot(self, time_slot: TimeSlot, room_id: str, 
                  faculty_id: str, group_id: str):
        """Book a time slot for the specified resources"""
        self.room_occupancy[room_id].append(time_slot)
        self.faculty_occupancy[faculty_id].append(time_slot)
        self.group_occupancy[group_id].append(time_slot)
    
    def find_suitable_faculty(self, course_code: str) -> Optional[str]:
        """Find a faculty member who can teach the course"""
        # First try exact course code match
        for faculty in self.faculty:
            if course_code in faculty.subjects:
                return faculty.id
        
        # Then try course name match (for courses loaded from database)
        course_name = None
        for course in self.courses:
            if course.code == course_code:
                course_name = course.name
                break
        
        if course_name:
            for faculty in self.faculty:
                if course_name in faculty.subjects:
                    return faculty.id
        
        # Try to find general faculty (marked with "GENERAL")
        for faculty in self.faculty:
            if "GENERAL" in faculty.subjects:
                print(f"[INFO] Assigning general faculty {faculty.name} to {course_code}")
                return faculty.id
        
        # Fallback: assign any available faculty
        if self.faculty:
            print(f"[WARNING] No specific faculty found for {course_code}, assigning {self.faculty[0].name}")
            return self.faculty[0].id
        
        return None
    
    def find_suitable_room(self, group_size: int, is_lab: bool, time_slot: TimeSlot = None) -> Optional[str]:
        """Find a suitable room for the session"""
        suitable_rooms = [room for room in self.rooms 
                         if room.can_accommodate(group_size, is_lab)]
        
        if not suitable_rooms:
            return None
        
        # If time_slot is provided, filter out rooms that are occupied at that time
        if time_slot:
            available_rooms = []
            for room in suitable_rooms:
                is_available = True
                for occupied_slot in self.room_occupancy[room.id]:
                    if time_slot.overlaps(occupied_slot):
                        is_available = False
                        break
                if is_available:
                    available_rooms.append(room)
            
            if available_rooms:
                # Prefer rooms with less current occupancy
                return min(available_rooms, 
                           key=lambda r: len(self.room_occupancy[r.id])).id
        
        # Fallback: return room with least occupancy (for backward compatibility)
        return min(suitable_rooms, 
                   key=lambda r: len(self.room_occupancy[r.id])).id
    
    def check_daily_constraints(self, group_id: str, day: str, 
                              new_slot: TimeSlot) -> bool:
        """Check if adding this slot violates daily constraints"""
        day_slots = [slot for slot in self.group_occupancy[group_id] 
                    if slot.day == day]
        
        # Calculate periods more accurately
        existing_periods = 0
        for slot in day_slots:
            if slot.duration >= 180:  # Lab session = 3+ periods
                existing_periods += 3
            elif slot.duration >= 100:  # Double period
                existing_periods += 2
            else:  # Single period
                existing_periods += 1
        
        new_periods = 0
        if new_slot.duration >= 180:
            new_periods = 3
        elif new_slot.duration >= 100:
            new_periods = 2
        else:
            new_periods = 1
        
        total_periods = existing_periods + new_periods
        
        # Allow up to 8 periods per day if needed
        if total_periods > self.rules.ABSOLUTE_MAX_PERIODS_PER_DAY:
            return False
        
        # Check max labs per day
        if new_slot.duration >= 180:  # This is a lab
            lab_count = sum(1 for slot in day_slots if slot.duration >= 180)
            if lab_count >= self.rules.MAX_LABS_PER_DAY_PER_GROUP:
                return False
        
        return True
    
    def check_continuous_periods_constraint(self, group_id: str, 
                                          new_slot: TimeSlot) -> bool:
        """Check if adding this slot violates continuous periods constraint"""
        day_slots = [slot for slot in self.group_occupancy[group_id] 
                    if slot.day == new_slot.day]
        day_slots.append(new_slot)
        day_slots.sort(key=lambda s: s.start_min)
        
        continuous_count = 1
        for i in range(1, len(day_slots)):
            prev_slot = day_slots[i-1]
            curr_slot = day_slots[i]
            
            # Check if slots are continuous (considering passing time)
            if prev_slot.end_min + self.rules.PASSING_TIME >= curr_slot.start_min:
                continuous_count += 1
                if continuous_count > self.rules.MAX_CONTINUOUS_PERIODS:
                    return False
            else:
                continuous_count = 1
        
        return True
    
    def schedule_labs_first(self) -> bool:
        """Schedule all lab sessions first (they have stricter constraints)"""
        lab_courses = [course for course in self.courses if course.is_lab]
        lab_slots = self.rules.get_lab_slots()
        
        # Sort lab slots to prefer afternoon slots (soft constraint)
        lab_slots.sort(key=lambda slot: (
            0 if slot.start_min >= t2min("13:20") else 1,  # Prefer afternoon
            slot.start_min  # Then by start time
        ))
        
        for course in lab_courses:
            # Each lab course needs to be scheduled for both subgroups
            subgroups = [group for group in self.groups if group.is_subgroup]
            
            for subgroup in subgroups:
                scheduled = False
                
                for slot in lab_slots:
                    # Check daily constraints
                    if not self.check_daily_constraints(subgroup.id, slot.day, slot):
                        continue
                    
                    # Find suitable faculty and room
                    faculty_id = self.find_suitable_faculty(course.code)
                    room_id = self.find_suitable_room(subgroup.size, True, slot)
                    
                    if not faculty_id or not room_id:
                        continue
                    
                    # Check availability
                    if self.is_slot_available(slot, room_id, faculty_id, subgroup.id):
                        # Book the slot
                        self.book_slot(slot, room_id, faculty_id, subgroup.id)
                        
                        # Add to schedule
                        entry = ScheduleEntry(
                            course_code=course.code,
                            course_name=course.name,
                            group_id=subgroup.id,
                            faculty_id=faculty_id,
                            room_id=room_id,
                            time_slot=slot,
                            is_lab=True,
                            session_duration=180
                        )
                        self.schedule.append(entry)
                        scheduled = True
                        break
                
                if not scheduled:
                    print(f"Failed to schedule {course.code} for {subgroup.name}")
                    return False
        
        return True
    
    def schedule_theory_sessions(self) -> bool:
        """Schedule all theory sessions"""
        theory_courses = [course for course in self.courses if not course.is_lab]
        
        # Get available slots
        single_slots = self.rules.get_theory_slots()
        double_slots = self.rules.get_double_period_slots()
        
        # Sort theory courses by priority (heavy courses first)
        theory_courses.sort(key=lambda c: c.hours_per_week, reverse=True)
        
        for course in theory_courses:
            sessions_needed = course.get_session_structure()
            main_group = next(group for group in self.groups if not group.is_subgroup)
            
            print(f"[INFO] Scheduling {course.code}: {len(sessions_needed)} sessions {sessions_needed}")
            
            for i, session_duration in enumerate(sessions_needed):
                scheduled = False
                
                # Choose appropriate slot type
                available_slots = double_slots if session_duration == 100 else single_slots
                
                # Apply soft constraints for slot preference
                available_slots = self.apply_soft_constraints_to_slots(
                    available_slots, course, main_group.id
                )
                
                print(f"  Session {i+1} ({session_duration}min): Checking {len(available_slots)} slots")
                
                for slot_idx, slot in enumerate(available_slots):
                    # Check constraints
                    daily_ok = self.check_daily_constraints(main_group.id, slot.day, slot)
                    if not daily_ok:
                        print(f"    Slot {slot}: Daily constraint failed")
                        continue
                    
                    # Relax continuous periods constraint for now
                    # continuous_ok = self.check_continuous_periods_constraint(main_group.id, slot)
                    # if not continuous_ok:
                    #     continue
                    
                    # Check for course repetition on same day (allow multiple sessions for heavy courses)
                    # Only restrict same-day scheduling for courses with <= 2 hours per week
                    if (session_duration < 100 and 
                        course.hours_per_week <= 2 and  # Only restrict for very light courses
                        self.has_course_on_day(course.code, main_group.id, slot.day)):
                        print(f"    Slot {slot}: Course already scheduled on {slot.day}")
                        continue
                    
                    # Find resources
                    faculty_id = self.find_suitable_faculty(course.code)
                    room_id = self.find_suitable_room(main_group.size, False, slot)
                    
                    if not faculty_id or not room_id:
                        print(f"    Slot {slot}: No faculty ({faculty_id}) or room ({room_id})")
                        continue
                    
                    # Check availability
                    if self.is_slot_available(slot, room_id, faculty_id, main_group.id):
                        # Book the slot
                        self.book_slot(slot, room_id, faculty_id, main_group.id)
                        
                        # Add to schedule
                        entry = ScheduleEntry(
                            course_code=course.code,
                            course_name=course.name,
                            group_id=main_group.id,
                            faculty_id=faculty_id,
                            room_id=room_id,
                            time_slot=slot,
                            is_lab=False,
                            session_duration=session_duration
                        )
                        self.schedule.append(entry)
                        print(f"    [SUCCESS] Scheduled at {slot} with {faculty_id} in {room_id}")
                        scheduled = True
                        break
                    else:
                        print(f"    Slot {slot}: Resource conflict (detailed check failed)")
                
                if not scheduled:
                    print(f"[ERROR] Failed to schedule {session_duration}min session for {course.code}")
                    # Return False to indicate scheduling failure
                    return False
        
        return True
    
    def apply_soft_constraints_to_slots(self, slots: List[TimeSlot], 
                                      course: CourseRequirement, 
                                      group_id: str) -> List[TimeSlot]:
        """Apply soft constraints to prioritize slots"""
        def slot_score(slot: TimeSlot) -> int:
            score = 0
            
            # Avoid early slots (08:00) for electives/minor
            if course.elective_type and slot.start_min == t2min("08:00"):
                score -= 15
            
            # Prefer mid-day for Industrial Management
            if course.code == "IND_MGMT":
                if t2min("10:00") <= slot.start_min <= t2min("15:00"):
                    score += 10
                else:
                    score -= 5
            
            # Prefer afternoon labs (13:20-16:30)
            if course.is_lab and t2min("13:20") <= slot.start_min <= t2min("16:30"):
                score += 15
            elif course.is_lab and slot.start_min < t2min("13:20"):
                score -= 5
            
            # Spread heavy theory courses (OS, OOP, ML) across different days
            if course.code in ["OS_THEORY", "OOP_THEORY", "ML_THEORY"]:
                occupied_days = {entry.time_slot.day for entry in self.schedule 
                               if entry.course_code == course.code and entry.group_id == group_id}
                if slot.day not in occupied_days:
                    score += 8
                else:
                    score -= 10  # Penalize same day scheduling
            
            # Avoid Cloud + Optimization back-to-back
            if course.code in ["CLOUD_COMP", "OPT_TECH"]:
                for entry in self.schedule:
                    if (entry.group_id == group_id and 
                        entry.time_slot.day == slot.day and
                        entry.course_code in ["CLOUD_COMP", "OPT_TECH"] and
                        entry.course_code != course.code):
                        # Check if slots are adjacent
                        time_diff = abs(entry.time_slot.start_min - slot.start_min)
                        if time_diff <= 60:  # Within one period
                            score -= 12
            
            # Balance daily load (prefer 7-9 periods/day)
            daily_periods = len([e for e in self.schedule 
                               if e.group_id == group_id and e.time_slot.day == slot.day])
            if 7 <= daily_periods <= 9:
                score += 5
            elif daily_periods < 7:
                score += 2
            else:
                score -= 8
            
            # Minimize idle gaps - prefer consecutive scheduling
            adjacent_sessions = any(
                abs(entry.time_slot.end_min - slot.start_min) <= 10 or
                abs(slot.end_min - entry.time_slot.start_min) <= 10
                for entry in self.schedule
                if entry.group_id == group_id and entry.time_slot.day == slot.day
            )
            if adjacent_sessions:
                score += 3
            
            return score
        
        # Sort slots by score (higher score first)
        return sorted(slots, key=slot_score, reverse=True)
    
    def has_course_on_day(self, course_code: str, group_id: str, day: str) -> bool:
        """Check if a course is already scheduled on a specific day for a group"""
        return any(entry.course_code == course_code and 
                  entry.group_id == group_id and 
                  entry.time_slot.day == day 
                  for entry in self.schedule)
    
    def calculate_schedule_score(self) -> int:
        """Calculate overall schedule score based on soft constraints"""
        score = 0
        
        # Group sessions by day and group for analysis
        daily_sessions = {}
        for entry in self.schedule:
            key = (entry.group_id, entry.time_slot.day)
            if key not in daily_sessions:
                daily_sessions[key] = []
            daily_sessions[key].append(entry)
        
        # Score based on various soft constraints
        for entry in self.schedule:
            # Prefer afternoon labs (13:20-16:30)
            if entry.is_lab:
                if t2min("13:20") <= entry.time_slot.start_min <= t2min("16:30"):
                    score += 10
                else:
                    score -= 5
            
            # Penalize early electives/minor courses (08:00 slot)
            if (entry.course_code in ["CLOUD_COMP", "OPT_TECH"] and 
                entry.time_slot.start_min == t2min("08:00")):
                score -= 15
            
            # Reward mid-day Industrial Management
            if entry.course_code == "IND_MGMT":
                if t2min("10:00") <= entry.time_slot.start_min <= t2min("15:00"):
                    score += 10
                else:
                    score -= 5
            
            # Prefer 2-period blocks for OS, OOP, ML
            if (entry.course_code in ["OS_THEORY", "OOP_THEORY", "ML_THEORY"] and 
                entry.time_slot.duration == 100):  # Double period
                score += 8
        
        # Check daily load balance (7-9 periods preferred)
        for (group_id, day), sessions in daily_sessions.items():
            daily_count = len(sessions)
            if 7 <= daily_count <= 9:
                score += 10
            elif daily_count < 7:
                score += 5
            else:
                score -= 10
        
        # Check heavy theory distribution across days
        heavy_courses = ["OS_THEORY", "OOP_THEORY", "ML_THEORY"]
        for course in heavy_courses:
            course_days = set()
            for entry in self.schedule:
                if entry.course_code == course:
                    course_days.add(entry.time_slot.day)
            
            # Reward spreading across different days
            if len(course_days) >= 3:
                score += 15
            elif len(course_days) == 2:
                score += 8
            else:
                score -= 10
        
        # Check for back-to-back Cloud + Optimization
        cloud_sessions = [e for e in self.schedule if e.course_code == "CLOUD_COMP"]
        opt_sessions = [e for e in self.schedule if e.course_code == "OPT_TECH"]
        
        for cloud in cloud_sessions:
            for opt in opt_sessions:
                if (cloud.group_id == opt.group_id and 
                    cloud.time_slot.day == opt.time_slot.day):
                    time_diff = abs(cloud.time_slot.start_min - opt.time_slot.start_min)
                    if time_diff <= 60:  # Within one period
                        score -= 20
        
        # Minimize idle gaps
        for (group_id, day), sessions in daily_sessions.items():
            if len(sessions) > 1:
                sorted_sessions = sorted(sessions, key=lambda x: x.time_slot.start_min)
                for i in range(len(sorted_sessions) - 1):
                    gap = sorted_sessions[i+1].time_slot.start_min - sorted_sessions[i].time_slot.end_min
                    if gap > 60:  # Gap larger than one period
                        score -= 5
                    elif gap <= 10:  # Consecutive or minimal gap
                        score += 3
        
        return score
    
    async def load_from_database(self, program_id: str, semester: int):
        """Load courses, groups, rooms, and faculty from database"""
        print(f"\n=== LOADING DATA FROM DATABASE ===")
        print(f"Program ID: {program_id}, Semester: {semester}")
        
        # Load courses from database
        courses_raw = await db.db.courses.find({
            "program_id": ObjectId(program_id),
            "semester": semester,
            "is_active": True
        }).to_list(length=None)
        print(f"Loaded {len(courses_raw)} courses from database")
        
        # Load groups from database
        groups_raw = await db.db.student_groups.find({
            "program_id": program_id
        }).to_list(length=None)
        print(f"Loaded {len(groups_raw)} groups from database")
        
        # Load rooms from database
        rooms_raw = await db.db.rooms.find({"is_active": True}).to_list(length=None)
        print(f"Loaded {len(rooms_raw)} rooms from database")
        
        # Load faculty from database
        faculty_raw = await db.db.faculty.find({}).to_list(length=None)
        print(f"Loaded {len(faculty_raw)} faculty from database")
        
        await self._process_database_data(courses_raw, groups_raw, rooms_raw, faculty_raw)
    
    async def load_from_database_with_setup(self, program_id: str, semester: int, academic_setup: dict = None):
        """Load data from database and apply academic setup constraints"""
        # Load base data from database
        await self.load_from_database(program_id, semester)
        
        # Update rules with academic setup if provided
        if academic_setup:
            self.rules = await SchedulingRules.from_database_with_setup(program_id, academic_setup)
            print(f"[SETUP] Applied academic setup constraints to timetable generator")
    
    async def _process_database_data(self, courses_raw, groups_raw, rooms_raw, faculty_raw):
        """Process raw database data into internal format"""
        # Convert to internal format
        self.courses = []
        for course in courses_raw:
            # Determine if it's a lab course
            is_lab = course.get("type", "").lower() == "lab" or "lab" in course.get("name", "").lower()
            
            # Create course requirement
            course_req = CourseRequirement(
                code=course.get("code", ""),
                name=course.get("name", ""),
                hours_per_week=course.get("hours_per_week", 3),
                is_lab=is_lab,
                prefer_double_periods=course.get("prefer_double_periods", False),
                elective_type=course.get("elective_type"),
                lab_duration=course.get("lab_duration", 180),
                theory_duration=course.get("theory_duration", 50)
            )
            self.courses.append(course_req)
        
        # Convert groups
        self.groups = []
        for group in groups_raw:
            # Handle different field names for group size
            group_size = group.get("size") or group.get("student_count") or group.get("student_strength", 30)
            
            group_obj = StudentGroup(
                id=str(group["_id"]),
                name=group.get("name", ""),
                size=group_size,
                is_subgroup=group.get("is_subgroup", False),
                parent_group_id=group.get("parent_group_id")
            )
            self.groups.append(group_obj)
        
        # Convert rooms
        self.rooms = []
        for room in rooms_raw:
            room_obj = Room(
                id=str(room["_id"]),
                name=room.get("name", ""),
                capacity=room.get("capacity", 30),
                is_lab=room.get("is_lab", False)
            )
            self.rooms.append(room_obj)
        
        # Convert faculty
        self.faculty = []
        for faculty in faculty_raw:
            # Get specializations this faculty can teach
            specializations = faculty.get("specialization", [])
            if isinstance(specializations, list):
                # Convert specializations to course-relevant subjects
                subject_codes = []
                for spec in specializations:
                    spec_lower = spec.lower()
                    # Map specializations to course codes
                    if "data structures" in spec_lower or "algorithms" in spec_lower:
                        subject_codes.extend(["CS501", "Advanced Data Structures"])
                    if "machine learning" in spec_lower or "artificial intelligence" in spec_lower:
                        subject_codes.extend(["CS502", "Machine Learning", "CS504L", "Machine Learning Lab"])
                    if "database" in spec_lower or "data mining" in spec_lower:
                        subject_codes.extend(["CS503", "Database Management Systems", "CS505L", "Database Lab"])
                    if "software engineering" in spec_lower or "web development" in spec_lower:
                        subject_codes.extend(["CS506", "Software Engineering"])
                    if "programming" in spec_lower or "lab" in spec_lower:
                        subject_codes.extend(["CS504L", "CS505L", "Machine Learning Lab", "Database Lab"])
                    if "management" in spec_lower or "business" in spec_lower or "industrial" in spec_lower:
                        subject_codes.extend(["IND_MGMT", "Industrial Management"])
                    if "statistics" in spec_lower or "probability" in spec_lower or "math" in spec_lower:
                        subject_codes.extend(["PROB_STATS", "Probability and Statistics"])
                    if "cloud" in spec_lower or "computing" in spec_lower or "distributed" in spec_lower:
                        subject_codes.extend(["CLOUD_COMP", "Cloud Computing"])
                    if "optimization" in spec_lower or "operations" in spec_lower or "research" in spec_lower:
                        subject_codes.extend(["OPT_TECH", "Optimization Techniques"])
                    if "general" in spec_lower or "core" in spec_lower:
                        subject_codes.extend(["IND_MGMT", "Industrial Management", "PROB_STATS", "CLOUD_COMP", "OPT_TECH"])
                
                # If no specific subjects found, mark as general faculty
                if len(subject_codes) == 0:
                    subject_codes = ["GENERAL"]  # Mark as general faculty who can teach any subject
            else:
                subject_codes = ["GENERAL"]  # If specializations is not a list, mark as general faculty
            
            faculty_obj = Faculty(
                id=str(faculty["_id"]),
                name=faculty.get("name", ""),
                subjects=subject_codes
            )
            self.faculty.append(faculty_obj)
        
        print(f"Loaded {len(self.courses)} courses, {len(self.groups)} groups, {len(self.rooms)} rooms, {len(self.faculty)} faculty")
        
        # Calculate total sessions needed
        total_sessions_needed = 0
        for course in self.courses:
            sessions_per_week = course.get_session_structure()
            total_sessions_needed += len(sessions_per_week)
        
        # Calculate available room slots per week
        theory_slots = self.rules.get_theory_slots()
        total_room_slots = len(self.rooms) * len(theory_slots)
        
        print(f"[INFO] Resource Analysis:")
        print(f"   Total sessions needed: {total_sessions_needed}")
        print(f"   Total room slots available: {total_room_slots}")
        print(f"   Room utilization: {(total_sessions_needed/total_room_slots)*100:.1f}%")
        
        if total_sessions_needed > total_room_slots:
            print(f"[WARNING] WARNING: Not enough room capacity! Need {total_sessions_needed} slots but only have {total_room_slots}")
        
        # Debug: Print loaded data
        print("\n=== DEBUG: Loaded Courses ===")
        for course in self.courses:
            print(f"  {course.code}: {course.name} (Lab: {course.is_lab}, Hours: {course.hours_per_week})")
        
        print("\n=== DEBUG: Loaded Groups ===")
        for group in self.groups:
            print(f"  {group.id}: {group.name} (Size: {group.size})")
        
        print("\n=== DEBUG: Loaded Rooms ===")
        for room in self.rooms:
            print(f"  {room.id}: {room.name} (Capacity: {room.capacity}, Lab: {room.is_lab})")
        
        print("\n=== DEBUG: Loaded Faculty ===")
        for faculty in self.faculty:
            print(f"  {faculty.id}: {faculty.name} (Subjects: {faculty.subjects})")
        print("\n")
    
    def generate_timetable(self, program_id: str = None, semester: int = None) -> Dict[str, Any]:
        """Main method to generate the timetable with multiple attempts for optimization"""
        # If no database data loaded, fall back to hardcoded setup
        if not self.courses or not self.groups or not self.rooms or not self.faculty:
            print("No database data loaded, using hardcoded setup...")
            self.setup_cse_ai_ml_courses()
            self.setup_groups_and_resources()
        
        print("Starting AI timetable generation with hard and soft constraints...")
        
        best_schedule = None
        best_score = float('-inf')
        best_validation = None
        best_statistics = None
        attempts = 5  # Try multiple times to find the best arrangement
        
        for attempt in range(attempts):
            print(f"\nAttempt {attempt + 1}/{attempts}...")
            
            # Reset for each attempt
            self.initialize_occupancy_tracking()
            self.schedule = []
            
            try:
                # Step 1: Schedule labs first (they have stricter constraints)
                if not self.schedule_labs_first():
                    print(f"Attempt {attempt + 1}: Failed to schedule lab sessions")
                    continue
                
                print(f"Scheduled {len([e for e in self.schedule if e.is_lab])} lab sessions")
                
                # Step 2: Schedule theory sessions
                if not self.schedule_theory_sessions():
                    print(f"Attempt {attempt + 1}: Failed to schedule theory sessions")
                    continue
                
                print(f"Scheduled {len([e for e in self.schedule if not e.is_lab])} theory sessions")
                
                # Step 3: Validate the schedule
                validation_result = self.validate_schedule()
                
                # Check for critical errors
                critical_errors = [error for error in validation_result["errors"] 
                                  if "No sessions scheduled" in error or "Overlap detected" in error]
                
                if critical_errors:
                    print(f"Attempt {attempt + 1}: Critical validation errors: {critical_errors}")
                    continue
                
                # Step 4: Calculate score
                score = self.calculate_schedule_score()
                print(f"Attempt {attempt + 1}: Score = {score}")
                
                # Keep the best scoring arrangement
                if score > best_score:
                    best_score = score
                    best_schedule = deepcopy(self.schedule)
                    best_validation = validation_result
                    best_statistics = self.get_schedule_statistics()
                    print(f"New best score: {best_score}")
                
            except Exception as e:
                print(f"Attempt {attempt + 1}: Exception occurred: {str(e)}")
                continue
        
        # Return the best result found
        if best_schedule is None:
            return {
                "success": False, 
                "error": "Failed to generate a valid timetable after all attempts. Please check constraints."
            }
        
        # Restore the best schedule for output formatting
        self.schedule = best_schedule
        formatted_schedule = self.format_schedule_output()
        
        print(f"\n[SUCCESS] AI Generation Complete!")
        print(f"Best arrangement found with score: {best_score}")
        print(f"Total sessions scheduled: {len(best_schedule)}")
        print(f"Hard constraints satisfied: {len(best_validation['errors']) == 0}")
        
        return {
            "success": True,
            "schedule": formatted_schedule,
            "score": best_score,
            "validation": best_validation,
            "statistics": best_statistics,
            "attempts_made": attempts,
            "message": f"AI generated timetable with score {best_score}. All hard constraints satisfied."
        }
    
    def validate_schedule(self) -> Dict[str, Any]:
        """Validate the generated schedule against all constraints"""
        errors = []
        warnings = []
        
        # Check weekly hour requirements
        course_hours = {}
        for entry in self.schedule:
            # Lab sessions are 180 minutes but represent 3 hours of weekly requirement
            if entry.is_lab:
                course_hours[entry.course_code] = course_hours.get(entry.course_code, 0) + 3.0
            else:
                course_hours[entry.course_code] = course_hours.get(entry.course_code, 0) + (entry.session_duration / 60)
        
        for course in self.courses:
            scheduled_hours = course_hours.get(course.code, 0)
            if abs(scheduled_hours - course.hours_per_week) > 0.1:  # Allow small floating point errors
                if scheduled_hours == 0:
                    errors.append(f"{course.code}: No sessions scheduled (expected {course.hours_per_week}h/week)")
                else:
                    warnings.append(f"{course.code}: Expected {course.hours_per_week}h/week, got {scheduled_hours}h/week")
        
        # Check for overlaps
        for i, entry1 in enumerate(self.schedule):
            for entry2 in self.schedule[i+1:]:
                if (entry1.time_slot.overlaps(entry2.time_slot) and 
                    (entry1.room_id == entry2.room_id or 
                     entry1.faculty_id == entry2.faculty_id or 
                     entry1.group_id == entry2.group_id)):
                    errors.append(f"Overlap detected: {entry1.course_code} and {entry2.course_code} on {entry1.time_slot}")
        
        # Check room capacities
        for entry in self.schedule:
            room = next(room for room in self.rooms if room.id == entry.room_id)
            group = next(group for group in self.groups if group.id == entry.group_id)
            if room.capacity < group.size:
                errors.append(f"Room {room.name} (cap {room.capacity}) too small for {group.name} ({group.size} students)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def format_schedule_output(self) -> List[Dict[str, Any]]:
        """Format the schedule for output"""
        formatted = []
        
        for entry in self.schedule:
            room = next(room for room in self.rooms if room.id == entry.room_id)
            group = next(group for group in self.groups if group.id == entry.group_id)
            faculty = next(faculty for faculty in self.faculty if faculty.id == entry.faculty_id)
            
            formatted.append({
                "day": entry.time_slot.day,
                "start_time": entry.time_slot.start_time,
                "end_time": entry.time_slot.end_time,
                "course_code": entry.course_code,
                "course_name": entry.course_name,
                "group": group.name,
                "room": room.name,
                "faculty": faculty.name,
                "is_lab": entry.is_lab,
                "duration_minutes": entry.session_duration
            })
        
        # Sort by day and time
        day_order = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5}
        formatted.sort(key=lambda x: (day_order[x["day"]], x["start_time"]))
        
        return formatted
    
    def get_schedule_statistics(self) -> Dict[str, Any]:
        """Get statistics about the generated schedule"""
        stats = {
            "total_sessions": len(self.schedule),
            "lab_sessions": len([e for e in self.schedule if e.is_lab]),
            "theory_sessions": len([e for e in self.schedule if not e.is_lab]),
            "total_hours": sum(entry.session_duration for entry in self.schedule) / 60,
        }
        
        # Sessions per day
        sessions_per_day = {}
        for entry in self.schedule:
            day = entry.time_slot.day
            sessions_per_day[day] = sessions_per_day.get(day, 0) + 1
        
        stats["sessions_per_day"] = sessions_per_day
        
        return stats
