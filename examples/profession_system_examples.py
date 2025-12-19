"""
Example usage of the Universal Profession Understanding System
"""
from pathlib import Path
from src.profession import UniversalProfessionSystem
from src.llm_provider import get_llm_provider
from src.cognitive_profile import ProfileManager

def example_software_engineer():
    """Example: Onboarding a software engineer."""
    
    # Initialize system
    llm = get_llm_provider()
    upus = UniversalProfessionSystem(
        llm_provider=llm,
        data_dir=Path("data"),
        google_api_key="YOUR_GOOGLE_API_KEY",  # Set in environment
        google_cse_id="YOUR_GOOGLE_CSE_ID"
    )
    
    # User describes their profession
    profession_description = """
    I'm a senior software engineer working in fintech. 
    
    My main responsibilities include:
    - Designing and implementing scalable backend systems
    - Leading code reviews and mentoring junior developers
    - Architecting microservices with high availability requirements
    - Ensuring security and compliance with financial regulations
    
    Daily tasks include writing Python and Go code, reviewing PRs, sprint planning, 
    and on-call rotations for production issues.
    
    Tools I use: Python, Go, Docker, Kubernetes, AWS, PostgreSQL, Redis, Kafka, 
    GitHub, Jira, PagerDuty, DataDog
    
    Methodologies: Agile/Scrum, TDD, CI/CD, DevOps practices
    
    I work in a fast-paced environment with high autonomy, collaborating with 
    a cross-functional team of 15 people. We have strict compliance requirements 
    for PCI-DSS and SOC 2.
    
    Critical rules: Never deploy to production without tests, always get code review, 
    never commit credentials, follow security protocols for sensitive data.
    """
    
    # Onboard the profession
    schema = upus.onboard_profession(
        user_input=profession_description,
        user_id="user123",
        interactive=False
    )
    
    print("\n" + "="*80)
    print("PROFESSION SCHEMA CREATED")
    print("="*80)
    print(schema.to_json())
    
    # Later: Process a query with profession context
    profile_manager = ProfileManager("data")
    cognitive_profile = profile_manager.load_profile()
    
    query = "Should I refactor this legacy payment processing module or wait until after the Q4 release?"
    
    result = upus.process_query(
        query=query,
        user_id="user123",
        cognitive_profile=cognitive_profile
    )
    
    print("\n" + "="*80)
    print("ENHANCED QUERY WITH PROFESSION CONTEXT")
    print("="*80)
    print(result["enhanced_query"])
    
    print("\n" + "="*80)
    print("DECISION FACTORS EXTRACTED")
    print("="*80)
    import json
    print(json.dumps(result["decision_factors"], indent=2))


def example_nurse():
    """Example: Onboarding a nurse."""
    
    llm = get_llm_provider()
    upus = UniversalProfessionSystem(
        llm_provider=llm,
        data_dir=Path("data")
    )
    
    profession_description = """
    I'm a registered nurse (RN) working in the ICU at a Level 1 trauma center.
    
    My responsibilities:
    - Assessing patient conditions and vital signs
    - Administering medications per physician orders
    - Operating life support equipment (ventilators, ECMO, dialysis)
    - Coordinating care with doctors, specialists, and other nurses
    - Documenting all care in electronic health records
    - Educating patients and families
    
    Daily routine: 12-hour shifts, usually 3-4 patients at once, constant monitoring,
    medication rounds every 2-4 hours, charting every 1-2 hours
    
    Tools: Epic EMR, IV pumps, cardiac monitors, ventilators, crash carts,
    medication dispensing systems (Pyxis)
    
    Environment: Fast-paced, high-stress, teamwork is critical, 24/7 coverage with
    night and day shifts
    
    Critical safety rules:
    - NEVER administer medication without checking patient ID and order
    - Always follow the 5 Rights of medication administration
    - Immediately report adverse reactions or patient deterioration
    - Maintain sterile technique for invasive procedures
    - Document everything in real-time
    - Follow isolation protocols for infectious patients
    
    Regulatory: HIPAA compliance, Joint Commission standards, state nursing board regulations
    """
    
    schema = upus.onboard_profession(
        user_input=profession_description,
        user_id="nurse456"
    )
    
    # Show summary
    summary = upus.get_profession_summary("nurse456")
    print("\n" + "="*80)
    print("PROFESSION SUMMARY")
    print("="*80)
    print(summary)


def example_financial_analyst():
    """Example: Onboarding a financial analyst."""
    
    llm = get_llm_provider()
    upus = UniversalProfessionSystem(
        llm_provider=llm,
        data_dir=Path("data")
    )
    
    profession_description = """
    I'm a senior financial analyst at an investment bank, focusing on equity research.
    
    Responsibilities:
    - Building financial models and valuations for public companies
    - Analyzing market trends and company performance
    - Writing research reports with buy/sell/hold recommendations
    - Presenting findings to portfolio managers and clients
    - Monitoring portfolio companies and updating models
    
    Daily tasks: Market monitoring, reading earnings reports, updating Excel models,
    industry research, client calls, team meetings
    
    Tools: Excel (advanced modeling), Bloomberg Terminal, FactSet, Python for data analysis,
    PowerPoint for presentations, Salesforce for CRM
    
    Methodologies: DCF valuation, comparable company analysis, precedent transactions,
    financial statement analysis, ratio analysis
    
    Environment: Fast-paced during earnings season, high pressure for accurate forecasts,
    moderate autonomy with senior oversight
    
    Decision framework: Data-driven analysis, peer comparison, management quality assessment,
    industry trends, macroeconomic factors
    
    Constraints:
    - Must comply with SEC regulations on insider trading
    - Chinese Wall policies - no sharing non-public information
    - All recommendations must be reviewed by compliance
    - Public statements require legal approval
    """
    
    schema = upus.onboard_profession(
        user_input=profession_description,
        user_id="analyst789"
    )
    
    # Create aligned persona
    profile_manager = ProfileManager("data")
    cognitive_profile = profile_manager.load_profile()
    
    aligned_persona = upus.create_aligned_persona("analyst789", cognitive_profile)
    
    print("\n" + "="*80)
    print("ALIGNED PERSONA (Parallel-Self)")
    print("="*80)
    import json
    print(json.dumps(aligned_persona, indent=2))


def example_query_with_expansion():
    """Example: Query that triggers knowledge expansion."""
    
    llm = get_llm_provider()
    upus = UniversalProfessionSystem(
        llm_provider=llm,
        data_dir=Path("data"),
        google_api_key="YOUR_API_KEY",
        google_cse_id="YOUR_CSE_ID"
    )
    
    # Load existing profession
    profile_manager = ProfileManager("data")
    cognitive_profile = profile_manager.load_profile()
    
    # Query mentions something not in the schema
    query = "What are the best practices for implementing GDPR compliance in our customer data pipeline?"
    
    # This will detect "GDPR" as a knowledge gap and fetch information
    result = upus.process_query(
        query=query,
        user_id="user123",
        cognitive_profile=cognitive_profile
    )
    
    print("\n" + "="*80)
    print("KNOWLEDGE EXPANSION TRIGGERED")
    print("="*80)
    print(f"Sources used: {len(result['sources'])}")
    for source in result['sources']:
        print(f"  - {source}")
    
    print("\nEnhanced query with new knowledge:")
    print(result["enhanced_query"])


if __name__ == "__main__":
    print("Universal Profession Understanding System - Examples\n")
    
    # Run examples
    print("\n" + "="*80)
    print("EXAMPLE 1: Software Engineer")
    print("="*80)
    example_software_engineer()
    
    print("\n\n" + "="*80)
    print("EXAMPLE 2: ICU Nurse")
    print("="*80)
    example_nurse()
    
    print("\n\n" + "="*80)
    print("EXAMPLE 3: Financial Analyst")
    print("="*80)
    example_financial_analyst()
    
    print("\n\n" + "="*80)
    print("EXAMPLE 4: Query with Knowledge Expansion")
    print("="*80)
    example_query_with_expansion()
