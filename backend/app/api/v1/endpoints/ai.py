from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.models.user import User
from app.services.auth import get_current_active_user
from app.services.ai.gemini import GeminiAIService
from app.db.mongodb import db
from bson import ObjectId

router = APIRouter()

class OptimizeRequest(BaseModel):
    timetable_id: str
    optimization_goals: Optional[Dict[str, Any]] = None

class SuggestionRequest(BaseModel):
    timetable_id: str
    focus_areas: Optional[list] = None

class AnalysisRequest(BaseModel):
    timetable_id: str
    analysis_type: str = "comprehensive"

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

@router.post("/optimize")
async def optimize_timetable(
    request: OptimizeRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Use AI to optimize an existing timetable. Users can only optimize their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} optimizing timetable {request.timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(request.timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {request.timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    try:
        ai_service = GeminiAIService()
        optimization_result = await ai_service.optimize_timetable(
            request.timetable_id, 
            request.optimization_goals or {}
        )
        return optimization_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI optimization failed: {str(e)}")

@router.post("/suggest")
async def suggest_improvements(
    request: SuggestionRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get AI suggestions for timetable improvements. Users can only get suggestions for their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} getting suggestions for timetable {request.timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(request.timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {request.timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    try:
        ai_service = GeminiAIService()
        suggestions = await ai_service.get_improvement_suggestions(
            request.timetable_id,
            request.focus_areas or []
        )
        return {
            "timetable_id": request.timetable_id,
            "suggestions": suggestions,
            "generated_at": "2025-08-30T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI suggestion failed: {str(e)}")

@router.post("/analysis")
async def analyze_timetable(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    AI analysis of timetable efficiency and compliance. Users can only analyze their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} analyzing timetable {request.timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(request.timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {request.timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    try:
        ai_service = GeminiAIService()
        analysis = await ai_service.analyze_timetable_efficiency(
            request.timetable_id,
            request.analysis_type
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/query")
async def natural_language_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Process natural language queries about timetables and scheduling.
    """
    try:
        ai_service = GeminiAIService()
        response = await ai_service.process_natural_language_query(
            request.query,
            request.context or {}
        )
        return {
            "query": request.query,
            "response": response,
            "processed_at": "2025-08-30T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/constraints/suggest/{program_id}")
async def suggest_constraints(
    program_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get AI-suggested constraints for a specific program.
    """
    # Check if program exists
    program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    try:
        ai_service = GeminiAIService()
        suggested_constraints = await ai_service.suggest_program_constraints(program_id)
        return {
            "program_id": program_id,
            "suggested_constraints": suggested_constraints,
            "generated_at": "2025-08-30T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Constraint suggestion failed: {str(e)}")

@router.post("/validate-schedule")
async def validate_schedule_with_ai(
    timetable_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Use AI to validate schedule against NEP 2020 guidelines and best practices. Users can only validate their own timetables.
    """
    print(f"🔒 SECURITY: User {current_user.id} validating timetable {timetable_id}")
    
    # CRITICAL: Check if timetable exists AND belongs to current user
    timetable = await db.db.timetables.find_one({
        "_id": ObjectId(timetable_id),
        "created_by": ObjectId(str(current_user.id))
    })
    if not timetable:
        print(f"🔒 SECURITY: Timetable {timetable_id} not found or not accessible by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    try:
        ai_service = GeminiAIService()
        validation_result = await ai_service.validate_nep_compliance(timetable_id)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI validation failed: {str(e)}")
