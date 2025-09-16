from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.user import MongoBaseModel

class TimeSlot(BaseModel):
    day: str = Field(..., description="Day of the week")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    duration_minutes: int = Field(..., description="Duration in minutes")

# inside TimetableEntry
class TimetableEntry(BaseModel):
    model_config = {"extra": "allow"}  # Allow extra fields for backward compatibility
    
    course_id: Optional[str] = Field(None, description="Course ID")
    faculty_id: Optional[str] = Field(None, description="Faculty ID")
    room_id: Optional[str] = Field(None, description="Room ID")
    group_id: Optional[str] = Field(None, description="Student group / lab subgroup ID")
    time_slot: Optional[TimeSlot] = Field(None, description="Time slot details")
    
    # Optional fields that might be present in database entries
    course_code: Optional[str] = Field(None, description="Course code")
    course_name: Optional[str] = Field(None, description="Course name")
    faculty_name: Optional[str] = Field(None, description="Faculty name")
    room_name: Optional[str] = Field(None, description="Room name")
    day: Optional[str] = Field(None, description="Day (legacy field)")
    start_time: Optional[str] = Field(None, description="Start time (legacy field)")
    end_time: Optional[str] = Field(None, description="End time (legacy field)")
    is_lab: Optional[bool] = Field(None, description="Is lab session")
    duration: Optional[int] = Field(None, description="Duration in minutes (legacy field)")


class TimetableBase(BaseModel):
    model_config = {"extra": "allow"}  # Allow extra fields for backward compatibility
    
    title: str = Field(..., description="Timetable title")
    program_id: str = Field(..., description="Program ID")
    semester: int = Field(..., description="Semester number")
    academic_year: str = Field(..., description="Academic year (e.g., '2024-25')")
    entries: List[TimetableEntry] = Field(default=[], description="Timetable entries")
    is_draft: bool = Field(default=True, description="Whether this is a draft")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class TimetableCreate(BaseModel):
    title: str = Field(..., description="Timetable title")
    program_id: str = Field(..., description="Program ID")
    semester: int = Field(..., description="Semester number")
    academic_year: str = Field(..., description="Academic year (e.g., '2024-25')")
    metadata: Optional[Dict[str, Any]] = None

class TimetableUpdate(BaseModel):
    title: Optional[str] = None
    program_id: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    entries: Optional[List[TimetableEntry]] = None
    is_draft: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class Timetable(TimetableBase, MongoBaseModel):
    created_by: str = Field(..., description="User who created this timetable")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    validation_status: str = Field(default="pending", description="Validation status")
    optimization_score: Optional[float] = Field(None, description="AI optimization score")