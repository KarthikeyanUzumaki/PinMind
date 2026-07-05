import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    uid = Column(String, primary_key=True, index=True) # Firebase unique User ID
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    keys = relationship("UserKeys", back_populates="owner", cascade="all, delete-orphan")

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="workspaces")
    hardware_context = relationship("HardwareContext", back_populates="workspace", uselist=False, cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="workspace", cascade="all, delete-orphan")

class HardwareContext(Base):
    __tablename__ = "hardware_contexts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False)
    mcu = Column(String, nullable=False, default="STM32F401")
    framework = Column(String, nullable=True)
    compiler = Column(String, nullable=True)
    board = Column(String, nullable=True)
    platformio_env = Column(String, nullable=True)
    clocks = Column(JSON, nullable=False, default=dict)
    gpios = Column(JSON, nullable=False, default=list)
    peripherals = Column(JSON, nullable=False, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="hardware_context")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False) # 'user', 'ai', 'system'
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True) # stores recall metrics, version, time
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="chats")

class UserKeys(Base):
    __tablename__ = "user_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), unique=True, nullable=False)
    encrypted_gemini_key = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="keys")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.uid", ondelete="CASCADE"), unique=True, nullable=False)
    preferences = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User")
