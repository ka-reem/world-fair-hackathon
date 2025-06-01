import sys
import os
import asyncio
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import using absolute imports
from meta_agent.controller import MetaAgentController

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test the basic agent system"""
    print("🧪 Testing Meta Agent System...")
    
    try:
        # Initialize controller (will auto-select best model)
        print("📋 Initializing controller...")
        controller = MetaAgentController()
        
        # Get system stats
        print("📊 System stats:")
        stats = controller.get_supervisor_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test cases
        test_cases = [
            {
                "name": "Math Problem",
                "input": {"query": "What is 15 * 23 + 7?"},
                "expected_agent": "math"
            },
            {
                "name": "Journal Entry", 
                "input": {"query": "I'm feeling stressed about work today. Help me reflect on this."},
                "expected_agent": "journal"
            },
            {
                "name": "General Question",
                "input": {"query": "Explain what photosynthesis is in simple terms."},
                "expected_agent": "dynamic"
            }
        ]
        
        # Run tests
        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test['name']}")
            print(f"📝 Query: {test['input']['query']}")
            
            result = await controller.process_request(
                input_data=test['input']
            )
            
            print(f"✅ Status: {result.get('status')}")
            print(f"🤖 Agent: {result.get('agent_used')}")
            print(f"📄 Response: {result.get('response', '')[:100]}...")
            
            if result.get('was_agent_created'):
                print("🏭 New agent was created!")
            
            print("-" * 50)
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality()) 