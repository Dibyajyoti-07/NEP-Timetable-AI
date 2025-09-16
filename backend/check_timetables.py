#!/usr/bin/env python3
import asyncio
from app.db.mongodb import connect_to_mongo, db

async def check_timetables():
    await connect_to_mongo()
    timetables = await db.db.timetables.find().to_list(length=None)
    print(f'Found {len(timetables)} timetables in database')
    
    for i, timetable in enumerate(timetables, 1):
        title = timetable.get('title', 'No title')
        program_id = timetable.get('program_id', 'No program')
        semester = timetable.get('semester', 'No semester')
        academic_year = timetable.get('academic_year', 'No year')
        is_draft = timetable.get('is_draft', False)
        created_by = timetable.get('created_by', 'No creator')
        
        print(f'{i}. {title}')
        print(f'   ID: {timetable["_id"]}')
        print(f'   Program: {program_id}')
        print(f'   Semester: {semester}, Year: {academic_year}')
        print(f'   Draft: {is_draft}, Created by: {created_by}')
        print()

if __name__ == '__main__':
    asyncio.run(check_timetables())