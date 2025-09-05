from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.models.user import User
from app.models.timetable import Timetable, TimetableCreate, TimetableUpdate
from app.services.auth import get_current_active_user
from app.services.timetable.generator import TimetableGenerator
from app.services.timetable.advanced_generator import AdvancedTimetableGenerator
from app.services.timetable.exporter import TimetableExporter
from app.db.mongodb import db
from bson import ObjectId
import io
import datetime

router = APIRouter()

@router.get("/", response_model=List[Timetable])
async def get_timetables(
    skip: int = Query(0, ge=0, description="Number of timetables to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of timetables to return"),
    program_id: Optional[str] = Query(None, description="Filter by program ID"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    is_draft: Optional[bool] = Query(None, description="Filter by draft status"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all timetables created by the current user with optional filtering.
    """
    # CRITICAL: Always filter by created_by to ensure user isolation
    filter_query = {"created_by": ObjectId(str(current_user.id))}
    
    if program_id:
        filter_query["program_id"] = ObjectId(program_id)
    if semester is not None:
        filter_query["semester"] = semester
    if academic_year:
        filter_query["academic_year"] = academic_year
    if is_draft is not None:
        filter_query["is_draft"] = is_draft
    
    print(f"🔒 SECURITY: Getting timetables for user {current_user.id} with filter: {filter_query}")
    
    timetables = await db.db.timetables.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
    
    print(f"🔒 SECURITY: Found {len(timetables)} timetables for user {current_user.id}")
    
    # Convert ObjectIds to strings for JSON serialization
    for timetable in timetables:
        # Convert _id to id for frontend compatibility
        timetable["id"] = str(timetable["_id"])
        del timetable["_id"]  # Remove the original _id field
        
        if "created_by" in timetable and timetable["created_by"]:
            timetable["created_by"] = str(timetable["created_by"])
        if "program_id" in timetable and timetable["program_id"]:
            timetable["program_id"] = str(timetable["program_id"])
        
        # Handle missing title field for old timetables
        if "title" not in timetable or not timetable["title"]:
            timetable["title"] = f"Timetable - {timetable.get('academic_year', 'Unknown')} Semester {timetable.get('semester', 'N/A')}"
        
        # Handle missing created_at field
        if "created_at" not in timetable or timetable["created_at"] is None:
            from datetime import datetime
            timetable["created_at"] = datetime.utcnow()
    
    return timetables

@router.get("/{timetable_id}", response_model=Timetable)
async def get_timetable(
    timetable_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific timetable by ID. Users can only access their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} requesting timetable {timetable_id}")
    
    # CRITICAL: Filter by both ID and created_by to ensure user isolation
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    
    if not timetable:
        print(f"🔒 SECURITY: Timetable {timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    print(f"🔒 SECURITY: Successfully retrieved timetable {timetable_id} for user {current_user.id}")
    
    # Convert ObjectIds to strings for JSON serialization
    # Convert _id to id for frontend compatibility
    timetable["id"] = str(timetable["_id"])
    del timetable["_id"]  # Remove the original _id field
    
    if "created_by" in timetable and timetable["created_by"]:
        timetable["created_by"] = str(timetable["created_by"])
    if "program_id" in timetable and timetable["program_id"]:
        timetable["program_id"] = str(timetable["program_id"])
    
    # Handle missing title field for old timetables
    if "title" not in timetable or not timetable["title"]:
        timetable["title"] = f"Timetable - {timetable.get('academic_year', 'Unknown')} Semester {timetable.get('semester', 'N/A')}"
    
    # Handle missing created_at field
    if "created_at" not in timetable or timetable["created_at"] is None:
        from datetime import datetime
        timetable["created_at"] = datetime.utcnow()
    
    return timetable

@router.post("/", response_model=Timetable)
async def create_timetable(
    timetable_data: TimetableCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new empty timetable.
    """
    timetable_dict = timetable_data.dict()
    timetable_dict["created_by"] = ObjectId(str(current_user.id))
    # Convert program_id string to ObjectId for storage
    timetable_dict["program_id"] = ObjectId(timetable_dict["program_id"])
    timetable_dict["entries"] = []
    timetable_dict["is_draft"] = True
    
    result = await db.db.timetables.insert_one(timetable_dict)
    timetable = await db.db.timetables.find_one({"_id": result.inserted_id})
    
    # Convert ObjectIds to strings for JSON serialization
    if timetable:
        # Convert _id to id for frontend compatibility
        timetable["id"] = str(timetable["_id"])
        del timetable["_id"]  # Remove the original _id field
        
        timetable["created_by"] = str(timetable["created_by"])
        if "program_id" in timetable and timetable["program_id"]:
            timetable["program_id"] = str(timetable["program_id"])
    
    return timetable

@router.post("/draft", response_model=dict)
async def save_draft_timetable(
    draft_data: dict,
    current_user: User = Depends(get_current_active_user),
):
    """
    Save or update a draft timetable with partial data.
    """
    try:
        # Extract timetable ID if updating existing draft
        timetable_id = draft_data.get('id')
        
        if timetable_id:
            # Update existing draft - CRITICAL: Ensure user owns this timetable
            print(f"🔒 SECURITY: User {current_user.id} updating timetable {timetable_id}")
            
            update_data = {
                **draft_data,
                "is_draft": True,
                "last_modified": draft_data.get('lastModified'),
                "modified_by": ObjectId(str(current_user.id))
            }
            # Remove ID from update data
            update_data.pop('id', None)
            
            # CRITICAL: Filter by both ID and created_by to ensure user isolation
            result = await db.db.timetables.update_one(
                {
                    "_id": ObjectId(timetable_id),
                    "created_by": ObjectId(str(current_user.id))  # Ensure user owns this timetable
                },
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                print(f"🔒 SECURITY: Draft timetable {timetable_id} not found or not accessible by user {current_user.id}")
                raise HTTPException(status_code=404, detail="Draft timetable not found")
            
            print(f"🔒 SECURITY: Successfully updated timetable {timetable_id} for user {current_user.id}")
            return {"message": "Draft saved successfully", "id": timetable_id}
        else:
            # Create new draft
            draft_dict = {
                **draft_data,
                "created_by": ObjectId(str(current_user.id)),
                "created_at": draft_data.get('lastModified'),
                "is_draft": True,
                "validation_status": "pending",
                "entries": []
            }
            
            result = await db.db.timetables.insert_one(draft_dict)
            return {"message": "Draft created successfully", "id": str(result.inserted_id)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save draft: {str(e)}")

@router.post("/generate", response_model=Timetable)
async def generate_timetable(
    program_id: str,
    semester: int,
    academic_year: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a new timetable using AI optimization.
    """
    try:
        # Check if program exists
        program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        # Create timetable generator
        generator = TimetableGenerator()
        
        # Generate timetable
        timetable = await generator.generate_timetable(
            program_id=program_id,
            semester=semester,
            academic_year=academic_year,
            created_by=str(current_user.id)
        )
        
        return timetable
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating timetable: {str(e)}")

@router.post("/generate-advanced")
async def generate_advanced_timetable(
    request: dict,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a new timetable using advanced constraint-based algorithm with hard and soft rules.
    Specifically designed for CSE AI & ML program with detailed scheduling requirements.
    """
    try:
        # Extract parameters from request
        program_id = request.get("program_id")
        semester = request.get("semester")
        academic_year = request.get("academic_year")
        title = request.get("title", "Advanced AI Generated Timetable")
        
        if not all([program_id, semester, academic_year]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: program_id, semester, academic_year"
            )
        
        # Check if program exists
        program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        
        print(f"🚀 Starting advanced timetable generation for program {program_id}")
        
        # Create advanced timetable generator
        generator = AdvancedTimetableGenerator()
        
        # Generate timetable using the advanced algorithm
        result = generator.generate_timetable()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        print(f"✅ Advanced generation successful with score: {result['score']}")
        
        # Convert the generated schedule to timetable entries
        entries = []
        for session in result["schedule"]:
            entries.append({
                "course_id": session["course_code"],  # Using course_code as ID for now
                "faculty_id": "default_faculty",     # Will be mapped properly later
                "room_id": session["room"],
                "time_slot": {
                    "day": session["day"],
                    "start_time": session["start_time"],
                    "end_time": session["end_time"],
                    "duration_minutes": session["duration_minutes"]
                },
                "group_id": session["group"]
            })
        
        # Create timetable document
        timetable_doc = {
            "title": title,
            "program_id": ObjectId(program_id),
            "semester": semester,
            "academic_year": academic_year,
            "entries": entries,
            "is_draft": False,
            "created_by": ObjectId(str(current_user.id)),
            "created_at": datetime.datetime.utcnow(),
            "generated_at": datetime.datetime.utcnow(),
            "validation_status": "valid" if result["validation"]["valid"] else "invalid",
            "optimization_score": result["score"],
            "metadata": {
                "generation_method": "advanced_constraint_based",
                "algorithm_version": "v2.0",
                "statistics": result["statistics"],
                "validation_report": result["validation"],
                "schedule_details": result["schedule"]
            }
        }
        
        # Save to database
        result_db = await db.db.timetables.insert_one(timetable_doc)
        saved_timetable = await db.db.timetables.find_one({"_id": result_db.inserted_id})
        
        # Convert ObjectIds to strings for JSON serialization
        if saved_timetable:
            saved_timetable["id"] = str(saved_timetable["_id"])
            del saved_timetable["_id"]
            
            if "created_by" in saved_timetable and saved_timetable["created_by"]:
                saved_timetable["created_by"] = str(saved_timetable["created_by"])
            if "program_id" in saved_timetable and saved_timetable["program_id"]:
                saved_timetable["program_id"] = str(saved_timetable["program_id"])
        
        return {
            "success": True,
            "message": "Advanced timetable generated successfully",
            "timetable": saved_timetable,
            "generation_details": {
                "score": result["score"],
                "statistics": result["statistics"],
                "validation": result["validation"]
            }
        }
        
    except Exception as e:
        print(f"❌ Error in advanced timetable generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating advanced timetable: {str(e)}")

@router.put("/{timetable_id}", response_model=Timetable)
async def update_timetable(
    timetable_id: str,
    timetable_data: TimetableUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a timetable. Users can only update their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} updating timetable {timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    # Update timetable
    update_data = {k: v for k, v in timetable_data.dict().items() if v is not None}
    if update_data:
        # CRITICAL: Filter by both ID and created_by to ensure user isolation
        await db.db.timetables.update_one(
            {
                "_id": ObjectId(timetable_id),
                "created_by": ObjectId(str(current_user.id))
            }, 
            {"$set": update_data}
        )
    
    updated_timetable = await db.db.timetables.find_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    
    print(f"🔒 SECURITY: Successfully updated timetable {timetable_id} for user {current_user.id}")
    
    # Convert ObjectIds to strings for JSON serialization
    if updated_timetable:
        # Convert _id to id for frontend compatibility
        updated_timetable["id"] = str(updated_timetable["_id"])
        del updated_timetable["_id"]  # Remove the original _id field
        
        if "created_by" in updated_timetable and updated_timetable["created_by"]:
            updated_timetable["created_by"] = str(updated_timetable["created_by"])
        if "program_id" in updated_timetable and updated_timetable["program_id"]:
            updated_timetable["program_id"] = str(updated_timetable["program_id"])
    
    return updated_timetable

@router.delete("/{timetable_id}")
async def delete_timetable(
    timetable_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a timetable. Users can only delete their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} deleting timetable {timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    # CRITICAL: Delete with user isolation
    result = await db.db.timetables.delete_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    
    if result.deleted_count == 0:
        print(f"🔒 SECURITY: Failed to delete timetable {timetable_id} for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    print(f"🔒 SECURITY: Successfully deleted timetable {timetable_id} for user {current_user.id}")
    return {"message": "Timetable deleted successfully"}

@router.get("/{timetable_id}/export/{format_type}")
async def export_timetable_endpoint(
    timetable_id: str,
    format_type: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Export a timetable in the specified format (excel, pdf, json). Users can only export their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} exporting timetable {timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    # Export timetable
    try:
        format_type = format_type.lower()
        exporter = TimetableExporter()
        
        if format_type == "json":
            result = await exporter.export_timetable(timetable_id, format_type)
            return result
        
        elif format_type == "excel":
            excel_data = await exporter.export_timetable(timetable_id, format_type)
            
            # Create response with appropriate headers
            return StreamingResponse(
                excel_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=timetable_{timetable_id}.xlsx"}
            )
        
        elif format_type == "pdf":
            pdf_data = await exporter.export_timetable(timetable_id, format_type)
            
            # Check if we got HTML (when WeasyPrint is not available) or PDF
            try:
                # Try to decode as UTF-8 to determine if it's HTML
                html_test = pdf_data.decode('utf-8')
                # If it doesn't raise, it's HTML
                return StreamingResponse(
                    io.BytesIO(pdf_data),
                    media_type="text/html",
                    headers={"Content-Disposition": f"attachment; filename=timetable_{timetable_id}.html"}
                )
            except UnicodeDecodeError:
                # If it raises, it's PDF
                return StreamingResponse(
                    io.BytesIO(pdf_data),
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=timetable_{timetable_id}.pdf"}
                )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format_type}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting timetable: {str(e)}")

@router.post("/{timetable_id}/optimize")
async def optimize_timetable(
    timetable_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Optimize an existing timetable using AI.
    """
    # Check if timetable exists
    timetable = await db.db.timetables.find_one({"_id": ObjectId(timetable_id)})
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    try:
        generator = TimetableGenerator()
        optimized_timetable = await generator.optimize_timetable(timetable_id)
        return optimized_timetable
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing timetable: {str(e)}")

@router.post("/{timetable_id}/validate")
async def validate_timetable(
    timetable_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Validate a timetable against constraints.
    """
    # Check if timetable exists
    timetable = await db.db.timetables.find_one({"_id": ObjectId(timetable_id)})
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    try:
        generator = TimetableGenerator()
        validation_result = await generator.validate_timetable(timetable_id)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating timetable: {str(e)}")