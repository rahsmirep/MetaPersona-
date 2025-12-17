"""
MetaPersona Skills Example
Demonstrates the modular skills system.
"""
from pathlib import Path
from src.skills import SkillManager
from src.skills.builtin import CalculatorSkill, FileOpsSkill, WebSearchSkill

def main():
    print("=" * 60)
    print("MetaPersona Skills System Demo")
    print("=" * 60)
    
    # Initialize skill manager
    skill_manager = SkillManager()
    
    # Register built-in skills
    print("\n📦 Registering built-in skills...")
    skill_manager.registry.register(CalculatorSkill())
    skill_manager.registry.register(FileOpsSkill())
    skill_manager.registry.register(WebSearchSkill())
    
    # List available skills
    print("\n📋 Available Skills:")
    skills = skill_manager.list_available_skills()
    for skill in skills:
        print(f"  • {skill['name']} ({skill['category']}): {skill['description']}")
    
    # Example 1: Calculator skill
    print("\n" + "=" * 60)
    print("Example 1: Calculator Skill")
    print("=" * 60)
    
    result = skill_manager.execute_skill("calculator", expression="sqrt(16) + 2**3")
    if result.success:
        print(f"✓ Result: {result.data}")
        print(f"  Metadata: {result.metadata}")
    else:
        print(f"✗ Error: {result.error}")
    
    # Example 2: File operations skill
    print("\n" + "=" * 60)
    print("Example 2: File Operations Skill")
    print("=" * 60)
    
    test_file = Path("./data/test_skill.txt")
    
    # Write to file
    result = skill_manager.execute_skill(
        "file_ops",
        operation="write",
        path=str(test_file),
        content="Hello from MetaPersona Skills System!\nThis is a test file."
    )
    if result.success:
        print(f"✓ Write: {result.data}")
    
    # Read from file
    result = skill_manager.execute_skill(
        "file_ops",
        operation="read",
        path=str(test_file)
    )
    if result.success:
        print(f"✓ Read content:\n{result.data}")
    
    # Check if file exists
    result = skill_manager.execute_skill(
        "file_ops",
        operation="exists",
        path=str(test_file)
    )
    if result.success:
        print(f"✓ File exists: {result.data}")
    
    # Example 3: Web search skill
    print("\n" + "=" * 60)
    print("Example 3: Web Search Skill")
    print("=" * 60)
    
    result = skill_manager.execute_skill(
        "web_search",
        query="artificial intelligence",
        max_results=3
    )
    if result.success:
        print(f"✓ Found {len(result.data)} results:")
        for i, item in enumerate(result.data, 1):
            print(f"\n  {i}. {item['title']}")
            print(f"     {item['snippet'][:100]}...")
            print(f"     URL: {item['url']}")
    else:
        print(f"✗ Error: {result.error}")
    
    # Example 4: Skill chaining
    print("\n" + "=" * 60)
    print("Example 4: Skill Chaining")
    print("=" * 60)
    
    skill_chain = [
        {
            "skill": "calculator",
            "parameters": {"expression": "100 * 0.15"},
            "output_var": "tax_amount"
        },
        {
            "skill": "calculator",
            "parameters": {"expression": "100 + 15"},  # Would use $tax_amount if we had substitution
            "output_var": "total"
        },
        {
            "skill": "file_ops",
            "parameters": {
                "operation": "write",
                "path": "./data/calculation_result.txt",
                "content": "Calculation result: 115"
            }
        }
    ]
    
    print("Executing chain: Calculate tax → Calculate total → Save to file")
    results = skill_manager.chain_skills(skill_chain)
    
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"  Step {i}: {status} {result.data if result.success else result.error}")
    
    # Display skill information
    print("\n" + "=" * 60)
    print("Skill Information: calculator")
    print("=" * 60)
    
    info = skill_manager.get_skill_info("calculator")
    if info:
        print(f"Name: {info['name']}")
        print(f"Category: {info['category']}")
        print(f"Description: {info['description']}")
        print(f"Version: {info['version']}")
        print(f"\nParameters:")
        for param in info['parameters']:
            req = "(required)" if param['required'] else "(optional)"
            print(f"  • {param['name']} ({param['type']}) {req}")
            print(f"    {param['description']}")
        print(f"\nReturns: {info['returns']}")
    
    print("\n" + "=" * 60)
    print("Skills Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
