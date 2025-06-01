#!/usr/bin/env python3
"""
Live Agent Execution Monitor
Shows real-time agent activity and workflow execution flow
"""
import asyncio
import sys
import os
import time
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController

class LiveWorkflowMonitor:
    def __init__(self):
        self.controller = MetaAgentController(use_full_supervisor=True)
        self.execution_history = []
        self.agent_usage_stats = {}
        
    def log_execution(self, query, result):
        """Log an execution for live monitoring"""
        timestamp = datetime.now()
        execution = {
            'timestamp': timestamp.strftime('%H:%M:%S'),
            'query_preview': query[:50] + "..." if len(query) > 50 else query,
            'agent_used': result.get('agent_used'),
            'was_new_agent': result.get('was_agent_created', False),
            'status': result.get('status'),
            'retry_count': result.get('retry_count', 0),
            'task_type': result.get('task_type'),
            'execution_path': self._extract_execution_path(result)
        }
        
        self.execution_history.append(execution)
        self._update_agent_stats(execution)
        return execution
        
    def _extract_execution_path(self, result):
        """Extract the workflow path taken"""
        path = ['analyze_task']
        
        # Determine path based on result
        if result.get('was_agent_created'):
            path.extend(['check_registry', 'spawn_agent', 'delegate_task'])
        else:
            path.extend(['check_registry', 'delegate_task'])
            
        if result.get('retry_count', 0) > 0:
            path.append('handle_failure')
            
        path.extend(['evaluate_output', 'return_output'])
        return ' → '.join(path)
        
    def _update_agent_stats(self, execution):
        """Update agent usage statistics"""
        agent = execution['agent_used']
        if agent not in self.agent_usage_stats:
            self.agent_usage_stats[agent] = {
                'total_uses': 0,
                'new_agent': execution['was_new_agent'],
                'success_rate': 0,
                'avg_retries': 0,
                'last_used': execution['timestamp']
            }
        
        stats = self.agent_usage_stats[agent]
        stats['total_uses'] += 1
        stats['last_used'] = execution['timestamp']
        
    def print_live_status(self):
        """Print current live workflow status"""
        print(f"\n{'='*80}")
        print(f"🔴 LIVE AGENT EXECUTION MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        # Current agent registry
        if hasattr(self.controller.supervisor, 'supervisor_graph'):
            stats = self.controller.supervisor.supervisor_graph.get_execution_stats()
            print(f"📊 Current Registry: {stats['available_agents']} agents")
            print(f"   Available: {', '.join(stats['agent_types'])}")
        
        # Recent executions
        print(f"\n🔄 Recent Executions (Last 5):")
        for exec_data in self.execution_history[-5:]:
            status_icon = "✅" if exec_data['status'] == 'success' else "❌"
            new_icon = "🆕" if exec_data['was_new_agent'] else "♻️"
            retry_info = f" (retry: {exec_data['retry_count']})" if exec_data['retry_count'] > 0 else ""
            
            print(f"  {exec_data['timestamp']} {status_icon} {new_icon} {exec_data['agent_used']}{retry_info}")
            print(f"    📝 {exec_data['query_preview']}")
            print(f"    🔀 {exec_data['execution_path']}")
        
        # Agent usage stats
        if self.agent_usage_stats:
            print(f"\n📈 Agent Usage Statistics:")
            for agent, stats in self.agent_usage_stats.items():
                type_icon = "🆕" if stats['new_agent'] else "🏠"
                print(f"  {type_icon} {agent}: {stats['total_uses']} uses, last: {stats['last_used']}")

async def run_live_scenarios():
    """Run scenarios while monitoring live execution"""
    monitor = LiveWorkflowMonitor()
    
    # Test scenarios that demonstrate different workflow paths
    test_scenarios = [
        {
            'name': 'Math Calculation',
            'query': 'Calculate 15% of 250 and add 75',
            'expected_path': 'Existing agent (math_agent)'
        },
        {
            'name': 'Personal Reflection',
            'query': 'Help me process feeling overwhelmed with my workload',
            'expected_path': 'Existing agent (journal_agent)'
        },
        {
            'name': 'Research Query',
            'query': 'What are the benefits of meditation for productivity?',
            'expected_path': 'Existing agent (research_agent)'
        },
        {
            'name': 'Novel Task - Cooking',
            'query': 'Create a healthy meal prep plan for busy weekdays',
            'expected_path': 'New agent creation (cooking/planning)'
        },
        {
            'name': 'Novel Task - Travel',
            'query': 'Plan a 3-day itinerary for visiting Tokyo on a budget',
            'expected_path': 'New agent creation (travel planning)'
        }
    ]
    
    print("🚀 Starting Live Agent Execution Monitor")
    print("This will show real-time workflow execution and agent usage")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'🔥' * 60}")
        print(f"🧪 LIVE SCENARIO {i}/5: {scenario['name']}")
        print(f"📝 Query: {scenario['query']}")
        print(f"🎯 Expected: {scenario['expected_path']}")
        print(f"{'🔥' * 60}")
        
        # Execute the scenario
        start_time = time.time()
        result = await monitor.controller.process_request({'query': scenario['query']})
        execution_time = time.time() - start_time
        
        # Log and display the execution
        execution = monitor.log_execution(scenario['query'], result)
        
        print(f"\n⚡ LIVE EXECUTION RESULT:")
        print(f"  🤖 Agent Used: {execution['agent_used']}")
        print(f"  🆕 New Agent: {'YES' if execution['was_new_agent'] else 'NO'}")
        print(f"  ⏱️ Execution Time: {execution_time:.2f}s")
        print(f"  🔄 Retries: {execution['retry_count']}")
        print(f"  🛤️ Workflow Path: {execution['execution_path']}")
        print(f"  📄 Response Preview: {result.get('response', '')[:100]}...")
        
        # Show live status after each execution
        monitor.print_live_status()
        
        # Brief pause between scenarios
        print(f"\n⏳ Waiting 2 seconds before next scenario...")
        await asyncio.sleep(2)
    
    # Final summary
    print(f"\n{'🎉' * 80}")
    print("🎉 LIVE MONITORING SESSION COMPLETE")
    print(f"{'🎉' * 80}")
    
    print(f"\n📊 SESSION SUMMARY:")
    print(f"  Total Executions: {len(monitor.execution_history)}")
    print(f"  New Agents Created: {sum(1 for e in monitor.execution_history if e['was_new_agent'])}")
    print(f"  Total Unique Agents Used: {len(monitor.agent_usage_stats)}")
    
    print(f"\n🌐 View live dashboard at: http://127.0.0.1:8000/workflow/dashboard")
    print(f"📊 API endpoint: http://127.0.0.1:8000/workflow/visualization")

def run_single_live_test():
    """Run a single test with live monitoring"""
    async def single_test():
        monitor = LiveWorkflowMonitor()
        
        query = input("🔥 Enter your query for live monitoring: ").strip()
        if not query:
            query = "What's the square root of 144 times 3?"
            
        print(f"\n{'⚡' * 60}")
        print(f"🔴 LIVE EXECUTION STARTING...")
        print(f"📝 Query: {query}")
        print(f"{'⚡' * 60}")
        
        start_time = time.time()
        result = await monitor.controller.process_request({'query': query})
        execution_time = time.time() - start_time
        
        execution = monitor.log_execution(query, result)
        
        print(f"\n⚡ LIVE EXECUTION COMPLETE:")
        print(f"  🤖 Agent: {execution['agent_used']}")
        print(f"  🆕 New Agent: {'YES' if execution['was_new_agent'] else 'NO'}")
        print(f"  ⏱️ Time: {execution_time:.2f}s")
        print(f"  🛤️ Path: {execution['execution_path']}")
        
        monitor.print_live_status()
        
    asyncio.run(single_test())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Agent Execution Monitor")
    parser.add_argument("--single", "-s", action="store_true", help="Run single live test")
    parser.add_argument("--scenarios", "-sc", action="store_true", help="Run all live scenarios")
    
    args = parser.parse_args()
    
    if args.single:
        run_single_live_test()
    elif args.scenarios:
        asyncio.run(run_live_scenarios())
    else:
        print("🔴 Live Agent Execution Monitor")
        print("Usage:")
        print("  python live_monitor.py --scenarios    # Run all live scenarios")
        print("  python live_monitor.py --single       # Run single live test")
        print("  python live_monitor.py --scenarios    # Show all scenarios with live monitoring") 