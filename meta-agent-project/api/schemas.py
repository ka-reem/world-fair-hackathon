from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AgentBlueprint(BaseModel):
    """Schema for agent blueprint"""
    type: str
    name: str
    capabilities: List[str]
    config: Dict[str, Any]
    description: Optional[str] = None

class AgentRequest(BaseModel):
    """Schema for agent processing request"""
    blueprint_id: str
    input_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Schema for agent processing response"""
    status: str
    type: str
    data: Dict[str, Any]
    error: Optional[str] = None

class BlueprintResponse(BaseModel):
    """Schema for blueprint registration response"""
    blueprint_id: str
    status: str
    message: str
