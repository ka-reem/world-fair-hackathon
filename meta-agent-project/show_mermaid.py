#!/usr/bin/env python3
"""
Quick script to output just the Mermaid diagram for copy-pasting
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController

def main():
    print("🎨 LangGraph Workflow - Mermaid Diagram")
    print("=" * 60)
    print("Copy the diagram below and paste it at: https://mermaid.live")
    print("=" * 60)
    
    try:
        controller = MetaAgentController(use_full_supervisor=True)
        
        if hasattr(controller.supervisor, 'supervisor_graph'):
            mermaid = controller.supervisor.supervisor_graph.get_mermaid_diagram()
            print("\n" + mermaid)
            
            print("\n" + "=" * 60)
            print("📋 Instructions:")
            print("1. Copy the diagram code above")
            print("2. Go to https://mermaid.live")
            print("3. Paste the code in the editor")
            print("4. View your interactive workflow diagram!")
            print("\n🌐 Or access the web dashboard at:")
            print("   http://localhost:8000/workflow/dashboard")
            
        else:
            print("❌ LangGraph supervisor not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 