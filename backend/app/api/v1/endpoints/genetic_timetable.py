from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.services.auth import get_current_active_user
from app.models.user import User
from app.services.genetic_algorithm.genetic_timetable_generator import GeneticTimetableGenerator
from pydantic import BaseModel, Field
from bson import ObjectId
from app.db.mongodb import db
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class GeneticTimetableRequest(BaseModel):
    """Request model for genetic algorithm timetable generation"""
    program_id: str = Field(..., description="Program ID")
    semester: int = Field(..., description="Semester number", ge=1, le=8)
    academic_year: str = Field(..., description="Academic year (e.g., '2024-25')")
    title: str = Field(..., description="Timetable title")
    
    # Optional genetic algorithm parameters
    population_size: int = Field(50, description="Population size for genetic algorithm", ge=10, le=200)
    generations: int = Field(100, description="Number of generations", ge=10, le=500)
    mutation_rate: float = Field(0.1, description="Mutation rate", ge=0.01, le=0.5)
    crossover_rate: float = Field(0.8, description="Crossover rate", ge=0.1, le=1.0)
    
    # Optional time and rules configuration
    time_rules: Dict[str, Any] = Field(default_factory=dict, description="Custom time rules configuration")

class GeneticTimetableResponse(BaseModel):
    """Response model for genetic algorithm timetable generation"""
    success: bool
    message: str
    timetable_id: str = None
    generation_stats: Dict[str, Any] = None
    data_summary: Dict[str, Any] = None
    conflicts: list = None
    fitness_score: float = None
    entries: list = None

@router.post("/generate", response_model=GeneticTimetableResponse)
async def generate_genetic_timetable(
    request: GeneticTimetableRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate timetable using genetic algorithm approach"""
    try:
        logger.info(f"Starting genetic algorithm timetable generation for program {request.program_id}")
        
        # Validate program exists
        program = await db.db.programs.find_one({"_id": ObjectId(request.program_id)})
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program not found: {request.program_id}"
            )
        
        # Initialize genetic algorithm generator
        generator = GeneticTimetableGenerator()
        
        # Set custom parameters if provided
        if request.population_size:
            generator.population_size = request.population_size
        if request.generations:
            generator.generations = request.generations
        if request.mutation_rate:
            generator.mutation_rate = request.mutation_rate
        if request.crossover_rate:
            generator.crossover_rate = request.crossover_rate
        
        # Set custom time rules if provided
        if request.time_rules:
            generator.time_rules.update(request.time_rules)
        
        # Generate timetable using genetic algorithm
        result = await generator.generate_timetable(
            program_id=request.program_id,
            semester=request.semester,
            academic_year=request.academic_year
        )
        
        logger.info(f"Genetic algorithm result: {result.keys()}")
        logger.info(f"Timetable entries count: {len(result.get('timetable_entries', []))}")
        print(f"DEBUG: Genetic algorithm result keys: {result.keys()}")
        print(f"DEBUG: Timetable entries count: {len(result.get('timetable_entries', []))}")
        print(f"DEBUG: First few entries: {result.get('timetable_entries', [])[:2]}")
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate timetable using genetic algorithm"
            )
        
        # Save the generated timetable to database
        timetable_doc = {
            "title": request.title,
            "program_id": ObjectId(request.program_id),
            "semester": request.semester,
            "academic_year": request.academic_year,
            "entries": result["timetable_entries"],
            "is_draft": False,
            "created_by": ObjectId(current_user.id),
            "created_at": datetime.utcnow(),
            "generated_at": datetime.utcnow(),
            "generation_method": "genetic_algorithm",
            "validation_status": "generated",
            "optimization_score": result["best_fitness_score"],
            "metadata": {
                "genetic_algorithm_stats": {
                    "generations_completed": result["generations_completed"],
                    "population_size": generator.population_size,
                    "mutation_rate": generator.mutation_rate,
                    "crossover_rate": generator.crossover_rate,
                    "fitness_history": result["fitness_history"],
                    "final_fitness_score": result["best_fitness_score"],
                    "total_classes_scheduled": result["total_classes_scheduled"],
                    "conflicts_detected": len(result["conflicts"]),
                    "data_summary": result["data_collected"]
                },
                "time_slots_generated": result["time_slots_generated"],
                "conflicts": result["conflicts"]
            }
        }
        
        # Insert timetable into database
        insert_result = await db.db.timetables.insert_one(timetable_doc)
        timetable_id = str(insert_result.inserted_id)
        
        logger.info(f"Genetic algorithm timetable generated successfully with ID: {timetable_id}")
        
        # Create response with entries included for frontend display
        response_data = {
            "success": True,
            "message": "Timetable generated successfully using genetic algorithm",
            "timetable_id": timetable_id,
            "generation_stats": {
                "generations_completed": result["generations_completed"],
                "population_size": generator.population_size,
                "mutation_rate": generator.mutation_rate,
                "crossover_rate": generator.crossover_rate,
                "total_classes_scheduled": result["total_classes_scheduled"],
                "time_slots_generated": result["time_slots_generated"]
            },
            "data_summary": {
                **result["data_collected"],
                "total_entries": result["total_classes_scheduled"]
            },
            "conflicts": result["conflicts"],
            "fitness_score": result["best_fitness_score"],
            "entries": result["timetable_entries"]  # Include entries for frontend display
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating genetic algorithm timetable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/algorithm-info")
async def get_genetic_algorithm_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get information about the genetic algorithm implementation"""
    return {
        "algorithm_name": "Genetic Algorithm for Timetable Generation",
        "description": "Advanced AI-based timetable generation using genetic algorithms",
        "data_sources": {
            "academic_setup": "Program, semester, academic year, working days configuration",
            "courses": "Course code, name, credits, type, hours/week, min/session",
            "faculty": "Name, subjects, max hours/week, available days",
            "student_groups": "Group name, courses, year, semester, section, strength",
            "rooms": "Room number, type, capacity",
            "time_rules": "College hours, lunch time, class intervals, constraints"
        },
        "genetic_algorithm_features": {
            "chromosome_representation": "Each gene represents a class assignment (course, faculty, room, group, time)",
            "fitness_function": "Evaluates conflicts, faculty workload, room capacity, continuous hours, preferences",
            "selection_method": "Tournament selection",
            "crossover_method": "Single-point crossover",
            "mutation_method": "Random gene modification (faculty, room, or time slot)",
            "elite_preservation": "Top 5 solutions preserved each generation"
        },
        "constraints_handled": [
            "No faculty conflicts (same faculty, different classes, same time)",
            "No room conflicts (same room, different classes, same time)",
            "No student group conflicts (same group, different classes, same time)",
            "Faculty maximum hours per week",
            "Room capacity vs student group strength",
            "Maximum continuous hours constraint",
            "Maximum classes per day",
            "Lunch break scheduling"
        ],
        "optimization_objectives": [
            "Minimize scheduling conflicts",
            "Balance faculty workload",
            "Optimize room utilization",
            "Prefer morning time slots",
            "Distribute classes evenly across days",
            "Respect continuous hours limits"
        ],
        "default_parameters": {
            "population_size": 50,
            "generations": 100,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
            "elite_size": 5
        }
    }

@router.post("/analyze-data")
async def analyze_timetable_data(
    program_id: str,
    semester: int,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze available data for timetable generation"""
    try:
        # Validate program exists
        program = await db.db.programs.find_one({"_id": ObjectId(program_id)})
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program not found: {program_id}"
            )
        
        # Initialize generator to collect data
        generator = GeneticTimetableGenerator()
        data_summary = await generator.collect_data_from_tabs(program_id, semester, "2024-25")
        
        # Additional analysis
        analysis = {
            "data_availability": data_summary,
            "readiness_check": {
                "courses_available": data_summary["courses"] > 0,
                "faculty_available": data_summary["faculty"] > 0,
                "student_groups_available": data_summary["student_groups"] > 0,
                "rooms_available": data_summary["rooms"] > 0,
                "ready_for_generation": all([
                    data_summary["courses"] > 0,
                    data_summary["faculty"] > 0,
                    data_summary["student_groups"] > 0,
                    data_summary["rooms"] > 0
                ])
            },
            "recommendations": []
        }
        
        # Add recommendations based on data availability
        if data_summary["courses"] == 0:
            analysis["recommendations"].append("Add courses for the selected program and semester")
        if data_summary["faculty"] == 0:
            analysis["recommendations"].append("Add faculty members for the department")
        if data_summary["student_groups"] == 0:
            analysis["recommendations"].append("Create student groups for the program")
        if data_summary["rooms"] == 0:
            analysis["recommendations"].append("Add rooms/classrooms to the system")
        
        if analysis["readiness_check"]["ready_for_generation"]:
            analysis["recommendations"].append("System is ready for genetic algorithm timetable generation")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing timetable data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )