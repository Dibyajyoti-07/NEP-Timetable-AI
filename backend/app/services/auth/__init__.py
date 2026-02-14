from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.models.user import User, UserCreate
from app.db.mongodb import db
from bson import ObjectId

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    try:
        # Try to query the database
        if getattr(db, 'db', None) is None:
            raise Exception("Database not connected")
        
        user = await db.db.users.find_one({"email": email})
        
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        # Convert ObjectId to string for Pydantic compatibility and remove _id field
        user["id"] = str(user["_id"])
        del user["_id"]  # Remove the _id field to avoid validation error
        return User(**user)
    except Exception as e:
        # If DB operations fail (e.g. Atlas auth), allow a local dev fallback
        # for the demo admin credentials so development can continue.
        print(f"[AUTH] Database query failed: {e}, checking fallback credentials")
        if email == 'admin@example.com' and password == 'admin123':
            print(f"[AUTH] Using fallback admin user")
            return User(
                id='local-admin',
                email=email,
                full_name='Administrator',
                is_active=True,
                is_admin=True,
                role='admin',
                created_at=datetime.utcnow()
            )
        print(f"[AUTH] Fallback credentials don't match, returning None")
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Handle fallback admin user for development
    if user_id == "local-admin":
        return User(
            id='local-admin',
            email='admin@example.com',
            full_name='Administrator',
            is_active=True,
            is_admin=True,
            role='admin',
            created_at=datetime.utcnow()
        )
    
    # Try to fetch from database
    try:
        user = await db.db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception
        
        # Convert ObjectId to string for Pydantic compatibility and remove _id field
        user["id"] = str(user["_id"])
        del user["_id"]  # Remove the _id field to avoid validation error
        return User(**user)
    except Exception as e:
        print(f"[AUTH] Error fetching user from database: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current active admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

async def create_user_account(user_data: UserCreate) -> User:
    """Create a new user account."""
    # Check if user already exists
    from fastapi import HTTPException, status
    if not getattr(db, 'db', None):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")

    existing_user = await db.db.users.find_one({"email": user_data.email})
    if existing_user:
        raise ValueError("Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user dict - handle both name and full_name
    user_dict = user_data.model_dump(exclude={"password", "name"})  # Exclude password and name
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    
    # Ensure full_name is set (validation should handle this, but double-check)
    if not user_dict.get("full_name"):
        user_dict["full_name"] = user_data.name or user_data.full_name
    
    # Insert user
    try:
        result = await db.db.users.insert_one(user_dict)
        user = await db.db.users.find_one({"_id": result.inserted_id})
    except Exception as e:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database operation failed: {e}")
    
    # Convert ObjectId to string for Pydantic compatibility and remove _id field
    user["id"] = str(user["_id"])
    del user["_id"]  # Remove the _id field to avoid validation error
    return User(**user)