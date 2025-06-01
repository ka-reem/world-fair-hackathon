#!/usr/bin/env python3
"""
Meta Agent Main Controller with MongoDB Integration
Central control point for the meta-agent system with MongoDB storage
"""

import sys
import os
import asyncio
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_agent.controller import MetaAgentController
from meta_agent.registry import AgentRegistry
from config.llm_config import LLAMA_MODELS

# MongoDB imports
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    print("⚠️ MongoDB not available. Install with: pip install pymongo")
    MONGODB_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaAgentMainController:
    """Main controller for the meta-agent system with MongoDB integration"""
    
    def __init__(self, model_name: str = None, mongo_uri: str = "mongodb://localhost:27017", 
                 db_name: str = "meta_agent_db", allow_agent_creation: bool = True, initial_agents: List[str] = None):
        self.model_name = model_name or "tinyllama"
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.allow_agent_creation = allow_agent_creation
        self.initial_agents = initial_agents if initial_agents is not None else ["fun_fact_agent"]
        
        # Initialize Meta Agent Controller
        self.controller = MetaAgentController(
            model_name=self.model_name, 
            use_full_supervisor=True, 
            enable_logging=True,
            allow_agent_creation=allow_agent_creation,
            initial_agents=self.initial_agents
        )
        
        # Initialize MongoDB if available
        self.db = None
        self.mongo_client = None
        if MONGODB_AVAILABLE:
            self._connect_mongodb()
        
        logger.info(f"🚀 Meta Agent Main Controller initialized with model: {self.model_name}")
        logger.info(f"🏭 Agent creation: {'✅ Enabled' if allow_agent_creation else '🚫 Disabled'}")
        logger.info(f"🤖 Initial agents: {self.initial_agents}")
    
    def _connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[self.db_name]
            
            # Create collections if they don't exist
            self.conversations_collection = self.db.conversations
            self.reports_collection = self.db.reports
            self.agents_collection = self.db.agents
            
            # Create indexes for better performance
            self.conversations_collection.create_index("timestamp")
            self.conversations_collection.create_index("agent_used")
            self.reports_collection.create_index("generated_at")
            
            logger.info(f"✅ Connected to MongoDB: {self.db_name}")
            return True
        except ConnectionFailure:
            logger.warning(f"⚠️ Could not connect to MongoDB at {self.mongo_uri}")
            logger.info("📝 Will use local file storage instead")
            return False
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            return False
    
    async def process_task(self, task: str, context: Dict[str, Any] = None, verbose: bool = True, 
                          allow_agent_creation: Optional[bool] = None) -> Dict[str, Any]:
        """Process a task through the meta-agent system with detailed output"""
        if verbose:
            creation_setting = allow_agent_creation if allow_agent_creation is not None else self.allow_agent_creation
            print(f"\n🔄 Processing Task: {task}")
            print("=" * 80)
            print(f"🤖 Model: {self.model_name}")
            print(f"📊 MongoDB: {'✅ Connected' if self.db else '❌ Not connected'}")
            print(f"🏭 Agent Creation: {'✅ Enabled' if creation_setting else '🚫 Disabled'}")
            print("-" * 80)
        
        # Process with meta-agent controller
        result = await self.controller.process_request(
            input_data={"query": task, "context": context or {}},
            allow_agent_creation=allow_agent_creation
        )
        
        if verbose:
            self._display_result(result)
        
        # Store conversation in MongoDB
        if self.db:
            await self._store_conversation(task, result, context)
        
        return result
    
    def _display_result(self, result: Dict[str, Any]):
        """Display the result in a nice format"""
        print("\n📋 WORKFLOW RESULTS:")
        print("-" * 80)
        
        status = result.get('status', 'unknown')
        status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"{status_emoji} Status: {status.upper()}")
        
        agent_used = result.get('agent_used', 'Unknown')
        print(f"🤖 Agent Used: {agent_used}")
        
        was_created = result.get('was_agent_created', False)
        creation_emoji = "🆕" if was_created else "♻️"
        print(f"{creation_emoji} Agent: {'Newly Created' if was_created else 'Existing'}")
        
        task_type = result.get('task_type', 'unknown')
        print(f"📋 Task Type: {task_type}")
        
        retry_count = result.get('retry_count', 0)
        if retry_count > 0:
            print(f"🔄 Retries: {retry_count}")
        
        execution_time = result.get('execution_time')
        if execution_time:
            print(f"⏱️ Execution Time: {execution_time:.2f}s")
        
        print("\n💬 AGENT RESPONSE:")
        print("-" * 80)
        response = result.get('response', 'No response available')
        print(response)
        
        review_notes = result.get('review_notes')
        if review_notes:
            print(f"\n📝 Review Notes: {review_notes}")
        
        print("-" * 80)
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query through the meta-agent system and store in MongoDB"""
        logger.info(f"🔄 Processing query: {query[:100]}...")
        
        # Process with meta-agent controller
        result = await self.controller.process_request(
            input_data={"query": query, "context": context or {}}
        )
        
        # Store conversation in MongoDB
        if self.db:
            await self._store_conversation(query, result, context)
        
        return result
    
    async def _store_conversation(self, query: str, result: Dict[str, Any], context: Dict[str, Any] = None):
        """Store conversation data in MongoDB"""
        try:
            conversation_doc = {
                "timestamp": datetime.utcnow(),
                "query": query,
                "context": context or {},
                "agent_used": result.get("agent_used"),
                "status": result.get("status"),
                "response": result.get("response"),
                "was_agent_created": result.get("was_agent_created", False),
                "task_type": result.get("task_type"),
                "retry_count": result.get("retry_count", 0),
                "review_notes": result.get("review_notes"),
                "execution_time": result.get("execution_time"),
                "model_used": self.model_name
            }
            
            self.conversations_collection.insert_one(conversation_doc)
            logger.info("💾 Conversation stored in MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Failed to store conversation in MongoDB: {e}")
    
    def generate_and_store_report(self) -> str:
        """Generate markdown report and store in both MongoDB and local files"""
        logger.info("📝 Generating comprehensive report...")
        
        # Generate local markdown report
        report_path = self.controller.generate_markdown_report()
        
        # Store report in MongoDB if available
        if self.db:
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                report_doc = {
                    "generated_at": datetime.utcnow(),
                    "report_path": report_path,
                    "content": report_content,
                    "summary": self.controller.get_conversation_summary(),
                    "model_used": self.model_name,
                    "total_conversations": len(self.controller.conversation_log)
                }
                
                self.reports_collection.insert_one(report_doc)
                logger.info("💾 Report stored in MongoDB")
                
            except Exception as e:
                logger.error(f"❌ Failed to store report in MongoDB: {e}")
        
        return report_path
    
    def get_conversation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history from MongoDB"""
        if not self.db:
            logger.warning("⚠️ MongoDB not available, returning local conversation log")
            return self.controller.conversation_log[-limit:]
        
        try:
            conversations = list(
                self.conversations_collection
                .find()
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string for JSON serialization
            for conv in conversations:
                conv['_id'] = str(conv['_id'])
                if 'timestamp' in conv:
                    conv['timestamp'] = conv['timestamp'].isoformat()
            
            return conversations
        except Exception as e:
            logger.error(f"❌ Failed to get conversation history: {e}")
            return []
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics from MongoDB"""
        if not self.db:
            logger.warning("⚠️ MongoDB not available, using local analytics")
            return self.controller.get_conversation_summary()
        
        try:
            # Agent usage statistics
            agent_usage = list(
                self.conversations_collection.aggregate([
                    {"$group": {"_id": "$agent_used", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ])
            )
            
            # Success rate
            total_conversations = self.conversations_collection.count_documents({})
            successful_conversations = self.conversations_collection.count_documents({"status": "success"})
            success_rate = (successful_conversations / total_conversations * 100) if total_conversations > 0 else 0
            
            # Task type distribution
            task_types = list(
                self.conversations_collection.aggregate([
                    {"$group": {"_id": "$task_type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ])
            )
            
            return {
                "total_conversations": total_conversations,
                "success_rate": success_rate,
                "agent_usage": agent_usage,
                "task_types": task_types,
                "new_agents_created": self.conversations_collection.count_documents({"was_agent_created": True})
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get analytics: {e}")
            return {}
    
    def export_data(self, format: str = "json") -> str:
        """Export all conversation data"""
        if format == "json":
            if self.db:
                # Export from MongoDB
                conversations = list(self.conversations_collection.find({}, {"_id": 0}))
                # Convert datetime objects to strings
                for conv in conversations:
                    if 'timestamp' in conv:
                        conv['timestamp'] = conv['timestamp'].isoformat()
                
                export_path = f"exports/mongodb_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                os.makedirs("exports", exist_ok=True)
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(conversations, f, indent=2, ensure_ascii=False)
                
                logger.info(f"📤 Data exported to: {export_path}")
                return export_path
            else:
                # Use controller's export
                return self.controller.export_conversation_log()
    
    def close(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("🔌 MongoDB connection closed")

# Interactive Functions
async def run_single_task(task: str, model: str = None, allow_agent_creation: bool = True, initial_agents: List[str] = None):
    """Run a single task and show the full workflow"""
    print("🚀 Meta Agent Task Processor")
    print("=" * 80)
    
    # Initialize main controller
    main_controller = MetaAgentMainController(
        model_name=model, 
        allow_agent_creation=allow_agent_creation,
        initial_agents=initial_agents
    )
    
    try:
        # Process the task
        result = await main_controller.process_task(task)
        
        # Show summary
        print("\n📊 TASK SUMMARY:")
        print("-" * 80)
        summary = main_controller.controller.get_conversation_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Generate report if successful
        if result.get('status') == 'success':
            print("\n📝 Generating Report...")
            report_path = main_controller.generate_and_store_report()
            print(f"✅ Report saved: {report_path}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing task: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
    
    finally:
        main_controller.close()

async def run_interactive_mode(model: str = None, allow_agent_creation: bool = True, initial_agents: List[str] = None):
    """Run in interactive mode where user can enter multiple tasks"""
    print("🚀 Meta Agent Interactive Mode")
    print("=" * 80)
    print("Enter tasks one by one. Type 'quit', 'exit', or 'done' to finish.")
    print("Type 'report' to generate a markdown report.")
    print("Type 'summary' to see conversation statistics.")
    print("Type 'toggle-creation' to enable/disable agent creation.")
    print("Type 'help' to see available commands.")
    print("Type 'status' to see current agent configuration.")
    print("-" * 80)
    
    # Initialize main controller
    main_controller = MetaAgentMainController(
        model_name=model, 
        allow_agent_creation=allow_agent_creation,
        initial_agents=initial_agents
    )
    current_creation_setting = allow_agent_creation
    
    try:
        task_count = 0
        
        while True:
            # Show current settings
            creation_status = "✅ Enabled" if current_creation_setting else "🚫 Disabled"
            
            # Get user input
            try:
                task = input(f"\n[Task #{task_count + 1}] [Agent Creation: {creation_status}] Enter your task: ").strip()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            
            # Check for exit commands
            if task.lower() in ['quit', 'exit', 'done', 'q']:
                print("👋 Goodbye!")
                break
            
            # Handle special commands
            if task.lower() == 'report':
                print("\n📝 Generating Report...")
                report_path = main_controller.generate_and_store_report()
                print(f"✅ Report saved: {report_path}")
                continue
            
            if task.lower() == 'summary':
                print("\n📊 Current Session Summary:")
                print("-" * 50)
                summary = main_controller.controller.get_conversation_summary()
                for key, value in summary.items():
                    print(f"  {key}: {value}")
                continue
            
            if task.lower() in ['toggle-creation', 'toggle']:
                current_creation_setting = not current_creation_setting
                status = "✅ Enabled" if current_creation_setting else "🚫 Disabled"
                print(f"🔄 Agent creation {status}")
                continue
            
            if task.lower() == 'help':
                print("\n📖 Available Commands:")
                print("-" * 50)
                print("  report         - Generate markdown report")
                print("  summary        - Show conversation statistics")
                print("  toggle-creation - Enable/disable agent creation")
                print("  status         - Show current agent configuration")
                print("  help           - Show this help message")
                print("  quit/exit/done - Exit interactive mode")
                print("\n📖 Available Agent Types:")
                print("  fun_fact_agent  - True/false questions and fun facts")
                print("  math_agent      - Mathematical calculations")
                print("  research_agent  - Research and information gathering")
                print("  writing_agent   - Writing and editing tasks")
                print("  code_agent      - Programming and debugging")
                print("  planning_agent  - Planning and strategy")
                continue
            
            if task.lower() == 'status':
                print("\n📊 Current Configuration:")
                print("-" * 50)
                print(f"  Model: {main_controller.model_name}")
                print(f"  Agent Creation: {'✅ Enabled' if current_creation_setting else '🚫 Disabled'}")
                print(f"  Initial Agents: {main_controller.initial_agents}")
                
                # Show currently loaded agents
                try:
                    stats = main_controller.controller.get_supervisor_stats()
                    available_agents = stats.get('agent_types', [])
                    print(f"  Loaded Agents: {available_agents}")
                    print(f"  Total Agents: {len(available_agents)}")
                except:
                    print("  Loaded Agents: Unable to retrieve")
                continue
            
            # Skip empty tasks
            if not task:
                print("⚠️ Please enter a task.")
                continue
            
            # Process the task
            task_count += 1
            try:
                result = await main_controller.process_task(
                    task, 
                    allow_agent_creation=current_creation_setting
                )
                
                # Ask if user wants to continue
                print(f"\n✅ Task #{task_count} completed!")
                
            except Exception as e:
                print(f"❌ Error processing task #{task_count}: {e}")
        
        # Final summary
        if task_count > 0:
            print(f"\n🎉 Session Complete! Processed {task_count} tasks.")
            
            # Generate final report
            print("📝 Generating final report...")
            report_path = main_controller.generate_and_store_report()
            print(f"✅ Final report saved: {report_path}")
            
            # Show analytics
            analytics = main_controller.get_analytics()
            if analytics:
                print("\n📊 Session Analytics:")
                for key, value in analytics.items():
                    print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"❌ Interactive mode error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        main_controller.close()

# Demo and Testing Functions
async def run_demo():
    """Run a demo of the main controller with MongoDB integration"""
    print("🚀 Meta Agent Main Controller Demo with MongoDB")
    print("=" * 60)
    
    # Initialize main controller
    main_controller = MetaAgentMainController()
    
    # Test queries
    test_queries = [
        "What is 25 * 17?",
        "Help me plan a productive morning routine",
        "Explain the concept of machine learning in simple terms"
    ]
    
    print("\n🔄 Processing test queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = await main_controller.process_query(query)
        print(f"   Agent: {result.get('agent_used')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Response: {result.get('response', '')[:100]}...")
    
    # Show analytics
    print("\n📊 Analytics:")
    analytics = main_controller.get_analytics()
    for key, value in analytics.items():
        print(f"   {key}: {value}")
    
    # Generate report
    print("\n📝 Generating report...")
    report_path = main_controller.generate_and_store_report()
    print(f"   Report saved: {report_path}")
    
    # Show conversation history
    print("\n📚 Recent conversations:")
    history = main_controller.get_conversation_history(limit=3)
    for conv in history:
        timestamp = conv.get('timestamp', 'Unknown')
        query = conv.get('query', 'Unknown')[:50]
        agent = conv.get('agent_used', 'Unknown')
        print(f"   {timestamp}: {query}... (Agent: {agent})")
    
    # Export data
    print("\n📤 Exporting data...")
    export_path = main_controller.export_data()
    print(f"   Data exported: {export_path}")
    
    # Close connection
    main_controller.close()
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Meta Agent Task Processor with MongoDB Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --task "Calculate 15% tip on $45.50"
  python main.py --task "Help me write a professional email" --no-create-agents
  python main.py --interactive --allow-agent-creation
  python main.py --demo
        """
    )
    
    parser.add_argument(
        "--task", "-t", 
        type=str, 
        help="Single task to process"
    )
    
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true", 
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--demo", "-d", 
        action="store_true", 
        help="Run demo with predefined tasks"
    )
    
    parser.add_argument(
        "--model", "-m", 
        type=str, 
        default="tinyllama",
        help="Model to use (default: tinyllama)"
    )
    
    parser.add_argument(
        "--allow-agent-creation", 
        action="store_true", 
        default=True,
        help="Allow creation of new agents (default: enabled)"
    )
    
    parser.add_argument(
        "--no-create-agents", 
        action="store_true", 
        help="Disable creation of new agents (use existing agents only)"
    )
    
    parser.add_argument(
        "--initial-agents", 
        type=str, 
        nargs='+',
        default=["fun_fact_agent"],
        help="Initial agents to load (default: fun_fact_agent). Available: fun_fact_agent, math_agent, research_agent, writing_agent, code_agent, planning_agent"
    )
    
    args = parser.parse_args()
    
    # Determine agent creation setting
    if args.no_create_agents:
        allow_creation = False
    else:
        allow_creation = args.allow_agent_creation
    
    # Get initial agents list
    initial_agents = getattr(args, 'initial_agents', ["fun_fact_agent"])
    
    # Check if MongoDB is available
    if not MONGODB_AVAILABLE:
        print("⚠️ MongoDB not available. Install with:")
        print("   pip install pymongo")
        print("   brew install mongodb/brew/mongodb-community (on macOS)")
        print("   Or use Docker: docker run -d -p 27017:27017 mongo")
        print()
    
    # Run based on arguments
    if args.task:
        # Single task mode
        asyncio.run(run_single_task(args.task, args.model, allow_creation, initial_agents))
    elif args.interactive:
        # Interactive mode
        asyncio.run(run_interactive_mode(args.model, allow_creation, initial_agents))
    elif args.demo:
        # Demo mode
        asyncio.run(run_demo())
    else:
        # Default to interactive mode if no arguments
        print("No arguments provided. Starting interactive mode...")
        print("Use --help to see all options.")
        asyncio.run(run_interactive_mode(args.model, allow_creation, initial_agents)) 