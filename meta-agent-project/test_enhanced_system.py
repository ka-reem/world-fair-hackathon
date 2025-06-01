import sys
import os
import asyncio
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_functionality():
    """Test the enhanced agent system with full LangGraph workflow"""
    print("🧪 Testing Enhanced Meta Agent System with LangGraph...")
    print("=" * 80)
    
    try:
        # Initialize controller with full supervisor and logging enabled
        print("📋 Initializing enhanced controller with conversation logging...")
        controller = MetaAgentController(use_full_supervisor=True, enable_logging=True)
        
        # Display workflow visualization
        print("\n🔍 LangGraph Workflow Visualization:")
        print("-" * 50)
        
        if hasattr(controller.supervisor, 'supervisor_graph'):
            # Show workflow summary
            controller.supervisor.supervisor_graph.print_workflow_summary()
            
            # Show execution stats
            print("\n📈 Execution Statistics:")
            stats = controller.supervisor.supervisor_graph.get_execution_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # Show Mermaid diagram code
            print("\n🎨 Mermaid Diagram (copy to mermaid.live):")
            print("-" * 50)
            mermaid = controller.supervisor.supervisor_graph.get_mermaid_diagram()
            print(mermaid)
            print("-" * 50)
        
        # Get system stats
        print("\n📊 System stats:")
        stats = controller.get_supervisor_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Enhanced test cases
        test_cases = [
            {
                "name": "Complex Math Problem",
                "input": {"query": "Calculate the compound interest on $1000 at 5% annual rate for 3 years, compounded quarterly."},
                "expected_features": ["step-by-step", "formula", "final answer"]
            },
            {
                "name": "Deep Reflection",
                "input": {"query": "I've been feeling overwhelmed with work lately. I'm working 60+ hours a week and feel like I'm losing myself. Help me reflect on this situation and find some clarity."},
                "expected_features": ["empathy", "questions", "guidance"]
            },
            {
                "name": "Research Analysis",
                "input": {"query": "Analyze the potential impacts of artificial intelligence on the job market over the next 10 years. What should workers consider?"},
                "expected_features": ["analysis", "considerations", "insights"]
            },
            {
                "name": "Novel Task (Should Spawn Agent)",
                "input": {"query": "Help me create a meal plan for a week that's vegetarian, budget-friendly, and takes less than 30 minutes to prepare each meal."},
                "expected_features": ["new agent creation", "specialized response"]
            }
        ]
        
        # Run enhanced tests
        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 Enhanced Test {i}: {test['name']}")
            print(f"📝 Query: {test['input']['query'][:100]}...")
            print("🔄 Processing with full LangGraph workflow and automatic logging...")
            
            result = await controller.process_request(
                input_data=test['input']
            )
            
            print(f"✅ Status: {result.get('status')}")
            print(f"🤖 Agent: {result.get('agent_used')}")
            print(f"🏭 New Agent Created: {result.get('was_agent_created', False)}")
            print(f"🔄 Retry Count: {result.get('retry_count', 0)}")
            print(f"📋 Task Type: {result.get('task_type', 'unknown')}")
            
            response = result.get('response', '')
            print(f"📄 Response Preview: {response[:200]}...")
            
            if result.get('review_notes'):
                print(f"📝 Review Notes: {result.get('review_notes')}")
            
            # Show agent attempts breakdown if available
            if result.get('agent_attempts'):
                print(f"🎯 Agent Attempts: {result.get('agent_attempts')}")
            
            print("-" * 80)
        
        print("🎉 All enhanced tests completed!")
        
        # Show conversation summary
        print("\n📊 Conversation Summary:")
        summary = controller.get_conversation_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Generate markdown report directly from controller
        print("\n📝 Generating Markdown Report...")
        try:
            report_path = controller.generate_markdown_report()
            print(f"✅ Markdown report generated: {report_path}")
            
            # Show preview of the report
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
                print(f"\n📄 Report Preview (first 500 characters):")
                print("-" * 50)
                print(report_content[:500] + "...")
                print("-" * 50)
                
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
        
        # Export conversation log as JSON
        print("\n💾 Exporting Conversation Log as JSON...")
        try:
            json_path = controller.export_conversation_log()
            print(f"✅ Conversation log exported: {json_path}")
        except Exception as e:
            print(f"❌ JSON export failed: {e}")
        
        print("\n📈 Final Statistics:")
        final_stats = controller.get_supervisor_stats()
        print(f"  Total Agents: {final_stats.get('available_agents')}")
        print(f"  Supervisor Type: {final_stats.get('supervisor_type')}")
        
        # Final workflow state
        if hasattr(controller.supervisor, 'supervisor_graph'):
            print("\n🔄 Final Workflow State:")
            final_exec_stats = controller.supervisor.supervisor_graph.get_execution_stats()
            print(f"  Available Agents: {final_exec_stats['available_agents']}")
            print(f"  Agent Types: {', '.join(final_exec_stats['agent_types'])}")
        
        print("\n📁 Generated Files:")
        print(f"  • Markdown Report: {report_path if 'report_path' in locals() else 'Not generated'}")
        print(f"  • JSON Log: {json_path if 'json_path' in locals() else 'Not generated'}")
        print(f"  • Reports Directory: reports/")
        
        print("\n🌟 NEW FEATURE: Direct Markdown Reporting")
        print("  • No API server needed!")
        print("  • Automatic conversation logging during process_request()")
        print("  • Generate reports with controller.generate_markdown_report()")
        print("  • Export logs with controller.export_conversation_log()")
        
        print("\n🌐 Optional: Access visual dashboard with API:")
        print("  • Start server: uvicorn api.main:app --reload")
        print("  • Open: http://localhost:8000/workflow/dashboard")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_direct_reporting_only():
    """Test just the direct reporting functionality without running full tests"""
    print("📝 Testing Direct Markdown Reporting")
    print("=" * 50)
    
    try:
        # Initialize with logging
        controller = MetaAgentController(use_full_supervisor=True, enable_logging=True)
        
        # Run a few quick tests
        test_queries = [
            "What is 2 + 2?",
            "Help me plan my day",
            "Explain quantum computing"
        ]
        
        print("🔄 Running test conversations...")
        for i, query in enumerate(test_queries, 1):
            print(f"  {i}. {query}")
            result = await controller.process_request(input_data={"query": query})
            print(f"     → {result.get('agent_used')} ({result.get('status')})")
        
        # Generate report
        print("\n📝 Generating markdown report...")
        report_path = controller.generate_markdown_report()
        print(f"✅ Report saved to: {report_path}")
        
        # Show conversation summary
        summary = controller.get_conversation_summary()
        print(f"\n📊 Summary: {summary['total_conversations']} conversations, {summary['success_rate']:.1f}% success rate")
        
        # Show what's in the reports directory
        import os
        reports_dir = "reports"
        if os.path.exists(reports_dir):
            files = os.listdir(reports_dir)
            print(f"\n📁 Files in {reports_dir}/:")
            for file in files:
                print(f"  • {file}")
                
    except Exception as e:
        print(f"❌ Direct reporting test failed: {e}")

def demonstrate_visualization():
    """Demonstrate visualization capabilities without running full tests"""
    print("🎨 LangGraph Visualization Demo")
    print("=" * 50)
    
    try:
        controller = MetaAgentController(use_full_supervisor=True)
        
        if hasattr(controller.supervisor, 'supervisor_graph'):
            supervisor_graph = controller.supervisor.supervisor_graph
            
            print("📊 Workflow Structure:")
            supervisor_graph.print_workflow_summary()
            
            print("\n🔍 Graph Visualization Data:")
            viz_data = supervisor_graph.get_graph_visualization()
            print(f"  Nodes: {len(viz_data.get('nodes', []))}")
            print(f"  Edges: {len(viz_data.get('edges', []))}")
            
            print("\n📈 Execution Statistics:")
            stats = supervisor_graph.get_execution_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
        else:
            print("❌ Full supervisor not available")
            
    except Exception as e:
        print(f"❌ Visualization demo error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Enhanced Meta Agent System")
    parser.add_argument("--viz-only", action="store_true", help="Show only visualization demo")
    parser.add_argument("--report-only", action="store_true", help="Test only direct reporting functionality")
    args = parser.parse_args()
    
    if args.viz_only:
        demonstrate_visualization()
    elif args.report_only:
        asyncio.run(test_direct_reporting_only())
    else:
        asyncio.run(test_enhanced_functionality()) 