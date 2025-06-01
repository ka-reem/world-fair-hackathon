#!/usr/bin/env python3
"""
Demo scenarios to showcase LangGraph workflow visualization
"""
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController

def print_scenario_header(scenario_num, title, description):
    """Print a formatted scenario header"""
    print(f"\n{'='*60}")
    print(f"🧪 SCENARIO {scenario_num}: {title}")
    print(f"{'='*60}")
    print(f"📝 {description}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 60)

async def scenario_1_existing_agent():
    """Test existing agent path (math_agent)"""
    print_scenario_header(1, "Existing Agent Path", 
                         "Testing math problem that should use existing math_agent")
    
    controller = MetaAgentController(use_full_supervisor=True)
    
    result = await controller.process_request({
        'query': 'What is 25% of 400, and then add 50 to that result?'
    })
    
    print(f"🎯 Result: {result.get('agent_used')} | New Agent: {result.get('was_agent_created', False)}")
    print(f"📄 Response: {result.get('response', '')[:100]}...")
    return result

async def scenario_2_spawn_new_agent():
    """Test new agent creation path"""
    print_scenario_header(2, "New Agent Creation", 
                         "Testing novel task that should spawn a new agent")
    
    controller = MetaAgentController(use_full_supervisor=True)
    
    result = await controller.process_request({
        'query': 'Create a 7-day workout plan for a beginner who wants to build muscle and has 45 minutes per day.'
    })
    
    print(f"🎯 Result: {result.get('agent_used')} | New Agent: {result.get('was_agent_created', False)}")
    print(f"📄 Response: {result.get('response', '')[:100]}...")
    return result

async def scenario_3_reflection_agent():
    """Test journal/reflection agent path"""
    print_scenario_header(3, "Reflection Agent Path", 
                         "Testing emotional/reflection query for journal_agent")
    
    controller = MetaAgentController(use_full_supervisor=True)
    
    result = await controller.process_request({
        'query': 'I feel overwhelmed with my studies and need help organizing my thoughts. What should I reflect on?'
    })
    
    print(f"🎯 Result: {result.get('agent_used')} | New Agent: {result.get('was_agent_created', False)}")
    print(f"📄 Response: {result.get('response', '')[:100]}...")
    return result

async def scenario_4_research_agent():
    """Test research agent path"""
    print_scenario_header(4, "Research Agent Path", 
                         "Testing research/analysis query for research_agent")
    
    controller = MetaAgentController(use_full_supervisor=True)
    
    result = await controller.process_request({
        'query': 'Analyze the pros and cons of remote work vs office work in the tech industry.'
    })
    
    print(f"🎯 Result: {result.get('agent_used')} | New Agent: {result.get('was_agent_created', False)}")
    print(f"📄 Response: {result.get('response', '')[:100]}...")
    return result

async def run_all_scenarios():
    """Run all demonstration scenarios"""
    print("🚀 LangGraph Workflow Demonstration")
    print("This will show different paths through the StateGraph workflow")
    print(f"{'='*60}")
    
    scenarios = [
        scenario_1_existing_agent,
        scenario_2_spawn_new_agent, 
        scenario_3_reflection_agent,
        scenario_4_research_agent
    ]
    
    results = []
    for scenario in scenarios:
        try:
            result = await scenario()
            results.append(result)
            print("✅ Scenario completed successfully")
        except Exception as e:
            print(f"❌ Scenario failed: {e}")
            results.append(None)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 DEMONSTRATION SUMMARY")
    print(f"{'='*60}")
    
    agent_usage = {}
    new_agents_created = 0
    
    for i, result in enumerate(results, 1):
        if result:
            agent = result.get('agent_used', 'unknown')
            agent_usage[agent] = agent_usage.get(agent, 0) + 1
            if result.get('was_agent_created', False):
                new_agents_created += 1
            print(f"Scenario {i}: {agent} ({'NEW' if result.get('was_agent_created') else 'EXISTING'})")
    
    print(f"\n📈 Workflow Statistics:")
    print(f"  • Total scenarios: {len(scenarios)}")
    print(f"  • New agents created: {new_agents_created}")
    print(f"  • Agent usage: {dict(agent_usage)}")
    
    print(f"\n🌐 View the workflow visualization at:")
    print(f"  • Dashboard: http://127.0.0.1:8000/workflow/dashboard")
    print(f"  • API Data: http://127.0.0.1:8000/workflow/visualization")

async def run_single_scenario(scenario_num):
    """Run a specific scenario by number"""
    scenarios = {
        1: scenario_1_existing_agent,
        2: scenario_2_spawn_new_agent,
        3: scenario_3_reflection_agent,
        4: scenario_4_research_agent
    }
    
    if scenario_num in scenarios:
        await scenarios[scenario_num]()
    else:
        print(f"❌ Invalid scenario number. Choose 1-{len(scenarios)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Demonstrate LangGraph Workflow Scenarios")
    parser.add_argument("--scenario", "-s", type=int, help="Run specific scenario (1-4)")
    parser.add_argument("--list", "-l", action="store_true", help="List available scenarios")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available scenarios:")
        print("  1: Existing Agent Path (math_agent)")
        print("  2: New Agent Creation (novel task)")
        print("  3: Reflection Agent Path (journal_agent)")
        print("  4: Research Agent Path (research_agent)")
        print("\nUsage:")
        print("  python demo_scenarios.py           # Run all scenarios")
        print("  python demo_scenarios.py -s 1      # Run scenario 1")
        print("  python demo_scenarios.py --list    # Show this help")
    elif args.scenario:
        asyncio.run(run_single_scenario(args.scenario))
    else:
        asyncio.run(run_all_scenarios()) 