"""
Batch Safety Template Generator
Pre-generates safety rules for common professions to reduce API costs and improve onboarding speed.
"""
from src.profession import UniversalProfessionSystem
from src.llm_provider import get_llm_provider
from pathlib import Path
import time

# Top 100 common professions across major industries
COMMON_PROFESSIONS = [
    # Technology
    ("Software Engineer", "Technology"),
    ("Data Scientist", "Technology"),
    ("DevOps Engineer", "Technology"),
    ("Product Manager", "Technology"),
    ("UX Designer", "Technology"),
    ("Cybersecurity Analyst", "Technology"),
    ("Machine Learning Engineer", "Technology"),
    ("Cloud Architect", "Technology"),
    ("Mobile Developer", "Technology"),
    ("Full Stack Developer", "Technology"),
    
    # Healthcare
    ("Physician", "Healthcare"),
    ("Registered Nurse", "Healthcare"),
    ("Pharmacist", "Healthcare"),
    ("Physical Therapist", "Healthcare"),
    ("Medical Laboratory Technician", "Healthcare"),
    ("Radiologist", "Healthcare"),
    ("Surgeon", "Healthcare"),
    ("Dentist", "Healthcare"),
    ("Clinical Psychologist", "Healthcare"),
    ("Data Scientist", "Healthcare"),
    
    # Finance
    ("Financial Analyst", "Finance"),
    ("Investment Banker", "Finance"),
    ("Accountant", "Finance"),
    ("Financial Advisor", "Finance"),
    ("Quantitative Analyst", "Finance"),
    ("Risk Manager", "Finance"),
    ("Tax Consultant", "Finance"),
    ("Portfolio Manager", "Finance"),
    ("Compliance Officer", "Finance"),
    ("Auditor", "Finance"),
    
    # Legal
    ("Attorney", "Legal Services"),
    ("Paralegal", "Legal Services"),
    ("Corporate Lawyer", "Legal Services"),
    ("Legal Consultant", "Legal Services"),
    ("Patent Attorney", "Legal Services"),
    ("Compliance Lawyer", "Legal Services"),
    
    # Education
    ("Teacher", "Education"),
    ("Professor", "Education"),
    ("School Counselor", "Education"),
    ("Educational Administrator", "Education"),
    ("Instructional Designer", "Education"),
    
    # Engineering
    ("Civil Engineer", "Engineering"),
    ("Mechanical Engineer", "Engineering"),
    ("Electrical Engineer", "Engineering"),
    ("Chemical Engineer", "Engineering"),
    ("Aerospace Engineer", "Engineering"),
    ("Environmental Engineer", "Engineering"),
    ("Industrial Engineer", "Engineering"),
    
    # Marketing & Sales
    ("Marketing Manager", "Marketing"),
    ("Digital Marketing Specialist", "Marketing"),
    ("Sales Manager", "Sales"),
    ("Business Development Manager", "Sales"),
    ("Content Strategist", "Marketing"),
    ("SEO Specialist", "Marketing"),
    
    # Manufacturing
    ("Manufacturing Engineer", "Manufacturing"),
    ("Quality Assurance Manager", "Manufacturing"),
    ("Supply Chain Manager", "Manufacturing"),
    ("Production Manager", "Manufacturing"),
    
    # Consulting
    ("Management Consultant", "Consulting"),
    ("Strategy Consultant", "Consulting"),
    ("IT Consultant", "Technology"),
    ("HR Consultant", "Human Resources"),
    
    # Real Estate
    ("Real Estate Agent", "Real Estate"),
    ("Property Manager", "Real Estate"),
    ("Real Estate Appraiser", "Real Estate"),
    
    # Media & Entertainment
    ("Journalist", "Media"),
    ("Video Editor", "Media"),
    ("Graphic Designer", "Creative"),
    ("Photographer", "Creative"),
    ("Content Writer", "Media"),
    
    # Government & Public Service
    ("Public Policy Analyst", "Government"),
    ("Urban Planner", "Government"),
    ("Social Worker", "Social Services"),
    
    # Science & Research
    ("Research Scientist", "Research"),
    ("Biomedical Scientist", "Healthcare"),
    ("Environmental Scientist", "Science"),
    ("Chemist", "Science"),
    
    # Hospitality
    ("Hotel Manager", "Hospitality"),
    ("Event Planner", "Hospitality"),
    ("Restaurant Manager", "Hospitality"),
    
    # Transportation & Logistics
    ("Logistics Coordinator", "Logistics"),
    ("Pilot", "Aviation"),
    ("Transportation Manager", "Logistics"),
    
    # Agriculture
    ("Agricultural Scientist", "Agriculture"),
    ("Farm Manager", "Agriculture"),
    
    # Construction
    ("Construction Manager", "Construction"),
    ("Architect", "Architecture"),
    ("Structural Engineer", "Engineering"),
]

def generate_templates(max_professions: int = None, delay_seconds: float = 2.0):
    """
    Generate safety rule templates for common professions.
    
    Args:
        max_professions: Maximum number to generate (None = all)
        delay_seconds: Delay between generations to avoid rate limits
    """
    print("=" * 70)
    print("Safety Template Batch Generator")
    print("=" * 70)
    
    # Initialize system
    llm = get_llm_provider()
    system = UniversalProfessionSystem(llm, "./data")
    
    professions_to_generate = COMMON_PROFESSIONS[:max_professions] if max_professions else COMMON_PROFESSIONS
    
    print(f"\n📋 Generating templates for {len(professions_to_generate)} professions...")
    print(f"⏱️  Estimated time: {len(professions_to_generate) * delay_seconds / 60:.1f} minutes\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, (profession, industry) in enumerate(professions_to_generate, 1):
        print(f"\n[{i}/{len(professions_to_generate)}] {profession} ({industry})")
        
        # Check if template already exists
        existing_template = system.knowledge_expansion.load_safety_template(profession, industry)
        if existing_template:
            print(f"   ⏭️  Template already exists, skipping...")
            skip_count += 1
            continue
        
        try:
            # Create minimal schema for safety generation
            from src.profession.schema import ProfessionSchema
            
            minimal_schema = ProfessionSchema(
                profession_id=f"template_{profession.lower().replace(' ', '_')}",
                profession_name=profession,
                industry=industry
            )
            
            # Generate safety rules
            safety_rules = system.knowledge_expansion.generate_comprehensive_safety_rules(minimal_schema)
            
            # Save as template
            system.knowledge_expansion.save_safety_template(profession, industry, safety_rules)
            
            print(f"   ✅ Generated: {len(safety_rules.critical)} critical, {len(safety_rules.important)} important rules")
            success_count += 1
            
            # Rate limiting
            if i < len(professions_to_generate):
                time.sleep(delay_seconds)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
    
    print("\n" + "=" * 70)
    print("Generation Complete!")
    print("=" * 70)
    print(f"✅ Successfully generated: {success_count}")
    print(f"⏭️  Skipped (existing): {skip_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Templates saved to: data/safety_templates/")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate safety rule templates for common professions")
    parser.add_argument("--max", type=int, default=None, help="Maximum number of professions to generate")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between generations (seconds)")
    
    args = parser.parse_args()
    
    generate_templates(max_professions=args.max, delay_seconds=args.delay)
