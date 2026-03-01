"""
Firebase Admin SDK integration for state management and real-time data.
This is the SINGLE SOURCE OF TRUTH for all persistent state.
"""
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum

from config import config

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manages all Firebase interactions with proper error handling."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._app = None
            self._db = None
            self._initialize()
            self._initialized = True
    
    def _initialize(self):
        """Initialize Firebase Admin SDK with validation."""
        try:
            if not config.validate():
                raise ValueError("Invalid configuration")
            
            # Create credential from service account
            cred_dict = {
                "type": "service_account",
                "project_id": config.FIREBASE_PROJECT_ID,
                "private_key": config.FIREBASE_PRIVATE_KEY,
                "client_email": config.FIREBASE_CLIENT_EMAIL,
                "token_uri": "https://oauth2.googleapis.com/token"
            }
            
            cred = credentials.Certificate(cred_dict)
            
            # Initialize app if not already initialized
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(
                    cred,
                    {'databaseURL': config.FIREBASE_DATABASE_URL}
                )
                logger.info(f"Firebase initialized for project: {config.FIREBASE_PROJECT_ID}")
            else:
                self._app = firebase_admin.get_app()
                logger.info("Firebase app already initialized, reusing")
            
            # Initialize Firestore
            self._db = firestore.client()
            
            # Test connection
            self._test_connection()
            
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase initialization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected initialization error: {e}")
            raise
    
    def _test_connection(self):
        """Test Firebase connection by writing a heartbeat."""
        try:
            doc_ref = self._db.collection("system").document("heartbeat")
            doc_ref.set({
                "timestamp": datetime.now(timezone.utc),
                "status": "active",
                "component": "FirebaseManager"
            }, merge=True)
            logger.info("Firebase connection test successful")
        except Exception as e:
            logger.error(f"Firebase connection test failed: {e}")
            raise
    
    def save_strategy(self, strategy_id: str, strategy_data: Dict[str, Any]) -> bool:
        """Save a trading strategy to Firestore."""
        try:
            if not strategy_id or not strategy_data:
                logger.error("Invalid strategy_id or strategy_data")
                return False
            
            # Add metadata
            strategy_data.update({
                "last_updated": datetime.now(timezone.utc),
                "version": strategy_data.get("version", 1)
            })
            
            doc_ref = self._db.collection("strategies").document(strategy_id)
            doc_ref.set(strategy_data, merge=True)
            
            logger.info(f"Strategy saved: {strategy_id}")
            return True
            
        except exceptions.FirebaseError as e: