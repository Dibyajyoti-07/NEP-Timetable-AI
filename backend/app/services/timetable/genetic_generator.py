from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
import random
import math
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Import from the existing advanced generator
from .advanced_generator import (
    AdvancedTimetableGenerator, TimeSlot, CourseRequirement, 
    StudentGroup, Room, Faculty, ScheduleEntry, SchedulingRules,
    t2min, min2t, DAY_NAMES
)

@dataclass
class Individual:
    """Represents a single timetable solution in the genetic algorithm"""
    schedule: List[ScheduleEntry]
    fitness: float = 0.0
    constraint_violations: int = 0
    
    def __post_init__(self):
        """Calculate fitness after initialization"""
        if not hasattr(self, '_fitness_calculated'):
            self.calculate_fitness()
            self._fitness_calculated = True
    
    def calculate_fitness(self):
        """Calculate fitness score for this individual"""
        # Start with base score
        score = 1000
        violations = 0
        
        # Hard constraint violations (heavily penalized)
        violations += self._check_hard_constraints()
        
        # Soft constraint scoring
        score += self._calculate_soft_constraint_score()
        
        # Apply penalty for constraint violations
        score -= violations * 100
        
        self.fitness = max(0, score)  # Ensure non-negative fitness
        self.constraint_violations = violations
    
    def _check_hard_constraints(self) -> int:
        """Check hard constraints and return violation count"""
        violations = 0
        
        # Check for overlapping sessions
        for i, entry1 in enumerate(self.schedule):
            for j, entry2 in enumerate(self.schedule[i+1:], i+1):
                # Same group, faculty, or room at same time
                if entry1.time_slot.overlaps(entry2.time_slot):
                    if (entry1.group_id == entry2.group_id or 
                        entry1.faculty_id == entry2.faculty_id or 
                        entry1.room_id == entry2.room_id):
                        violations += 1
        
        # Check daily constraints
        daily_sessions = {}
        for entry in self.schedule:
            key = (entry.group_id, entry.time_slot.day)
            if key not in daily_sessions:
                daily_sessions[key] = []
            daily_sessions[key].append(entry)
        
        for (group_id, day), sessions in daily_sessions.items():
            # Max periods per day
            if len(sessions) > SchedulingRules.ABSOLUTE_MAX_PERIODS_PER_DAY:
                violations += len(sessions) - SchedulingRules.ABSOLUTE_MAX_PERIODS_PER_DAY
            
            # Max labs per day
            lab_count = sum(1 for s in sessions if s.is_lab)
            if lab_count > SchedulingRules.MAX_LABS_PER_DAY_PER_GROUP:
                violations += lab_count - SchedulingRules.MAX_LABS_PER_DAY_PER_GROUP
        
        return violations
    
    def _calculate_soft_constraint_score(self) -> int:
        """Calculate score based on soft constraints"""
        score = 0
        
        # Group sessions by day and group
        daily_sessions = {}
        for entry in self.schedule:
            key = (entry.group_id, entry.time_slot.day)
            if key not in daily_sessions:
                daily_sessions[key] = []
            daily_sessions[key].append(entry)
        
        # Prefer afternoon labs
        for entry in self.schedule:
            if entry.is_lab:
                if t2min("13:20") <= entry.time_slot.start_min <= t2min("16:30"):
                    score += 15
                else:
                    score -= 5
        
        # Prefer optimal daily load (7-9 periods)
        for sessions in daily_sessions.values():
            daily_count = len(sessions)
            if 7 <= daily_count <= 9:
                score += 10
            elif daily_count < 7:
                score += 5
            else:
                score -= 10
        
        # Minimize gaps between sessions
        for sessions in daily_sessions.values():
            if len(sessions) > 1:
                sorted_sessions = sorted(sessions, key=lambda x: x.time_slot.start_min)
                for i in range(len(sorted_sessions) - 1):
                    gap = sorted_sessions[i+1].time_slot.start_min - sorted_sessions[i].time_slot.end_min
                    if gap <= 10:  # Consecutive
                        score += 5
                    elif gap > 60:  # Large gap
                        score -= 3
        
        # Spread heavy courses across days
        heavy_courses = ["OS_THEORY", "OOP_THEORY", "ML_THEORY"]
        for course in heavy_courses:
            course_days = set()
            for entry in self.schedule:
                if entry.course_code == course:
                    course_days.add(entry.time_slot.day)
            
            if len(course_days) >= 3:
                score += 15
            elif len(course_days) == 2:
                score += 8
            else:
                score -= 10
        
        return score

class GeneticTimetableGenerator(AdvancedTimetableGenerator):
    """Enhanced timetable generator using genetic algorithm"""
    
    def __init__(self, population_size: int = 50, generations: int = 100, 
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8,
                 elite_size: int = 5, tournament_size: int = 5):
        super().__init__()
        
        # Genetic algorithm parameters
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        
        # Evolution tracking
        self.generation_stats = []
        self.best_individual = None
        
        # Available slots cache
        self._theory_slots = None
        self._lab_slots = None
        self._double_period_slots = None
    
    def _get_available_slots(self):
        """Cache available slots for efficiency"""
        if self._theory_slots is None:
            rules = SchedulingRules()
            self._theory_slots = rules.get_theory_slots()
            self._lab_slots = rules.get_lab_slots()
            self._double_period_slots = rules.get_double_period_slots()
    
    def create_random_individual(self) -> Individual:
        """Create a random valid individual"""
        self._get_available_slots()
        
        # Reset state
        self.initialize_occupancy_tracking()
        schedule = []
        
        # Get all required sessions
        required_sessions = []
        
        # Add lab sessions
        for course in self.courses:
            if course.is_lab:
                for group in self.groups:
                    if not group.is_subgroup:  # Only main groups for labs
                        required_sessions.append((course, group, True))
        
        # Add theory sessions
        for course in self.courses:
            if not course.is_lab:
                session_durations = course.get_session_structure()
                for group in self.groups:
                    if not group.is_subgroup:  # Only main groups
                        for duration in session_durations:
                            required_sessions.append((course, group, False, duration))
        
        # Shuffle for randomness
        random.shuffle(required_sessions)
        
        # Try to schedule each session
        for session_info in required_sessions:
            if len(session_info) == 3:  # Lab session
                course, group, is_lab = session_info
                duration = course.lab_duration
                available_slots = self._lab_slots.copy()
            else:  # Theory session
                course, group, is_lab, duration = session_info
                if duration == 100:  # Double period
                    available_slots = self._double_period_slots.copy()
                else:
                    available_slots = self._theory_slots.copy()
            
            # Shuffle slots for randomness
            random.shuffle(available_slots)
            
            # Try to find a valid slot
            scheduled = False
            for slot in available_slots:
                # Adjust slot duration if needed
                if duration != slot.duration:
                    adjusted_slot = TimeSlot(
                        day=slot.day,
                        start_min=slot.start_min,
                        end_min=slot.start_min + duration
                    )
                else:
                    adjusted_slot = slot
                
                # Find resources
                faculty_id = self.find_suitable_faculty(course.code)
                room_id = self.find_suitable_room(group.size, is_lab)
                
                if not faculty_id or not room_id:
                    continue
                
                # Check availability
                if self.is_slot_available(adjusted_slot, room_id, faculty_id, group.id):
                    # Book the slot
                    self.book_slot(adjusted_slot, room_id, faculty_id, group.id)
                    
                    # Add to schedule
                    entry = ScheduleEntry(
                        course_code=course.code,
                        course_name=course.name,
                        group_id=group.id,
                        faculty_id=faculty_id,
                        room_id=room_id,
                        time_slot=adjusted_slot,
                        is_lab=is_lab,
                        session_duration=duration
                    )
                    schedule.append(entry)
                    scheduled = True
                    break
            
            # If we couldn't schedule this session, continue with others
            # The fitness function will penalize incomplete schedules
        
        return Individual(schedule=schedule)
    
    def create_initial_population(self) -> List[Individual]:
        """Create initial population of random individuals"""
        print(f"Creating initial population of {self.population_size} individuals...")
        population = []
        
        # Use threading for faster population creation
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.create_random_individual) 
                      for _ in range(self.population_size)]
            
            for future in as_completed(futures):
                try:
                    individual = future.result()
                    population.append(individual)
                except Exception as e:
                    print(f"Error creating individual: {e}")
                    # Create a simple fallback individual
                    population.append(Individual(schedule=[]))
        
        return population
    
    def tournament_selection(self, population: List[Individual]) -> Individual:
        """Select individual using tournament selection"""
        tournament = random.sample(population, min(self.tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Create offspring using order crossover"""
        if random.random() > self.crossover_rate:
            return deepcopy(parent1), deepcopy(parent2)
        
        # Combine schedules from both parents
        all_sessions = parent1.schedule + parent2.schedule
        
        # Remove duplicates based on course and group
        seen = set()
        unique_sessions = []
        
        for session in all_sessions:
            key = (session.course_code, session.group_id, session.is_lab)
            if key not in seen:
                seen.add(key)
                unique_sessions.append(session)
        
        # Split into two offspring
        mid = len(unique_sessions) // 2
        random.shuffle(unique_sessions)
        
        offspring1 = Individual(schedule=unique_sessions[:mid])
        offspring2 = Individual(schedule=unique_sessions[mid:])
        
        return offspring1, offspring2
    
    def mutate(self, individual: Individual) -> Individual:
        """Mutate an individual by modifying some sessions"""
        if random.random() > self.mutation_rate:
            return individual
        
        mutated = deepcopy(individual)
        
        if not mutated.schedule:
            return mutated
        
        # Choose mutation type
        mutation_type = random.choice(['time_change', 'resource_change', 'swap_sessions'])
        
        if mutation_type == 'time_change' and mutated.schedule:
            # Change time slot of a random session
            session_idx = random.randint(0, len(mutated.schedule) - 1)
            session = mutated.schedule[session_idx]
            
            # Get appropriate slots
            if session.is_lab:
                available_slots = self._lab_slots
            elif session.session_duration == 100:
                available_slots = self._double_period_slots
            else:
                available_slots = self._theory_slots
            
            new_slot = random.choice(available_slots)
            if session.session_duration != new_slot.duration:
                new_slot = TimeSlot(
                    day=new_slot.day,
                    start_min=new_slot.start_min,
                    end_min=new_slot.start_min + session.session_duration
                )
            
            mutated.schedule[session_idx].time_slot = new_slot
        
        elif mutation_type == 'resource_change' and mutated.schedule:
            # Change faculty or room of a random session
            session_idx = random.randint(0, len(mutated.schedule) - 1)
            session = mutated.schedule[session_idx]
            
            # Try to change faculty
            new_faculty = self.find_suitable_faculty(session.course_code)
            if new_faculty and new_faculty != session.faculty_id:
                mutated.schedule[session_idx].faculty_id = new_faculty
        
        elif mutation_type == 'swap_sessions' and len(mutated.schedule) >= 2:
            # Swap time slots of two random sessions
            idx1, idx2 = random.sample(range(len(mutated.schedule)), 2)
            session1, session2 = mutated.schedule[idx1], mutated.schedule[idx2]
            
            # Swap time slots
            mutated.schedule[idx1].time_slot, mutated.schedule[idx2].time_slot = \
                session2.time_slot, session1.time_slot
        
        # Recalculate fitness
        mutated.calculate_fitness()
        return mutated
    
    def evolve_population(self, population: List[Individual]) -> List[Individual]:
        """Evolve population for one generation"""
        # Sort by fitness
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Keep elite individuals
        new_population = population[:self.elite_size]
        
        # Generate offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self.tournament_selection(population)
            parent2 = self.tournament_selection(population)
            
            # Crossover
            offspring1, offspring2 = self.crossover(parent1, parent2)
            
            # Mutation
            offspring1 = self.mutate(offspring1)
            offspring2 = self.mutate(offspring2)
            
            new_population.extend([offspring1, offspring2])
        
        # Trim to exact population size
        return new_population[:self.population_size]
    
    def generate_timetable_genetic(self) -> Dict[str, Any]:
        """Generate timetable using genetic algorithm"""
        print("[INFO] Starting Genetic Algorithm Timetable Generation...")
        start_time = time.time()
        
        # Setup
        self.setup_cse_ai_ml_courses()
        self.setup_groups_and_resources()
        self._get_available_slots()
        
        # Create initial population
        population = self.create_initial_population()
        
        # Evolution loop
        for generation in range(self.generations):
            # Evolve
            population = self.evolve_population(population)
            
            # Track statistics
            best_fitness = max(ind.fitness for ind in population)
            avg_fitness = sum(ind.fitness for ind in population) / len(population)
            best_violations = min(ind.constraint_violations for ind in population)
            
            self.generation_stats.append({
                'generation': generation,
                'best_fitness': best_fitness,
                'avg_fitness': avg_fitness,
                'best_violations': best_violations
            })
            
            # Update best individual
            current_best = max(population, key=lambda x: x.fitness)
            if self.best_individual is None or current_best.fitness > self.best_individual.fitness:
                self.best_individual = deepcopy(current_best)
            
            # Progress reporting
            if generation % 10 == 0 or generation == self.generations - 1:
                print(f"Generation {generation}: Best Fitness = {best_fitness:.2f}, "
                      f"Avg Fitness = {avg_fitness:.2f}, Violations = {best_violations}")
            
            # Early stopping if perfect solution found
            if best_violations == 0 and best_fitness > 1500:
                print(f"Perfect solution found at generation {generation}!")
                break
        
        end_time = time.time()
        
        # Prepare results
        if self.best_individual and self.best_individual.schedule:
            self.schedule = self.best_individual.schedule
            formatted_schedule = self.format_schedule_output()
            validation_result = self.validate_schedule()
            statistics = self.get_schedule_statistics()
            
            print(f"\n[SUCCESS] Genetic Algorithm Complete!")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            print(f"Best fitness: {self.best_individual.fitness:.2f}")
            print(f"Constraint violations: {self.best_individual.constraint_violations}")
            print(f"Total sessions scheduled: {len(self.best_individual.schedule)}")
            
            return {
                "success": True,
                "schedule": formatted_schedule,
                "fitness": self.best_individual.fitness,
                "constraint_violations": self.best_individual.constraint_violations,
                "validation": validation_result,
                "statistics": statistics,
                "generation_stats": self.generation_stats,
                "generations_run": len(self.generation_stats),
                "time_taken": end_time - start_time,
                "message": f"Genetic algorithm generated timetable with fitness {self.best_individual.fitness:.2f}"
            }
        else:
            return {
                "success": False,
                "error": "Genetic algorithm failed to generate a valid timetable",
                "generation_stats": self.generation_stats,
                "time_taken": end_time - start_time
            }
    
    def generate_timetable(self) -> Dict[str, Any]:
        """Override the main generation method to use genetic algorithm"""
        return self.generate_timetable_genetic()