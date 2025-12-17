"""
Example: Quick Start with MetaPersona
This script demonstrates basic usage of MetaPersona as a library.
"""
import os
from src import AgentManager, MemoryLoop

# Set your LLM provider
os.environ['LLM_PROVIDER'] = 'openai'  # or 'anthropic', 'ollama'
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

def main():
    """Run a simple example interaction."""
    
    # Initialize agent
    print("🚀 Initializing MetaPersona...")
    agent_manager = AgentManager(data_dir="./data")
    
    try:
        agent = agent_manager.initialize_agent(user_id="demo_user")
        memory = MemoryLoop(data_dir="./data")
        
        print(f"✓ Agent initialized: {agent.profile.user_id}\n")
        
        # Example tasks
        tasks = [
            "Write a brief introduction about yourself",
            "How would you prioritize these tasks: urgent bug fix, code review, team meeting?",
            "Draft a professional email declining a meeting invitation"
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{'='*60}")
            print(f"Task {i}: {task}")
            print('='*60)
            
            # Process task
            response = agent.process_task(task)
            print(f"\nResponse:\n{response}\n")
            
            # Record interaction
            memory.record_interaction(task, response, tags=["demo"])
            agent.profile.interaction_count += 1
        
        # Save state
        agent_manager.save_agent_state(agent)
        
        # Show summary
        print("\n" + "="*60)
        print("📊 Session Summary")
        print("="*60)
        status = agent.get_agent_status()
        for key, value in status.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created .env file with your API key")
        print("2. Installed dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
