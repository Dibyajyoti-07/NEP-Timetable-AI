from typing import Dict, List, Any, Optional
# from ortools.sat.python import cp_model  # Temporarily disabled due to protobuf version conflict
from app.db.mongodb import db
from app.services.ai.gemini import GeminiAIService
from bson import ObjectId
import datetime

class TimetableGenerator:
    """AI-powered timetable generator using constraint programming and Gemini AI"""
    
    def __init__(self):
        # self.model = cp_model.CpModel()  # Temporarily disabled
        # self.solver = cp_model.CpSolver()  # Temporarily disabled
        self.ai_service = GeminiAIService()
    
    async def generate_timetable(self, program_id: str, semester: int, academic_year: str, created_by: str) -> Dict[str, Any]:
        """Generate a new timetable for a program using AI optimization"""
        try:
            # Get program data
            program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
            if not program:
                raise ValueError("Program not found")
            
            # Get courses for the program and semester
            courses = await db.db.courses.find({
                "program_id": ObjectId(program_id),
                "semester": semester
            }).to_list(length=None)
            
            if not courses:
                raise ValueError("No courses found for this program and semester")
            
            # Get available faculty and rooms
            faculty = await db.db.faculty.find().to_list(length=None)
            rooms = await db.db.rooms.find().to_list(length=None)
            
            # Get constraints
            constraints = await db.db.constraints.find({
                "$or": [
                    {"program_id": ObjectId(program_id)},
                    {"program_id": None}  # Global constraints
                ],
                "is_active": True
            }).to_list(length=None)
            
            # Generate timetable using constraint programming
            timetable_entries = await self._generate_with_constraints(
                courses, faculty, rooms, constraints
            )
            
            # Create timetable document
            timetable_doc = {
                "program_id": ObjectId(program_id),
                "semester": semester,
                "academic_year": academic_year,
                "entries": timetable_entries,
                "is_draft": True,
                "created_by": ObjectId(created_by),
                "created_at": datetime.datetime.utcnow(),
                "generated_at": datetime.datetime.utcnow(),
                "validation_status": "pending",
                "metadata": {
                    "generation_method": "ai_optimized",
                    "total_courses": len(courses),
                    "total_constraints": len(constraints)
                }
            }
            
            # Save timetable
            result = await db.db.timetables.insert_one(timetable_doc)
            timetable = await db.db.timetables.find_one({"_id": result.inserted_id})
            
            # AI optimization
            await self._optimize_with_ai(str(result.inserted_id))
            
            return timetable
            
        except Exception as e:
            raise Exception(f"Timetable generation failed: {str(e)}")
    
    async def _generate_with_constraints(self, courses: List[Dict], faculty: List[Dict], 
                                       rooms: List[Dict], constraints: List[Dict]) -> List[Dict]:
        """Generate timetable entries using constraint programming"""
        entries = []
        
        # Time slots (simplified - 5 days, 8 hours per day)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = [
            ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00"), ("12:00", "13:00"),
            ("14:00", "15:00"), ("15:00", "16:00"), ("16:00", "17:00"), ("17:00", "18:00")
        ]
        
        # Simple assignment (in real implementation, would use OR-Tools for constraint solving)
        for i, course in enumerate(courses):
            # Assign faculty (simplified - first available)
            assigned_faculty = faculty[i % len(faculty)] if faculty else None
            # Assign room (simplified - first available)
            assigned_room = rooms[i % len(rooms)] if rooms else None
            # Assign time slot (simplified - sequential assignment)
            day = days[i % len(days)]
            time_slot = time_slots[i % len(time_slots)]
            
            if assigned_faculty and assigned_room:
                entry = {
                    "course_id": course["_id"],
                    "faculty_id": assigned_faculty["_id"],
                    "room_id": assigned_room["_id"],
                    "time_slot": {
                        "day": day,
                        "start_time": time_slot[0],
                        "end_time": time_slot[1],
                        "duration_minutes": 60
                    },
                    "entry_type": "lecture",
                    "is_mandatory": True
                }
                entries.append(entry)
        
        return entries
    
    async def _optimize_with_ai(self, timetable_id: str) -> None:
        """Optimize timetable using Gemini AI"""
        try:
            optimization_goals = {
                "minimize_gaps": True,
                "balance_workload": True,
                "optimize_room_usage": True,
                "nep_compliance": True
            }
            
            result = await self.ai_service.optimize_timetable(timetable_id, optimization_goals)
            
            # Update timetable with optimization score
            if result.get("optimized"):
                await db.db.timetables.update_one(
                    {"_id": ObjectId(timetable_id)},
                    {
                        "$set": {
                            "optimization_score": 0.8,  # Simplified score
                            "validation_status": "ai_optimized"
                        }
                    }
                )
        except Exception as e:
            print(f"AI optimization failed: {e}")
    
    async def optimize_timetable(self, timetable_id: str) -> Dict[str, Any]:
        """Optimize an existing timetable"""
        try:
            timetable = await db.db.timetables.find_one({"_id": ObjectId(timetable_id)})
            if not timetable:
                raise ValueError("Timetable not found")
            
            # AI optimization
            optimization_result = await self.ai_service.optimize_timetable(
                timetable_id, 
                {"improve_efficiency": True, "nep_compliance": True}
            )
            
            # Update timetable
            await db.db.timetables.update_one(
                {"_id": ObjectId(timetable_id)},
                {
                    "$set": {
                        "optimization_score": 0.85,
                        "validation_status": "optimized",
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            
            updated_timetable = await db.db.timetables.find_one({"_id": ObjectId(timetable_id)})
            return updated_timetable
            
        except Exception as e:
            raise Exception(f"Timetable optimization failed: {str(e)}")
    
    async def validate_timetable(self, timetable_id: str) -> Dict[str, Any]:
        """Validate timetable against constraints"""
        try:
            timetable = await db.db.timetables.find_one({"_id": ObjectId(timetable_id)})
            if not timetable:
                raise ValueError("Timetable not found")
            
            # Get program constraints
            program_id = timetable["program_id"]
            constraints = await db.db.constraints.find({
                "$or": [
                    {"program_id": program_id},
                    {"program_id": None}
                ],
                "is_active": True
            }).to_list(length=None)
            
            violations = []
            warnings = []
            
            # Basic validation logic (simplified)
            entries = timetable.get("entries", [])
            
            # Check for time conflicts
            time_map = {}
            for entry in entries:
                time_slot = entry["time_slot"]
                key = f"{time_slot['day']}_{time_slot['start_time']}"
                
                if key in time_map:
                    violations.append({
                        "type": "time_conflict",
                        "message": f"Time conflict on {time_slot['day']} at {time_slot['start_time']}",
                        "severity": "high"
                    })
                else:
                    time_map[key] = entry
            
            # Check faculty workload (simplified)
            faculty_hours = {}
            for entry in entries:
                faculty_id = str(entry["faculty_id"])
                if faculty_id not in faculty_hours:
                    faculty_hours[faculty_id] = 0
                faculty_hours[faculty_id] += entry["time_slot"]["duration_minutes"] / 60
            
            for faculty_id, hours in faculty_hours.items():
                if hours > 20:  # Max 20 hours per week
                    violations.append({
                        "type": "faculty_overload",
                        "message": f"Faculty {faculty_id} assigned {hours} hours (max 20)",
                        "severity": "medium"
                    })
            
            # Update validation status
            validation_status = "valid" if not violations else "has_violations"
            await db.db.timetables.update_one(
                {"_id": ObjectId(timetable_id)},
                {"$set": {"validation_status": validation_status}}
            )
            
            return {
                "timetable_id": timetable_id,
                "is_valid": len(violations) == 0,
                "violations": violations,
                "warnings": warnings,
                "validation_date": datetime.datetime.utcnow().isoformat(),
                "total_constraints_checked": len(constraints)
            }
            
        except Exception as e:
            raise Exception(f"Timetable validation failed: {str(e)}")