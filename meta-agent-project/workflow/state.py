from typing import Dict, Any, Optional, List
from typing_extensions import TypedDict

class AgentSystemState(TypedDict):
    # Input
    task_input: str
    task_context: Dict[str, Any]
    
    # Analysis results
    task_analysis: Optional[Dict[str, Any]]
    capabilities_required: List[str]
    task_type: str
    
    # Agent matching
    available_agents: List[Any]
    chosen_agent: Optional[Any]
    agent_created: bool
    agents_created: int
    agent_attempts: Dict[str, int]
    
    # Task execution
    agent_output: Optional[Dict[str, Any]]
    execution_success: bool
    
    # Evaluation
    evaluation_result: Optional[Dict[str, Any]]
    output_acceptable: bool
    review_notes: str
    
    # Flow control
    retry_count: int
    max_retries: int
    spawn_attempted: bool
    correction_attempted: bool
    allow_agent_creation: bool
    
    # Final output
    final_response: Optional[Dict[str, Any]]
    error_message: Optional[str] 