"""
Configuration management for the Autonomous Meta-Trading Framework.
Centralizes all environment variables, constants, and system-wide settings.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """System configuration with validation and defaults."""
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")
    
    # Trading Configuration
    DEFAULT_EXCHANGE: str = "binance"
    DEFAULT_TIMEFRAME: str = "1h"
    INITIAL_CAPITAL: float = 10000.0
    MAX_POSITION_SIZE: float = 0.1  # 10% of capital
    MAX_DRAWDOWN: float = 0.25  # 25% max drawdown
    
    # Model Configuration
    MODEL_SAVE_PATH: str = "./models/"
    BACKTEST_WINDOW_DAYS: int = 365
    MIN_TRAINING_SAMPLES: int = 1000
    
    # System Configuration
    HEARTBEAT_INTERVAL_SECONDS: int = 60
    MAX_CONCURRENT_STRATEGIES: int = 5
    LOG_LEVEL: str = "INFO"
    
    # External APIs (if configured)
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    
    def validate(self) -> bool:
        """Validate critical configuration."""
        errors = []
        
        # Firebase validation
        if not self.FIREBASE_PROJECT_ID:
            errors.append("FIREBASE_PROJECT_ID is required")
        if not self.FIREBASE_PRIVATE_KEY:
            errors.append("FIREBASE_PRIVATE_KEY is required")
        if not self.FIREBASE_CLIENT_EMAIL:
            errors.append("FIREBASE_CLIENT_EMAIL is required")
            
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
            return False
            
        # Ensure model directory exists
        os.makedirs(self.MODEL_SAVE_PATH, exist_ok=True)
        
        logger.info("Configuration validated successfully")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for logging."""
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith("_") and k != "FIREBASE_PRIVATE_KEY"}

# Global configuration instance
config = Config()