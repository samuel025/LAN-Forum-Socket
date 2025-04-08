import bcrypt
import re

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(stored_password, provided_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def validate_username(username):
    """Validate username format"""
    # Username must be 3-20 characters, alphanumeric and underscores only
    pattern = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    return bool(pattern.match(username))

def validate_password(password):
    """Validate password strength"""
    # Password must be at least 8 characters
    return len(password) >= 8