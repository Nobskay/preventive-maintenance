"""
User model for authentication and RBAC
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="technician")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
