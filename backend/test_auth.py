#!/usr/bin/env python3
"""Test authentication."""
import asyncio
from app.core.db import AsyncSessionLocal, init_db
from app.core.auth import authenticate_user, get_user_by_username

async def test():
    """Test auth."""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        print("Testing authentication...")
        
        # Check if user exists
        user = await get_user_by_username(session, "admin")
        if user:
            print(f"✓ User 'admin' found: {user.username}")
            print(f"  Active: {user.is_active}")
            print(f"  Admin: {user.is_admin}")
        else:
            print("✗ User 'admin' not found")
            return
        
        # Test authentication
        auth_user = await authenticate_user(session, "admin", "teamflow")
        if auth_user:
            print("✓ Authentication successful")
        else:
            print("✗ Authentication failed")

if __name__ == "__main__":
    asyncio.run(test())
