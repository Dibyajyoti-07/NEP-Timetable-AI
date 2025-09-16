#!/usr/bin/env python3
import asyncio
from app.db.mongodb import connect_to_mongo, db

async def check_users():
    await connect_to_mongo()
    users = await db.db.users.find().to_list(length=None)
    print(f'Found {len(users)} users in database')
    
    for i, user in enumerate(users, 1):
        email = user.get('email', 'No email')
        name = user.get('name', 'No name')
        is_active = user.get('is_active', False)
        is_admin = user.get('is_admin', False)
        
        print(f'{i}. {name} ({email})')
        print(f'   ID: {user["_id"]}')
        print(f'   Active: {is_active}, Admin: {is_admin}')
        print()

if __name__ == '__main__':
    asyncio.run(check_users())