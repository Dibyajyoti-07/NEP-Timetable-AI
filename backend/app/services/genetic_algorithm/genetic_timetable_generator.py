from typing import List, Dict, Any, Optional, Tuple
import random
import numpy as np
from dataclasses import dataclass
from datetime import datetime, time, timedelta
import asyncio
import logging
from bson import ObjectId
from app.db.mongodb import db
from app.models.course import Course
from app.models.faculty import Faculty
from app.models.student_group import StudentGroup
from app.models.room import Room
from app.models.program import Program
from .data_collector import TimetableDataCollector

@dataclass
class TimeSlot:
    """Represents a time slot in the timetable"""
    day: str
    start_time: str
    end_time: str
    duration_minutes: int
    slot_index: int

@dataclass
class TimetableGene:
    """Represents a single gene in the chromosome (one class assignment)"""
    course_id: str
    faculty_id: str
    room_id: str
    group_id: str
    time_slot: TimeSlot
    session_type: str  # 'theory' or 'practical'

@dataclass
class Chromosome:
    """Represents a complete timetable solution"""
    genes: List[TimetableGene]
    fitness_score: float = 0.0
    
class GeneticTimetableGenerator:
    """Genetic Algorithm-based Timetable Generator"""
    
    def __init__(self, population_size: int = 50, generations: int = 100, 
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = 5
        self.logger = logging.getLogger(__name__)
        # Initialize data collector
        self.data_collector = TimetableDataCollector()
        
        # Data from six tabs
        self.academic_setup = {}
        self.courses = []
        self.faculty = []
        self.student_groups = []
        self.rooms = []
        self.time_rules = {}
        
        # Generated time slots
        self.time_slots = []
        

    
    def generate_time_slots(self) -> List[TimeSlot]:
        """Generate time slots based on time rules"""
        slots = []
        slot_index = 0
        
        for day in self.academic_setup["working_days"]:
            current_time = datetime.strptime(self.time_rules["college_start_time"], "%H:%M").time()
            end_time = datetime.strptime(self.time_rules["college_end_time"], "%H:%M").time()
            lunch_start = datetime.strptime(self.time_rules["lunch_start_time"], "%H:%M").time()
            lunch_end = datetime.strptime(self.time_rules["lunch_end_time"], "%H:%M").time()
            
            while current_time < end_time:
                # Calculate slot end time
                current_datetime = datetime.combine(datetime.today(), current_time)
                slot_end_datetime = current_datetime + timedelta(minutes=self.time_rules["class_duration"])
                slot_end_time = slot_end_datetime.time()
                
                # Skip lunch time
                if not (current_time >= lunch_start and current_time < lunch_end):
                    slot = TimeSlot(
                        day=day,
                        start_time=current_time.strftime("%H:%M"),
                        end_time=slot_end_time.strftime("%H:%M"),
                        duration_minutes=self.time_rules["class_duration"],
                        slot_index=slot_index
                    )
                    slots.append(slot)
                    slot_index += 1
                
                # Move to next slot with break
                current_datetime = slot_end_datetime + timedelta(minutes=self.time_rules["break_duration"])
                current_time = current_datetime.time()
        
        self.time_slots = slots
        return slots
    
    def create_random_chromosome(self) -> Chromosome:
        """Create a random chromosome (timetable solution)"""
        genes = []
        
        self.logger.info(f"Creating chromosome with {len(self.courses)} courses")
        
        for course in self.courses:
            course_id = course["id"]
            hours_per_week = course.get("hours_per_week", 3)
            is_lab = course.get("is_lab", False)
            
            self.logger.debug(f"Processing course {course.get('code', course_id)} - {hours_per_week} hours/week")
            
            # Find suitable faculty for this course
            suitable_faculty = [
                f for f in self.faculty 
                if course.get("code") in f.get("subjects", []) or 
                   course.get("name") in f.get("subjects", [])
            ]
            
            if not suitable_faculty:
                suitable_faculty = self.faculty  # Fallback to any faculty
                self.logger.debug(f"No specific faculty found for course {course.get('code')}, using all faculty")
            
            # Find suitable rooms
            if is_lab:
                suitable_rooms = [r for r in self.rooms if r.get("is_lab", False)]
            else:
                suitable_rooms = [r for r in self.rooms if not r.get("is_lab", False)]
            
            if not suitable_rooms:
                suitable_rooms = self.rooms  # Fallback to any room
                self.logger.debug(f"No specific rooms found for course {course.get('code')}, using all rooms")
            
            # Find student groups taking this course
            course_groups = [
                g for g in self.student_groups 
                if course_id in g.get("course_ids", [])
            ]
            
            self.logger.debug(f"Course {course.get('code')}: {len(course_groups)} groups, {len(suitable_faculty)} faculty, {len(suitable_rooms)} rooms, {len(self.time_slots)} time slots")

            # Create genes for required hours
            sessions_needed = hours_per_week
            for session in range(sessions_needed):
                if course_groups and suitable_faculty and suitable_rooms and self.time_slots:
                    gene = TimetableGene(
                        course_id=course_id,
                        faculty_id=random.choice(suitable_faculty)["id"],
                        room_id=random.choice(suitable_rooms)["id"],
                        group_id=random.choice(course_groups)["id"],
                        time_slot=random.choice(self.time_slots),
                        session_type="practical" if is_lab else "theory"
                    )
                    genes.append(gene)
                    self.logger.debug(f"Created gene {len(genes)} for course {course.get('code')} session {session + 1}")
                else:
                    self.logger.warning(f"Cannot create gene for course {course.get('code')} session {session + 1}: groups={len(course_groups)}, faculty={len(suitable_faculty)}, rooms={len(suitable_rooms)}, time_slots={len(self.time_slots)}")
        
        self.logger.info(f"Created chromosome with {len(genes)} genes")
        return Chromosome(genes=genes)
    
    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """Calculate fitness score for a chromosome"""
        score = 1000.0  # Start with perfect score
        
        # Penalty weights
        CONFLICT_PENALTY = 50
        FACULTY_OVERLOAD_PENALTY = 30
        ROOM_CAPACITY_PENALTY = 40
        CONTINUOUS_HOURS_PENALTY = 20
        PREFERENCE_PENALTY = 10
        
        # Check for conflicts
        conflicts = self._check_conflicts(chromosome)
        score -= len(conflicts) * CONFLICT_PENALTY
        
        # Check faculty workload
        faculty_hours = self._calculate_faculty_hours(chromosome)
        for faculty_id, hours in faculty_hours.items():
            faculty = next((f for f in self.faculty if f["id"] == faculty_id), None)
            if faculty:
                max_hours = faculty.get("max_hours_per_week", 16)
                if hours > max_hours:
                    score -= (hours - max_hours) * FACULTY_OVERLOAD_PENALTY
        
        # Check room capacity constraints
        room_violations = self._check_room_capacity(chromosome)
        score -= len(room_violations) * ROOM_CAPACITY_PENALTY
        
        # Check continuous hours constraint
        continuous_violations = self._check_continuous_hours(chromosome)
        score -= len(continuous_violations) * CONTINUOUS_HOURS_PENALTY
        
        # Preference bonuses (morning slots, balanced distribution)
        preference_score = self._calculate_preference_score(chromosome)
        score += preference_score
        
        return max(0, score)  # Ensure non-negative score
    
    def _check_conflicts(self, chromosome: Chromosome) -> List[str]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        # Group genes by time slot
        slot_assignments = {}
        for gene in chromosome.genes:
            slot_key = f"{gene.time_slot.day}_{gene.time_slot.start_time}"
            if slot_key not in slot_assignments:
                slot_assignments[slot_key] = []
            slot_assignments[slot_key].append(gene)
        
        # Check for conflicts in each time slot
        for slot_key, genes in slot_assignments.items():
            # Faculty conflicts
            faculty_ids = [g.faculty_id for g in genes]
            if len(faculty_ids) != len(set(faculty_ids)):
                conflicts.append(f"Faculty conflict in {slot_key}")
            
            # Room conflicts
            room_ids = [g.room_id for g in genes]
            if len(room_ids) != len(set(room_ids)):
                conflicts.append(f"Room conflict in {slot_key}")
            
            # Student group conflicts
            group_ids = [g.group_id for g in genes]
            if len(group_ids) != len(set(group_ids)):
                conflicts.append(f"Student group conflict in {slot_key}")
        
        return conflicts
    
    def _calculate_faculty_hours(self, chromosome: Chromosome) -> Dict[str, int]:
        """Calculate total hours for each faculty member"""
        faculty_hours = {}
        for gene in chromosome.genes:
            if gene.faculty_id not in faculty_hours:
                faculty_hours[gene.faculty_id] = 0
            faculty_hours[gene.faculty_id] += gene.time_slot.duration_minutes // 60
        return faculty_hours
    
    def _check_room_capacity(self, chromosome: Chromosome) -> List[str]:
        """Check room capacity violations"""
        violations = []
        for gene in chromosome.genes:
            room = next((r for r in self.rooms if r["id"] == gene.room_id), None)
            group = next((g for g in self.student_groups if g["id"] == gene.group_id), None)
            
            if room and group:
                room_capacity = room.get("capacity", 0)
                group_strength = group.get("student_strength", 0)
                if group_strength > room_capacity:
                    violations.append(f"Room {room.get('name')} capacity exceeded")
        
        return violations
    
    def _check_continuous_hours(self, chromosome: Chromosome) -> List[str]:
        """Check continuous hours constraint"""
        violations = []
        max_continuous = self.time_rules["max_continuous_hours"]
        
        # Group by day and faculty/group
        day_schedules = {}
        for gene in chromosome.genes:
            day = gene.time_slot.day
            key = f"{gene.faculty_id}_{gene.group_id}"
            
            if day not in day_schedules:
                day_schedules[day] = {}
            if key not in day_schedules[day]:
                day_schedules[day][key] = []
            
            day_schedules[day][key].append(gene.time_slot.slot_index)
        
        # Check continuous hours for each day
        for day, schedules in day_schedules.items():
            for key, slot_indices in schedules.items():
                slot_indices.sort()
                continuous_count = 1
                
                for i in range(1, len(slot_indices)):
                    if slot_indices[i] == slot_indices[i-1] + 1:
                        continuous_count += 1
                        if continuous_count > max_continuous:
                            violations.append(f"Continuous hours exceeded for {key} on {day}")
                    else:
                        continuous_count = 1
        
        return violations
    
    def _calculate_preference_score(self, chromosome: Chromosome) -> float:
        """Calculate preference-based bonus score"""
        score = 0
        
        # Morning slot preference
        for gene in chromosome.genes:
            start_hour = int(gene.time_slot.start_time.split(':')[0])
            if start_hour < 12:  # Morning slots
                score += 5
        
        # Balanced distribution bonus
        day_counts = {}
        for gene in chromosome.genes:
            day = gene.time_slot.day
            day_counts[day] = day_counts.get(day, 0) + 1
        
        # Bonus for balanced distribution across days
        if day_counts:
            avg_per_day = sum(day_counts.values()) / len(day_counts)
            variance = sum((count - avg_per_day) ** 2 for count in day_counts.values()) / len(day_counts)
            score += max(0, 50 - variance)  # Lower variance = higher score
        
        return score
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Perform crossover between two chromosomes"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # Single-point crossover
        min_genes = min(len(parent1.genes), len(parent2.genes))
        if min_genes <= 1:
            # If chromosomes have 0 or 1 genes, return copies
            return Chromosome(genes=parent1.genes.copy()), Chromosome(genes=parent2.genes.copy())
        
        crossover_point = random.randint(1, min_genes - 1)
        
        child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
        
        return Chromosome(genes=child1_genes), Chromosome(genes=child2_genes)
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """Perform mutation on a chromosome"""
        if random.random() > self.mutation_rate:
            return chromosome
        
        # Random mutation: change a random gene's assignment
        if chromosome.genes:
            gene_index = random.randint(0, len(chromosome.genes) - 1)
            gene = chromosome.genes[gene_index]
            
            # Mutate one aspect of the gene
            mutation_type = random.choice(['faculty', 'room', 'time_slot'])
            
            if mutation_type == 'faculty' and self.faculty:
                # Find suitable faculty for the course
                course = next((c for c in self.courses if c["id"] == gene.course_id), None)
                if course:
                    suitable_faculty = [
                        f for f in self.faculty 
                        if course.get("code") in f.get("subjects", []) or 
                           course.get("name") in f.get("subjects", [])
                    ]
                    if suitable_faculty:
                        gene.faculty_id = random.choice(suitable_faculty)["id"]
            
            elif mutation_type == 'room' and self.rooms:
                # Find suitable room
                is_lab = gene.session_type == 'practical'
                suitable_rooms = [r for r in self.rooms if r.get("is_lab", False) == is_lab]
                if suitable_rooms:
                    gene.room_id = random.choice(suitable_rooms)["id"]
            
            elif mutation_type == 'time_slot' and self.time_slots:
                gene.time_slot = random.choice(self.time_slots)
        
        return chromosome
    
    def selection(self, population: List[Chromosome]) -> List[Chromosome]:
        """Select parents for next generation using tournament selection"""
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            tournament = random.sample(population, min(tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x.fitness_score)
            selected.append(winner)
        
        return selected
    
    async def generate_timetable(self, program_id: str, semester: int, academic_year: str) -> Dict[str, Any]:
        """Main genetic algorithm function to generate timetable"""
        try:
            self.logger.info(f"Starting timetable generation for program {program_id}, semester {semester}")
            
            # Step 1: Collect data from all tabs using data collector
            collected_data = await self.data_collector.collect_all_data(program_id, semester, academic_year)
            
            # Validate collected data
            if not await self.data_collector.validate_collected_data(collected_data):
                raise ValueError("Invalid or incomplete data collected from tabs")
            
            # Update instance variables with collected data
            self.academic_setup = collected_data['academic_setup']
            self.courses = collected_data['courses']
            self.faculty = collected_data['faculty']
            self.student_groups = collected_data['student_groups']
            self.rooms = collected_data['rooms']
            self.time_rules = collected_data['time_rules']
            
            # Debug logging
            self.logger.info(f"Data collected - Courses: {len(self.courses)}, Faculty: {len(self.faculty)}, Groups: {len(self.student_groups)}, Rooms: {len(self.rooms)}")
            if len(self.courses) == 0:
                self.logger.warning("No courses found for timetable generation")
            if len(self.student_groups) == 0:
                self.logger.warning("No student groups found for timetable generation")
            if len(self.faculty) == 0:
                self.logger.warning("No faculty found for timetable generation")
            if len(self.rooms) == 0:
                self.logger.warning("No rooms found for timetable generation")
            
            # Get data summary
            data_summary = await self.data_collector.get_data_summary(collected_data)
            
            # Step 2: Generate time slots if not already generated
            if not self.time_slots:
                self.generate_time_slots()
            
            if not self.time_slots:
                raise ValueError("No time slots generated")
            
            # Step 3: Initialize population
            population = []
            for _ in range(self.population_size):
                chromosome = self.create_random_chromosome()
                chromosome.fitness_score = self.calculate_fitness(chromosome)
                population.append(chromosome)
            
            # Step 4: Evolution loop
            best_fitness_history = []
            
            for generation in range(self.generations):
                # Calculate fitness for all chromosomes
                for chromosome in population:
                    chromosome.fitness_score = self.calculate_fitness(chromosome)
                
                # Sort by fitness (descending)
                population.sort(key=lambda x: x.fitness_score, reverse=True)
                
                # Track best fitness
                best_fitness = population[0].fitness_score
                best_fitness_history.append(best_fitness)
                
                # Elite selection
                new_population = population[:self.elite_size]
                
                # Generate offspring
                while len(new_population) < self.population_size:
                    # Selection
                    parents = self.selection(population[:self.population_size//2])
                    parent1, parent2 = random.sample(parents, 2)
                    
                    # Crossover
                    child1, child2 = self.crossover(parent1, parent2)
                    
                    # Mutation
                    child1 = self.mutate(child1)
                    child2 = self.mutate(child2)
                    
                    new_population.extend([child1, child2])
                
                population = new_population[:self.population_size]
            
            # Step 5: Return best solution
            best_chromosome = max(population, key=lambda x: x.fitness_score)
            
            # Convert to timetable format
            timetable_entries = []
            for gene in best_chromosome.genes:
                entry = {
                    "course_id": gene.course_id,
                    "faculty_id": gene.faculty_id,
                    "room_id": gene.room_id,
                    "group_id": gene.group_id,
                    "time_slot": {
                        "day": gene.time_slot.day,
                        "start_time": gene.time_slot.start_time,
                        "end_time": gene.time_slot.end_time,
                        "duration_minutes": gene.time_slot.duration_minutes
                    },
                    "session_type": gene.session_type
                }
                timetable_entries.append(entry)
            
            self.logger.info("Timetable generation completed successfully")
            
            return {
                "success": True,
                "data_collected": data_summary,
                "time_slots_generated": len(self.time_slots),
                "generations_completed": self.generations,
                "best_fitness_score": best_chromosome.fitness_score,
                "fitness_history": best_fitness_history,
                "timetable_entries": timetable_entries,
                "conflicts": self._check_conflicts(best_chromosome),
                "total_classes_scheduled": len(timetable_entries)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating timetable: {str(e)}")
            raise