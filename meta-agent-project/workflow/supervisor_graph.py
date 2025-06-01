from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional, List
import logging
import io
import base64
import asyncio

from .state import AgentSystemState
from meta_agent.task_analyzer import TaskAnalyzer
from meta_agent.registry import AgentRegistry
from meta_agent.validator import ResponseValidator
from agents.agent_factory import AgentFactory, BaseAgent

logger = logging.getLogger(__name__)

class SupervisorGraph:
    def __init__(self, llm, allow_agent_creation: bool = True, initial_agents: List[str] = None):
        self.llm = llm
        self.analyzer = TaskAnalyzer(llm)
        self.registry = AgentRegistry()
        self.validator = ResponseValidator(llm)
        self.factory = AgentFactory(llm)
        self.allow_agent_creation = allow_agent_creation
        
        # Set default initial agents to only fun_fact_agent
        if initial_agents is None:
            initial_agents = ["fun_fact_agent"]
        self.initial_agents = initial_agents
        
        # Initialize existing agents
        self._initialize_agents()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"Initialized SupervisorGraph with agent creation {'enabled' if allow_agent_creation else 'disabled'}")
        logger.info(f"Initial agents: {self.initial_agents}")
    
    def get_graph_visualization(self, output_format="png"):
        """Generate a visual representation of the workflow graph"""
        try:
            # Get the graph structure for visualization
            graph_representation = self.graph.get_graph()
            
            # Handle the graph representation properly
            nodes = []
            edges = []
            
            if hasattr(graph_representation, 'nodes'):
                nodes = list(graph_representation.nodes())
            if hasattr(graph_representation, 'edges'):
                edges = list(graph_representation.edges())
            
            # Return information about the graph structure
            return {
                "nodes": nodes,
                "edges": edges,
                "graph_type": "LangGraph StateGraph",
                "visualization_available": True,
                "description": "Agent workflow visualization showing task flow from analysis to completion"
            }
        except Exception as e:
            logger.error(f"Failed to generate graph visualization: {e}")
            # Return basic structure information
            return {
                "nodes": [
                    "analyze_task", "check_registry", "delegate_task", 
                    "evaluate_output", "handle_failure", "spawn_agent", "return_output"
                ],
                "edges": [
                    ("analyze_task", "check_registry"),
                    ("check_registry", "delegate_task"),
                    ("check_registry", "spawn_agent"),
                    ("delegate_task", "evaluate_output"),
                    ("delegate_task", "handle_failure"),
                    ("evaluate_output", "return_output"),
                    ("evaluate_output", "handle_failure"),
                    ("handle_failure", "delegate_task"),
                    ("handle_failure", "spawn_agent"),
                    ("spawn_agent", "delegate_task")
                ],
                "graph_type": "LangGraph StateGraph",
                "visualization_available": True,
                "description": "Agent workflow visualization showing task flow from analysis to completion",
                "note": f"Using fallback visualization due to: {str(e)}"
            }
    
    def get_mermaid_diagram(self):
        """Generate a Mermaid diagram representation of the workflow"""
        mermaid = """
graph TD
    A[analyze_task] --> B{Task Analysis OK?}
    B -->|Yes| C[check_registry]
    B -->|No| END1[return_output - Error]
    
    C --> D{Agent Found?}
    D -->|Yes| E[delegate_task]
    D -->|No| F[spawn_agent]
    
    E --> G{Execution Success?}
    G -->|Yes| H[evaluate_output]
    G -->|No| I[handle_failure]
    
    H --> J{Output Acceptable?}
    J -->|Yes| END2[return_output - Success]
    J -->|No| I
    
    I --> K{Retry Strategy}
    K -->|Retry| E
    K -->|Spawn New Agent| F
    K -->|Give Up| END3[return_output - Partial]
    
    F --> E
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style E fill:#e8f5e8
    style H fill:#fff3e0
    style END2 fill:#e8f5e8
    style END1 fill:#ffebee
    style END3 fill:#fff8e1
        """
        return mermaid.strip()
    
    def print_workflow_summary(self):
        """Print a detailed summary of the workflow structure"""
        print("🔍 LangGraph Workflow Structure:")
        print("=" * 50)
        
        print("\n📋 Workflow Nodes:")
        nodes = [
            ("analyze_task", "Analyzes incoming task requirements"),
            ("check_registry", "Searches for suitable existing agents"),
            ("delegate_task", "Executes task with chosen agent"),
            ("evaluate_output", "Validates response quality"),
            ("handle_failure", "Manages retries and failure strategies"),
            ("spawn_agent", "Creates new specialized agents"),
            ("return_output", "Prepares final response")
        ]
        
        for node, description in nodes:
            print(f"  🔸 {node}: {description}")
        
        print("\n🔀 Workflow Flow:")
        flow_steps = [
            "1. Task Analysis → Understand requirements",
            "2. Registry Check → Find suitable agents",
            "3. Agent Selection → Choose or create agent",
            "4. Task Delegation → Execute with agent",
            "5. Output Evaluation → Validate quality",
            "6. Failure Handling → Retry or escalate",
            "7. Final Response → Return results"
        ]
        
        for step in flow_steps:
            print(f"  {step}")
        
        print("\n🔄 Decision Points:")
        decisions = [
            "• Agent Found? → Delegate vs Spawn",
            "• Execution Success? → Evaluate vs Retry",
            "• Output Quality? → Return vs Improve",
            "• Retry Strategy? → Same Agent vs New Agent vs Give Up"
        ]
        
        for decision in decisions:
            print(f"  {decision}")
        
        print("\n📊 Current Registry Status:")
        agents = self.registry.get_available_agents()
        print(f"  Available Agents: {len(agents)}")
        for agent in agents:
            print(f"    🤖 {agent.name}: {agent.capabilities}")
    
    def get_execution_stats(self):
        """Get statistics about the workflow execution capabilities"""
        return {
            "total_nodes": 7,
            "decision_points": 4,
            "max_retries_per_agent": 3,
            "max_agents_spawnable": 3,
            "recursion_limit": 25,
            "available_agents": len(self.registry.get_available_agents()),
            "agent_types": [agent.name for agent in self.registry.get_available_agents()]
        }
    
    def _initialize_agents(self):
        """Initialize registry with specified agents"""
        # Available agent templates
        agent_templates = {
            "math_agent": {
                "name": "math_agent",
                "type": "math",
                "capabilities": ["calculation", "arithmetic", "algebra", "statistics"],
                "description": "Specialized agent for mathematical calculations and problem solving",
                "config": {"temperature": 0.1}
            },
            "fun_fact_agent": {
                "name": "fun_fact_agent",
                "type": "fun_fact",
                "capabilities": ["true_false_questions", "yes_no_questions", "historical_facts", "general_knowledge", "trivia"],
                "description": "Specialized agent for answering true/false questions, yes/no questions, and sharing fun facts about history, science, and general knowledge",
                "config": {"temperature": 0.3}
            },
            "research_agent": {
                "name": "research_agent",
                "type": "research",
                "capabilities": ["research", "analysis", "information_gathering", "web_search"],
                "description": "Specialized agent for research and information gathering tasks",
                "config": {"temperature": 0.2}
            },
            "writing_agent": {
                "name": "writing_agent",
                "type": "writing",
                "capabilities": ["writing", "editing", "creative_writing", "documentation"],
                "description": "Specialized agent for writing and editing tasks",
                "config": {"temperature": 0.5}
            },
            "code_agent": {
                "name": "code_agent",
                "type": "code",
                "capabilities": ["coding", "programming", "debugging", "code_review"],
                "description": "Specialized agent for programming and code-related tasks",
                "config": {"temperature": 0.1}
            },
            "planning_agent": {
                "name": "planning_agent",
                "type": "planning",
                "capabilities": ["planning", "strategy", "project_management", "task_breakdown"],
                "description": "Specialized agent for planning and strategy tasks",
                "config": {"temperature": 0.3}
            }
        }
        
        # Initialize only the specified agents
        initialized_count = 0
        for agent_name in self.initial_agents:
            if agent_name in agent_templates:
                template = agent_templates[agent_name]
                try:
                    agent = self.factory.create_agent(template)
                    self.registry.register_agent(agent)
                    initialized_count += 1
                    logger.info(f"✅ Initialized {agent_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {agent_name}: {e}")
            else:
                logger.warning(f"⚠️ Unknown agent template: {agent_name}")
                logger.info(f"Available templates: {list(agent_templates.keys())}")
        
        logger.info(f"Initialized {initialized_count}/{len(self.initial_agents)} requested agents")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow with recursion limits"""
        workflow = StateGraph(AgentSystemState)
        
        # Add nodes
        workflow.add_node("analyze_task", self.analyze_task)
        workflow.add_node("check_registry", self.check_registry)
        workflow.add_node("delegate_task", self.delegate_task)
        workflow.add_node("evaluate_output", self.evaluate_output)
        workflow.add_node("handle_failure", self.handle_failure)
        workflow.add_node("spawn_agent", self.spawn_agent)
        workflow.add_node("return_output", self.return_output)
        
        # Define the workflow
        workflow.set_entry_point("analyze_task")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_task",
            self._should_continue_to_registry,
            {
                "continue": "check_registry",
                "error": "return_output"
            }
        )
        
        workflow.add_conditional_edges(
            "check_registry", 
            self._agent_selection_logic,
            {
                "delegate": "delegate_task",
                "spawn": "spawn_agent",
                "error": "return_output"
            }
        )
        
        workflow.add_conditional_edges(
            "delegate_task",
            self._delegation_result,
            {
                "evaluate": "evaluate_output",
                "retry": "handle_failure",
                "error": "return_output"
            }
        )
        
        workflow.add_conditional_edges(
            "evaluate_output",
            self._evaluation_result,
            {
                "success": "return_output",
                "retry": "handle_failure",
                "spawn": "spawn_agent"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_failure",
            self._failure_strategy,
            {
                "retry": "delegate_task",
                "spawn": "spawn_agent", 
                "give_up": "return_output"
            }
        )
        
        workflow.add_edge("spawn_agent", "delegate_task")
        workflow.add_edge("return_output", END)
        
        return workflow.compile()
    
    # Node implementations with enhanced logging and limits
    async def analyze_task(self, state: AgentSystemState) -> AgentSystemState:
        """Analyze the incoming task"""
        try:
            logger.info("🧠 Analyzing task...")
            analysis = await self.analyzer.analyze_task(
                state["task_input"], 
                state["task_context"]
            )
            
            state["task_analysis"] = analysis
            state["capabilities_required"] = analysis["capabilities_required"]
            state["task_type"] = analysis["task_type"]
            
            logger.info(f"📋 Task type: {analysis['task_type']} (confidence: {analysis.get('confidence', 0):.2f})")
            logger.info(f"🔧 Required capabilities: {analysis['capabilities_required']}")
            
        except Exception as e:
            logger.error(f"❌ Task analysis failed: {e}")
            state["error_message"] = f"Task analysis failed: {str(e)}"
            
        return state
    
    async def check_registry(self, state: AgentSystemState) -> AgentSystemState:
        """Check for available agents"""
        try:
            logger.info("🔍 Checking agent registry...")
            
            # Find agents with required capabilities
            suitable_agents = []
            for capability in state["capabilities_required"]:
                agents = self.registry.find_agents_by_capability(capability)
                suitable_agents.extend(agents)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_agents = []
            for agent in suitable_agents:
                if agent.name not in seen:
                    unique_agents.append(agent)
                    seen.add(agent.name)
            
            state["available_agents"] = unique_agents
            
            if unique_agents:
                # Choose the best agent (first match for now)
                state["chosen_agent"] = unique_agents[0]
                logger.info(f"🎯 Selected agent: {unique_agents[0].name}")
                logger.info(f"🔧 Agent capabilities: {unique_agents[0].capabilities}")
                logger.info(f"📝 Agent description: {unique_agents[0].description}")
            else:
                logger.info("❌ No suitable agents found")
                state["chosen_agent"] = None
                
                # If no agents found and creation is disabled, try to find the "best fit" agent
                if not state.get("allow_agent_creation", True):
                    logger.info("🔍 Agent creation disabled, looking for best fit among existing agents...")
                    best_agent = self._find_best_fit_agent(state)
                    if best_agent:
                        state["chosen_agent"] = best_agent
                        logger.info(f"🎯 Selected best fit agent: {best_agent.name}")
                        logger.info(f"🔧 Agent capabilities: {best_agent.capabilities}")
                        logger.info(f"📝 Agent description: {best_agent.description}")
                
        except Exception as e:
            logger.error(f"❌ Registry check failed: {e}")
            state["error_message"] = f"Registry check failed: {str(e)}"
            
        return state
    
    async def delegate_task(self, state: AgentSystemState) -> AgentSystemState:
        """Delegate task to chosen agent"""
        try:
            if state["chosen_agent"]:
                # Increment delegation attempts for current agent
                current_agent_name = state["chosen_agent"].name
                agent_attempts = state.get("agent_attempts", {})
                agent_attempts[current_agent_name] = agent_attempts.get(current_agent_name, 0) + 1
                state["agent_attempts"] = agent_attempts
                
                attempt_num = agent_attempts[current_agent_name]
                logger.info(f"📤 Delegating to {current_agent_name} (attempt {attempt_num}/3)...")
                
                # Prepare input for agent
                agent_input = {
                    "query": state["task_input"],
                    "context": state["task_context"],
                    "task_type": state["task_type"],
                    "attempt": attempt_num
                }
                
                # Execute agent with timeout protection
                try:
                    # 30 second timeout to prevent hanging
                    result = await asyncio.wait_for(
                        state["chosen_agent"].process(agent_input),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    logger.error(f"⏰ Agent {current_agent_name} timed out after 30 seconds")
                    result = {
                        "status": "error",
                        "error": "Agent execution timed out after 30 seconds",
                        "response": "Task execution timed out. Please try a simpler request."
                    }
                
                state["agent_output"] = result
                state["execution_success"] = result.get("status") == "success"
                
                if state["execution_success"]:
                    logger.info(f"✅ Agent execution completed successfully")
                    # Handle different response structures for preview
                    if "response" in result:
                        response_preview = result["response"][:100]
                    elif "data" in result and isinstance(result["data"], dict):
                        response_preview = result["data"].get("response", "")[:100]
                    else:
                        response_preview = str(result)[:100]
                    logger.info(f"📄 Response preview: {response_preview}...")
                else:
                    logger.warning(f"⚠️ Agent execution failed: {result.get('error', 'Unknown error')}")
                
            else:
                logger.error("❌ No agent available for delegation")
                state["execution_success"] = False
                state["error_message"] = "No agent available for delegation"
                
        except Exception as e:
            logger.error(f"❌ Delegation failed: {e}")
            state["execution_success"] = False
            state["error_message"] = f"Delegation failed: {str(e)}"
            
        return state
    
    async def evaluate_output(self, state: AgentSystemState) -> AgentSystemState:
        """Evaluate the output quality"""
        try:
            if state["agent_output"]:
                logger.info("🔍 Evaluating output quality...")
                
                evaluation = await self.validator.validate_response(
                    state["task_input"],
                    {"data": state["agent_output"]}
                )
                
                state["evaluation_result"] = evaluation
                state["output_acceptable"] = evaluation["is_valid"]
                state["review_notes"] = f"Confidence: {evaluation['confidence']:.2f}"
                
                if evaluation["issues"]:
                    state["review_notes"] += f" | Issues: {', '.join(evaluation['issues'])}"
                
                logger.info(f"📊 Output acceptable: {state['output_acceptable']} (confidence: {evaluation['confidence']:.2f})")
                
                if not state["output_acceptable"]:
                    logger.info(f"⚠️ Quality issues: {evaluation['issues']}")
                
            else:
                state["output_acceptable"] = False
                state["review_notes"] = "No output to evaluate"
                logger.warning("⚠️ No output to evaluate")
                
        except Exception as e:
            logger.error(f"❌ Evaluation failed: {e}")
            state["output_acceptable"] = False
            state["error_message"] = f"Evaluation failed: {str(e)}"
            
        return state
    
    async def handle_failure(self, state: AgentSystemState) -> AgentSystemState:
        """Handle failures and determine retry strategy"""
        try:
            logger.info("🔧 Handling failure...")
            
            state["retry_count"] = state.get("retry_count", 0) + 1
            current_agent = state.get("chosen_agent")
            
            if current_agent:
                agent_attempts = state.get("agent_attempts", {})
                current_attempts = agent_attempts.get(current_agent.name, 0)
                
                logger.info(f"🔄 Current agent ({current_agent.name}) attempts: {current_attempts}/3")
                logger.info(f"🔄 Total retry count: {state['retry_count']}/{state['max_retries']}")
            
        except Exception as e:
            logger.error(f"❌ Failure handling error: {e}")
            
        return state
    
    async def spawn_agent(self, state: AgentSystemState) -> AgentSystemState:
        """Create a new agent for the task with limits"""
        try:
            # Check if agent creation is allowed
            if not state.get("allow_agent_creation", True):
                logger.warning("🚫 Agent creation is disabled. Cannot create new agents.")
                state["error_message"] = "Agent creation disabled - using existing agents only"
                return state
            
            # Check spawn limits
            agents_created = state.get("agents_created", 0)
            max_agents = 3
            
            if agents_created >= max_agents:
                logger.warning(f"🚫 Agent creation limit reached ({max_agents}). Cannot create more agents.")
                state["error_message"] = f"Maximum agent creation limit ({max_agents}) reached"
                return state
            
            logger.info(f"🏭 Spawning new agent ({agents_created + 1}/{max_agents})...")
            
            # Create blueprint for new agent
            task_type = state.get("task_type", "general")
            agent_name = f"dynamic_{task_type}_agent_v{agents_created + 1}"
            
            blueprint = {
                "name": agent_name,
                "capabilities": state["capabilities_required"],
                "description": f"Dynamically created specialized agent for {task_type} tasks (version {agents_created + 1})",
                "task_specific": True,
                "creation_context": {
                    "original_task": state["task_input"][:100],
                    "required_capabilities": state["capabilities_required"],
                    "creation_reason": "Existing agents insufficient for task requirements"
                }
            }
            
            # Create and register new agent
            new_agent = self.factory.create_agent(blueprint)
            self.registry.register_agent(new_agent)
            
            state["chosen_agent"] = new_agent
            state["agents_created"] = agents_created + 1
            state["agent_created"] = True
            
            logger.info(f"✅ Created new agent: {new_agent.name}")
            logger.info(f"🔧 New agent capabilities: {new_agent.capabilities}")
            logger.info(f"📝 New agent description: {new_agent.description}")
            logger.info(f"📊 Total agents created this session: {state['agents_created']}")
            
        except Exception as e:
            logger.error(f"❌ Agent spawning failed: {e}")
            state["error_message"] = f"Agent spawning failed: {str(e)}"
            
        return state
    
    async def return_output(self, state: AgentSystemState) -> AgentSystemState:
        """Return final output"""
        try:
            logger.info("📋 Preparing final output...")
            
            if state["output_acceptable"] and state["agent_output"]:
                # Extract response from different agent response structures
                agent_output = state["agent_output"]
                
                # Handle different response structures:
                # 1. {"response": "..."}  - BaseAgent
                # 2. {"data": {"response": "..."}}  - DynamicAgent, MathAgent, etc.
                # 3. {"output": "..."}  - LangChain agent executor output
                
                if "response" in agent_output:
                    response = agent_output["response"]
                elif "data" in agent_output and isinstance(agent_output["data"], dict):
                    response = agent_output["data"].get("response", "No response in data")
                elif "output" in agent_output:
                    response = agent_output["output"]
                else:
                    # Fallback: convert entire output to string
                    response = str(agent_output)
                
                status = "success"
            elif state["error_message"]:
                response = f"Task failed: {state['error_message']}"
                status = "error"
            else:
                response = "Task completed but output quality was insufficient"
                status = "partial_success"
            
            state["final_response"] = {
                "status": status,
                "response": response,
                "agent_used": state["chosen_agent"].name if state["chosen_agent"] else "none",
                "was_agent_created": state.get("agent_created", False),
                "task_type": state.get("task_type", "unknown"),
                "retry_count": state.get("retry_count", 0),
                "review_notes": state.get("review_notes", ""),
                "agents_created_count": state.get("agents_created", 0),
                "agent_attempts": state.get("agent_attempts", {})
            }
            
            logger.info(f"🎉 Final output prepared: {status}")
            if state.get("agents_created", 0) > 0:
                logger.info(f"🏭 Total new agents created: {state['agents_created']}")
            
        except Exception as e:
            logger.error(f"❌ Output preparation failed: {e}")
            state["final_response"] = {
                "status": "error",
                "error": str(e),
                "agent_used": None,
                "was_agent_created": False
            }
            
        return state
    
    # Enhanced conditional logic functions
    def _should_continue_to_registry(self, state: AgentSystemState) -> str:
        """Determine if we should continue to registry check"""
        if state.get("error_message"):
            return "error"
        return "continue"
    
    def _agent_selection_logic(self, state: AgentSystemState) -> str:
        """Determine agent selection strategy"""
        if state.get("error_message"):
            return "error"
        elif state.get("chosen_agent"):
            return "delegate"
        else:
            # Check if agent creation is allowed
            if not state.get("allow_agent_creation", True):
                logger.warning("🚫 No suitable agent found and creation is disabled")
                return "error"
            
            # Check if we can still create agents
            agents_created = state.get("agents_created", 0)
            if agents_created < 3:
                return "spawn"
            else:
                return "error"
    
    def _delegation_result(self, state: AgentSystemState) -> str:
        """Determine next step after delegation"""
        if state.get("error_message"):
            return "error"
        elif state.get("execution_success"):
            return "evaluate"
        else:
            return "retry"
    
    def _evaluation_result(self, state: AgentSystemState) -> str:
        """Determine next step after evaluation"""
        if state.get("output_acceptable"):
            return "success"
        
        # Check current agent attempts
        current_agent = state.get("chosen_agent")
        if current_agent:
            agent_attempts = state.get("agent_attempts", {})
            current_attempts = agent_attempts.get(current_agent.name, 0)
            
            # Try current agent 3 times before spawning new one
            if current_attempts < 3:
                return "retry"
        
        # Check if we can spawn more agents (only if creation is allowed)
        if state.get("allow_agent_creation", True):
            agents_created = state.get("agents_created", 0)
            if agents_created < 3:
                return "spawn"
        
        # If can't create agents or reached limit, return what we have
        return "success"  # Give up and return what we have
    
    def _failure_strategy(self, state: AgentSystemState) -> str:
        """Determine failure handling strategy"""
        current_agent = state.get("chosen_agent")
        
        if current_agent:
            agent_attempts = state.get("agent_attempts", {})
            current_attempts = agent_attempts.get(current_agent.name, 0)
            
            # Try current agent up to 3 times
            if current_attempts < 3:
                return "retry"
        
        # Check if we can spawn more agents (only if creation is allowed)
        if state.get("allow_agent_creation", True):
            agents_created = state.get("agents_created", 0)
            if agents_created < 3:
                return "spawn"
        
        return "give_up"
    
    def _find_best_fit_agent(self, state: AgentSystemState) -> Optional[Any]:
        """Find the best fit agent when no exact matches are found and creation is disabled"""
        all_agents = self.registry.get_available_agents()
        if not all_agents:
            return None
        
        required_capabilities = state["capabilities_required"]
        task_type = state.get("task_type", "").lower()
        
        # Score agents based on capability overlap and task type match
        best_agent = None
        best_score = -1
        
        for agent in all_agents:
            score = 0
            agent_capabilities = getattr(agent, 'capabilities', [])
            
            # Score for capability overlap
            capability_overlap = len(set(required_capabilities) & set(agent_capabilities))
            score += capability_overlap * 2
            
            # Score for task type match (check if agent name contains task type)
            if task_type and task_type in agent.name.lower():
                score += 3
            
            # Score for agent description relevance
            description = getattr(agent, 'description', '').lower()
            for capability in required_capabilities:
                if capability.lower() in description:
                    score += 1
            
            logger.info(f"🔍 Agent {agent.name} score: {score} (capabilities: {agent_capabilities})")
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent:
            logger.info(f"🏆 Best fit agent: {best_agent.name} (score: {best_score})")
        
        return best_agent
    
    async def process_task(self, task_input: str, task_context: Dict[str, Any] = None, allow_agent_creation: bool = True) -> Dict[str, Any]:
        """Process a task through the workflow"""
        initial_state = AgentSystemState(
            task_input=task_input,
            task_context=task_context or {},
            task_analysis=None,
            capabilities_required=[],
            task_type="",
            available_agents=[],
            chosen_agent=None,
            agent_created=False,
            agent_output=None,
            execution_success=False,
            evaluation_result=None,
            output_acceptable=False,
            review_notes="",
            retry_count=0,
            max_retries=10,  # Increased to allow for proper retry logic
            spawn_attempted=False,
            correction_attempted=False,
            allow_agent_creation=allow_agent_creation,  # Add control parameter
            final_response=None,
            error_message=None,
            agents_created=0,  # Track number of agents created
            agent_attempts={}   # Track attempts per agent
        )
        
        try:
            logger.info("🚀 Starting LangGraph workflow execution...")
            if not allow_agent_creation:
                logger.info("🚫 Agent creation disabled - will use existing agents only")
            # Set recursion limit to prevent infinite loops
            final_state = await self.graph.ainvoke(initial_state, config={"recursion_limit": 25})
            logger.info("✅ LangGraph workflow completed successfully")
            return final_state["final_response"]
        except Exception as e:
            logger.error(f"❌ LangGraph workflow failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_used": None,
                "was_agent_created": False
            } 