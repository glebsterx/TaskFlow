#!/usr/bin/env python3
"""Create admin user."""
import asyncio
import sys
from app.core.db import AsyncSessionLocal, init_db
from app.core.auth import create_user


async def create_admin_user(username: str, password: str):
    """Create admin user."""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            # Проверяем существует ли пользователь
            from app.core.auth import get_user_by_username
            existing_user = await get_user_by_username(session, username)
            
            if existing_user:
                print(f"✓ Admin user '{username}' already exists")
                return True
            
            # Создаём нового пользователя
            user = await create_user(
                session,
                username=username,
                password=password,
                is_admin=True
            )
            await session.commit()
            print(f"✓ Admin user '{username}' created successfully")
            return True
        except Exception as e:
            await session.rollback()
            print(f"✗ Error creating admin user: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    success = asyncio.run(create_admin_user(username, password))
    sys.exit(0 if success else 1)
