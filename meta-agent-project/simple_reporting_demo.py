#!/usr/bin/env python3
"""
Simple Demo: Direct Markdown Reporting
Shows how to generate markdown reports without needing an API server
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController

async def simple_demo():
    """Simple demonstration of direct markdown reporting"""
    print("🚀 Simple Markdown Reporting Demo")
    print("=" * 60)
    
    # Initialize controller with logging enabled
    print("1. Initializing Meta Agent Controller with logging...")
    controller = MetaAgentController(
        use_full_supervisor=True,
        enable_logging=True  # This enables automatic conversation logging
    )
    
    # Run some example conversations
    print("\n2. Running example conversations...")
    test_queries = [
        "What is 15 * 23?",
        "I'm feeling stressed about work. Help me reflect on this.",
        "Explain how photosynthesis works in simple terms",
        "Create a simple workout plan for beginners"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"   {i}. Processing: {query[:50]}...")
        result = await controller.process_request(input_data={"query": query})
        print(f"      → Agent: {result.get('agent_used')} | Status: {result.get('status')}")
    
    # Show conversation summary
    print("\n3. Conversation Summary:")
    summary = controller.get_conversation_summary()
    print(f"   • Total conversations: {summary['total_conversations']}")
    print(f"   • Success rate: {summary['success_rate']:.1f}%")
    print(f"   • New agents created: {summary['new_agents_created']}")
    print(f"   • Average execution time: {summary['average_execution_time']:.2f}s")
    
    # Generate markdown report
    print("\n4. Generating Markdown Report...")
    report_path = controller.generate_markdown_report()
    print(f"   ✅ Report saved to: {report_path}")
    
    # Export JSON log (optional)
    print("\n5. Exporting JSON conversation log...")
    json_path = controller.export_conversation_log()
    print(f"   ✅ JSON log saved to: {json_path}")
    
    # Show what was created
    print("\n6. Files Created:")
    import os
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        files = os.listdir(reports_dir)
        for file in sorted(files):
            file_path = os.path.join(reports_dir, file)
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size:,} bytes)")
    
    # Show a preview of the markdown report
    print("\n7. Markdown Report Preview:")
    print("-" * 60)
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Show first 1500 characters instead of 800
            preview = content[:1500]
            print(preview)
            if len(content) > 1500:
                print("\n... (report continues) ...")
    except Exception as e:
        print(f"Could not read report: {e}")
    
    print("-" * 60)
    print("\n🎉 Demo Complete!")
    print("\nKey Benefits:")
    print("• ✅ No API server required")
    print("• ✅ Automatic conversation logging")
    print("• ✅ Rich markdown reports with analytics")
    print("• ✅ JSON export for further analysis")
    print("• ✅ Mermaid diagrams for visualization")
    
    print(f"\nTo view your report:")
    print(f"• Open {report_path} in any markdown viewer")
    print(f"• Use VS Code, Obsidian, or any markdown editor")
    print(f"• View Mermaid diagrams at https://mermaid.live")

if __name__ == "__main__":
    asyncio.run(simple_demo()) 