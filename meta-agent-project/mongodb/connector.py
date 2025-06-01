from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
import os

class MongoDBConnector:
    """MongoDB connection and operations handler"""
    
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGODB_DB", "meta_agent")]
        self.blueprints: Collection = self.db.blueprints
        self.results: Collection = self.db.results
    
    def store_blueprint(self, blueprint: Dict[str, Any]) -> str:
        """Store a new blueprint"""
        result = self.blueprints.insert_one(blueprint)
        return str(result.inserted_id)
    
    def get_blueprint(self, blueprint_id: str) -> Optional[Dict[str, Any]]:
        """Get a blueprint by ID"""
        return self.blueprints.find_one({"_id": blueprint_id})
    
    def get_all_blueprints(self) -> Dict[str, Any]:
        """Get all blueprints"""
        return {
            str(bp["_id"]): bp
            for bp in self.blueprints.find()
        }
    
    def store_result(self, blueprint_id: str, result: Dict[str, Any]) -> None:
        """Store an agent execution result"""
        self.results.insert_one({
            "blueprint_id": blueprint_id,
            "result": result,
            "timestamp": datetime.utcnow()
        })
