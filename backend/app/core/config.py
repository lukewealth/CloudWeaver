# CloudWeaver - Multi-Agent Cloud Orchestrator
# Core configuration and shared utilities

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application configuration"""
    
    # App
    APP_NAME: str = "CloudWeaver"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://cloudweaver:password@localhost/cloudweaver"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    
    # Cloud Providers
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    GCP_PROJECT_ID: Optional[str] = None
    GCP_SERVICE_ACCOUNT_KEY: Optional[str] = None
    
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    
    # Agent Configuration
    AGENT_HEARTBEAT_INTERVAL: int = 30
    AGENT_MAX_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 300
    
    # Cost Optimization
    COST_OPTIMIZATION_ENABLED: bool = True
    COST_SAVINGS_THRESHOLD: float = 50.0  # Minimum $ to act
    
    # Security
    SECURITY_SCAN_INTERVAL_MINUTES: int = 15
    VAULT_ADDR: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()