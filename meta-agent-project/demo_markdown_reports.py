#!/usr/bin/env python3
"""
Demonstration of the Meta Agent System's Markdown Report Generation

This script shows how the system automatically logs conversations and generates
comprehensive markdown reports with workflow execution details, metrics, and insights.
"""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController

def print_banner():
    """Print demo banner"""
    print("📊 Meta Agent Markdown Report Generation Demo")
    print("=" * 60)
    print("This demo will:")
    print("• Run several test conversations")
    print("• Generate a comprehensive markdown report")
    print("• Show real-time logging of workflow execution")
    print("• Demonstrate metrics and analytics")
    print("=" * 60)

async def run_test_conversations():
    """Run a series of test conversations to populate the log"""
    print("\n🔄 Running test conversations to populate logs...")
    
    # Initialize controller
    controller = MetaAgentController(use_full_supervisor=True)
    
    # Test conversations with varied complexity
    test_queries = [
        {
            "name": "Mathematical Problem",
            "query": "What's the derivative of x^3 + 2x^2 - 5x + 1?"
        },
        {
            "name": "Personal Reflection", 
            "query": "I'm struggling with work-life balance. Can you help me think through this?"
        },
        {
            "name": "Research Question",
            "query": "What are the main benefits and drawbacks of renewable energy?"
        },
        {
            "name": "Creative Task",
            "query": "Help me write a short story about a robot learning to paint"
        },
        {
            "name": "Technical Analysis",
            "query": "Explain how machine learning algorithms can be used in fraud detection"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n  {i}/5: {test['name']}")
        print(f"       Query: {test['query'][:50]}...")
        
        try:
            result = await controller.process_request(
                input_data={"query": test['query']}
            )
            results.append({
                "test_name": test['name'],
                "query": test['query'],
                "result": result
            })
            
            # Show brief result
            status = result.get('status', 'unknown')
            agent = result.get('agent_used', 'unknown')
            new_agent = result.get('was_agent_created', False)
            
            print(f"       Result: {status} | Agent: {agent} | New: {new_agent}")
            
        except Exception as e:
            print(f"       Error: {str(e)}")
            results.append({
                "test_name": test['name'],
                "query": test['query'],
                "error": str(e)
            })
    
    print(f"\n✅ Completed {len(results)} test conversations")
    return results

async def demonstrate_api_report_generation():
    """Demonstrate report generation via API"""
    print("\n🌐 Testing API-based report generation...")
    
    # Check if API server is running
    try:
        response = requests.get("http://127.0.0.1:8000/workflow/report", timeout=30)
        
        if response.status_code == 200:
            report_data = response.json()
            print("✅ API report generation successful!")
            print(f"   📄 Filename: {report_data['filename']}")
            print(f"   📊 Conversations logged: {report_data['conversations_logged']}")
            print(f"   💾 Report size: {report_data['report_size_bytes']} bytes")
            print(f"   🔗 Download URL: {report_data['download_url']}")
            
            # Show report location
            if 'path' in report_data:
                print(f"\n📁 Report saved to: {report_data['path']}")
                
                # Try to read first few lines of the report
                try:
                    with open(report_data['path'], 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:10]
                    
                    print("\n📖 Report preview (first 10 lines):")
                    print("-" * 50)
                    for line in lines:
                        print(f"   {line.rstrip()}")
                    print("-" * 50)
                    
                except Exception as e:
                    print(f"   ⚠️  Could not preview report: {e}")
            
            return report_data
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   💡 Make sure to start the server with:")
        print("      uvicorn api.main:app --host 127.0.0.1 --port 8000")
        return None
    except Exception as e:
        print(f"❌ API request error: {e}")
        return None

def show_local_stats():
    """Show local system statistics"""
    print("\n📈 Local System Statistics:")
    
    try:
        controller = MetaAgentController(use_full_supervisor=True)
        
        if hasattr(controller.supervisor, 'supervisor_graph'):
            stats = controller.supervisor.supervisor_graph.get_execution_stats()
            
            print("   System Configuration:")
            for key, value in stats.items():
                print(f"     {key}: {value}")
                
            print("\n   Workflow Capabilities:")
            print(f"     • {stats['total_nodes']} workflow nodes")
            print(f"     • {stats['decision_points']} decision points")
            print(f"     • {stats['available_agents']} available agents")
            print(f"     • Up to {stats['max_retries_per_agent']} retries per agent")
            print(f"     • Maximum {stats['recursion_limit']} recursion depth")
            
        else:
            print("   ⚠️  Full supervisor not available")
            
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")

def show_usage_instructions():
    """Show comprehensive usage instructions"""
    print("\n📋 Markdown Report System Usage:")
    print("-" * 40)
    
    print("\n🚀 Getting Started:")
    print("   1. Start the FastAPI server:")
    print("      uvicorn api.main:app --host 127.0.0.1 --port 8000")
    print("   2. Run conversations through /agents/process endpoint")
    print("   3. Generate reports via /workflow/report endpoint")
    
    print("\n🔗 API Endpoints:")
    print("   • POST /agents/process - Process agent requests (logs automatically)")
    print("   • GET  /workflow/report - Generate markdown report")
    print("   • GET  /workflow/report/download/{filename} - Download report")
    print("   • GET  /workflow/dashboard - Interactive HTML dashboard")
    print("   • GET  /workflow/visualization - JSON workflow data")
    print("   • GET  /workflow/mermaid - Mermaid diagram code")
    
    print("\n📊 Report Contents:")
    print("   • Executive summary with key metrics")
    print("   • Complete conversation logs with timestamps")
    print("   • Workflow execution paths and decision points")
    print("   • Performance analytics and agent usage patterns")
    print("   • System insights and recommendations")
    print("   • Interactive Mermaid diagrams")
    
    print("\n💡 Usage Examples:")
    print("   # Generate report via curl")
    print("   curl http://127.0.0.1:8000/workflow/report")
    print("   ")
    print("   # Download specific report")
    print("   curl -O http://127.0.0.1:8000/workflow/report/download/meta_agent_report_20241201_143022.md")
    print("   ")
    print("   # View dashboard")
    print("   open http://127.0.0.1:8000/workflow/dashboard")

async def main():
    """Main demo function"""
    print_banner()
    
    # Run test conversations
    await run_test_conversations()
    
    # Show local stats
    show_local_stats()
    
    # Test API report generation
    report_result = await demonstrate_api_report_generation()
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n🎯 Demo Summary:")
    print("   ✅ Test conversations completed")
    print("   ✅ Local statistics displayed")
    
    if report_result:
        print("   ✅ API report generation successful")
        print(f"   📄 Generated: {report_result['filename']}")
    else:
        print("   ⚠️  API report generation skipped (server not running)")
    
    print("\n🔮 Next Steps:")
    print("   • Start the FastAPI server if not running")
    print("   • Process more conversations through the API")
    print("   • Generate and download comprehensive reports")
    print("   • Explore the interactive dashboard")
    print("   • Use reports for system analysis and optimization")

if __name__ == "__main__":
    asyncio.run(main()) 