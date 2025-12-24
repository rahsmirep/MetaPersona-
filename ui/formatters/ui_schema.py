from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class UIAgentMetadata(BaseModel):
    mode: Optional[str]
    handler: Optional[str]
    persona_shaping: Optional[str]
    memory_updates: Optional[Dict[str, Any]]
    routing_trace: Optional[Any]
    signature_required: bool = False
    persona_state_update: bool = False

class UIPersonaSnapshot(BaseModel):
    voice_style: Optional[str]
    tone_modifiers: Optional[List[str]]
    signature_phrasing: Optional[List[str]]
    persona_memory: Optional[Dict[str, Any]]

class UIWeb3Context(BaseModel):
    wallet_address: Optional[str]
    connection_status: bool = False
    signature_required: bool = False
    identity_state: Optional[Dict[str, Any]]

class UIAgentTurn(BaseModel):
    display_text: str
    reasoning_trace: Optional[str]
    metadata: UIAgentMetadata
    persona_snapshot: UIPersonaSnapshot
    web3_context: UIWeb3Context
