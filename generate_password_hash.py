#!/usr/bin/env python3
"""Generate password hash for TeamFlow."""
import sys
from passlib.context import CryptContext

if len(sys.argv) != 2:
    print("Usage: python3 generate_password_hash.py <password>")
    sys.exit(1)

password = sys.argv[1]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash(password))
