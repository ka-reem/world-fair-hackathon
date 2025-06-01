#!/usr/bin/env python3
"""
LangGraph Workflow Visualization Tool
Demonstrates the meta-agent system's workflow visualization capabilities
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController


def print_banner():
    """Print a fancy banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                🤖 LangGraph Workflow Visualizer 🤖            ║
║                                                               ║
║        Meta-Agent System Workflow Analysis & Visualization   ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def save_mermaid_diagram(mermaid_code, filename="workflow_diagram.md"):
    """Save the Mermaid diagram to a file"""
    try:
        content = f"""# Meta Agent Workflow Diagram

This diagram shows the LangGraph-based workflow for the meta-agent system.

## Workflow Overview

The system uses LangGraph's StateGraph to orchestrate agent selection, task delegation, and quality validation.

## Mermaid Diagram

```mermaid
{mermaid_code}
```

## How to View

1. Copy the mermaid code above
2. Go to [mermaid.live](https://mermaid.live)
3. Paste the code to see the interactive diagram

## Workflow Description

- **analyze_task**: Analyzes incoming requests to understand requirements
- **check_registry**: Searches for suitable existing agents
- **delegate_task**: Executes the task with the chosen agent
- **evaluate_output**: Validates response quality and completeness
- **handle_failure**: Manages retries and escalation strategies
- **spawn_agent**: Creates new specialized agents when needed
- **return_output**: Prepares and returns the final response

## Decision Points

The workflow includes several decision points that determine the flow:

1. **Task Analysis OK?** - Ensures the task is properly understood
2. **Agent Found?** - Determines if existing agents can handle the task
3. **Execution Success?** - Checks if the agent completed the task
4. **Output Acceptable?** - Validates response quality
5. **Retry Strategy** - Decides how to handle failures

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(filename, 'w') as f:
            f.write(content)
        print(f"💾 Mermaid diagram saved to: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save diagram: {e}")
        return False


def save_visualization_data(viz_data, stats, filename="workflow_data.json"):
    """Save visualization data as JSON"""
    try:
        data = {
            "workflow_graph": viz_data,
            "execution_stats": stats,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "description": "LangGraph workflow visualization data",
                "system": "meta-agent-system"
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 Visualization data saved to: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save data: {e}")
        return False


async def demonstrate_workflow_execution():
    """Demonstrate the workflow with a sample task"""
    print("\n🚀 Workflow Execution Demonstration")
    print("=" * 60)
    
    try:
        controller = MetaAgentController(use_full_supervisor=True)
        
        # Sample task to trace through the workflow
        sample_task = {
            "query": "What are the key principles of effective time management for remote workers?"
        }
        
        print(f"📝 Sample Task: {sample_task['query']}")
        print("\n🔄 Executing workflow...")
        
        result = await controller.process_request(input_data=sample_task)
        
        print(f"\n✅ Workflow Completed!")
        print(f"📊 Status: {result.get('status')}")
        print(f"🤖 Agent Used: {result.get('agent_used')}")
        print(f"🔄 Retry Count: {result.get('retry_count', 0)}")
        print(f"🏭 New Agent Created: {result.get('was_agent_created', False)}")
        print(f"📋 Task Type: {result.get('task_type', 'unknown')}")
        
        if result.get('agent_attempts'):
            print(f"🎯 Agent Attempts Breakdown:")
            for agent, attempts in result.get('agent_attempts', {}).items():
                print(f"    {agent}: {attempts} attempts")
        
        response_preview = result.get('response', '')[:300]
        print(f"\n📄 Response Preview:")
        print(f"    {response_preview}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return None


def main():
    """Main visualization demonstration"""
    print_banner()
    
    try:
        print("🔧 Initializing Meta Agent Controller...")
        controller = MetaAgentController(use_full_supervisor=True)
        
        if not hasattr(controller.supervisor, 'supervisor_graph'):
            print("❌ Error: Full supervisor with LangGraph not available")
            print("   Make sure the controller is initialized with use_full_supervisor=True")
            return
        
        supervisor_graph = controller.supervisor.supervisor_graph
        
        # 1. Display workflow structure
        print("\n" + "="*80)
        supervisor_graph.print_workflow_summary()
        
        # 2. Show execution statistics
        print("\n📈 Detailed Execution Statistics:")
        print("-" * 50)
        stats = supervisor_graph.get_execution_stats()
        for key, value in stats.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")
        
        # 3. Generate and display Mermaid diagram
        print("\n🎨 Mermaid Workflow Diagram:")
        print("-" * 50)
        mermaid = supervisor_graph.get_mermaid_diagram()
        print(mermaid)
        
        # 4. Get graph visualization data
        print("\n🔍 Graph Structure Analysis:")
        print("-" * 50)
        viz_data = supervisor_graph.get_graph_visualization()
        if viz_data.get('visualization_available'):
            print(f"  Nodes: {len(viz_data.get('nodes', []))}")
            print(f"  Edges: {len(viz_data.get('edges', []))}")
            print(f"  Graph Type: {viz_data.get('graph_type')}")
            print(f"  Description: {viz_data.get('description')}")
            
            # Show nodes and edges
            print(f"\n  📋 Workflow Nodes:")
            for node in viz_data.get('nodes', []):
                print(f"    • {node}")
            
            print(f"\n  🔗 Workflow Edges:")
            for edge in viz_data.get('edges', []):
                print(f"    • {edge}")
        else:
            print(f"  ❌ Visualization Error: {viz_data.get('error')}")
        
        # 5. Save outputs
        print("\n💾 Saving Visualization Outputs:")
        print("-" * 50)
        save_mermaid_diagram(mermaid)
        save_visualization_data(viz_data, stats)
        
        # 6. Demonstrate workflow execution
        asyncio.run(demonstrate_workflow_execution())
        
        # 7. Show access instructions
        print("\n🌐 Interactive Visualization Access:")
        print("-" * 50)
        print("  1. Start the FastAPI server:")
        print("     uvicorn api.main:app --reload")
        print()
        print("  2. Access visualization endpoints:")
        print("     • Dashboard: http://localhost:8000/workflow/dashboard")
        print("     • JSON Data: http://localhost:8000/workflow/visualization")
        print("     • Mermaid: http://localhost:8000/workflow/mermaid")
        print()
        print("  3. For external visualization tools:")
        print("     • Copy mermaid code to: https://mermaid.live")
        print("     • Use saved files: workflow_diagram.md, workflow_data.json")
        
        print("\n✨ Visualization demonstration completed!")
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGraph Workflow Visualizer")
    parser.add_argument("--save", action="store_true", help="Save visualization files")
    parser.add_argument("--demo", action="store_true", help="Run workflow execution demo")
    
    args = parser.parse_args()
    
    if args.demo or args.save:
        # Run specific parts based on arguments
        main()
    else:
        # Run full demonstration
        main() 