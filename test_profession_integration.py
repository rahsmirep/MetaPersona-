"""
Test script for profession system integration
"""
from pathlib import Path
from src.question_router import QuestionRouter

# Test routing with profession keywords
router = QuestionRouter(Path("data/personas"))

print(f"📊 Loaded {len(router.profession_experts)} profession experts")
if router.profession_experts:
    for expert in router.profession_experts:
        print(f"   ✅ {expert['role']} - {expert['profession_name']}")
        print(f"      Keywords: {len(expert['keywords'])} terms")
print()

test_queries = [
    "What's the best way to backtest a trading strategy?",
    "Should I deploy this code to production now?",
    "How do I write a Python function?",
    "What are the risk management best practices for quantitative trading?",
]

print("=" * 80)
print("PROFESSION EXPERT ROUTING TEST")
print("=" * 80)

for query in test_queries:
    print(f"\n📝 Query: {query}")
    personas, analysis = router.route_question(query)
    
    print(f"   Primary Domain: {analysis.primary_domain}")
    print(f"   Confidence: {analysis.confidence:.0%}")
    print(f"   Selected Experts: {len(personas)}")
    
    for persona in personas:
        agent_type = persona.get('agent_type', 'domain_expert')
        if agent_type == 'profession_expert':
            print(f"   ✅ PROFESSION EXPERT: {persona['role']}")
        else:
            print(f"   • {persona.get('name', 'Unknown')} - {persona.get('role', 'Unknown')}")
    
    print()

print("=" * 80)
print("✅ Routing test complete!")
print("=" * 80)
