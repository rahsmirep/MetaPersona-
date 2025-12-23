from typing import Any
from pydantic import ValidationError
from .schema import ProfessionSchema
from .onboarding_interpreter import OnboardingInterpreter

class ProfessionSchemaInterpreter:
    """
    Extracts and validates ProfessionSchema from raw onboarding text.
    """
    def __init__(self, llm_provider: Any):
        self.llm_provider = llm_provider
        self.onboarding = OnboardingInterpreter(llm_provider)

    def extract_schema(self, text: str, user_id: str = "default_user") -> ProfessionSchema:
        """
        Extract and validate ProfessionSchema from raw text.
        """
        schema = self.onboarding.interpret(text, user_id)
        # Dataclass instantiation acts as validation
        try:
            validated_schema = ProfessionSchema(**schema.__dict__)
            return validated_schema
        except TypeError as e:
            raise ValueError(f"ProfessionSchema validation failed: {e}")

    def mock_extract_schema(self, mock_data: dict) -> ProfessionSchema:
        """
        For testing: create ProfessionSchema from mock data.
        """
        try:
            schema = ProfessionSchema(**mock_data)
            return schema
        except TypeError as e:
            raise ValueError(f"ProfessionSchema validation failed: {e}")
