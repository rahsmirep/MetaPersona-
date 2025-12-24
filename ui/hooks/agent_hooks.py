from src.single_use_agent import SingleUseAgent
from ui.formatters.ui_response_builder import build_ui_response
from ui.web3.wallet_manager import WalletManager
from ui.web3.signature_flow import SignatureFlow
from ui.web3.user_identity import UserIdentity

def run_turn_for_ui(agent: SingleUseAgent, user_input: str, wallet_context=None):
    """
    Calls SingleUseAgent.process_turn(), returns unified UIAgentTurn object.
    """
    agent_msg = agent.process_turn(user_input)
    persona_snapshot = getattr(agent, 'persona_context', None)
    mode = agent.get_mode() if hasattr(agent, 'get_mode') else None
    output = agent_msg.payload.get('result') if hasattr(agent_msg, 'payload') else None
    reasoning_trace = agent_msg.payload.get('internal') if hasattr(agent_msg, 'payload') else None
    def safe_bool(val):
        return bool(val) if val is not None else False
    metadata = {
        "mode": mode,
        "handler": agent_msg.metadata.get('handler') if hasattr(agent_msg, 'metadata') else None,
        "persona_shaping": getattr(persona_snapshot, 'voice_style', None),
        "memory_updates": getattr(persona_snapshot, 'persona_memory', None),
        "routing_trace": agent_msg.metadata.get('routing_trace') if hasattr(agent_msg, 'metadata') else None,
        "signature_required": safe_bool(agent_msg.metadata.get('signature_required') if hasattr(agent_msg, 'metadata') else False),
        "persona_state_update": safe_bool(agent_msg.metadata.get('persona_state_update') if hasattr(agent_msg, 'metadata') else False)
    }
    persona_snapshot_dict = {
        "voice_style": getattr(persona_snapshot, 'voice_style', None),
        "tone_modifiers": getattr(persona_snapshot, 'tone_modifiers', None),
        "signature_phrasing": getattr(persona_snapshot, 'signature_phrasing', None),
        "persona_memory": getattr(persona_snapshot, 'persona_memory', None)
    }
    web3_context = wallet_context or {
        "wallet_address": None,
        "connection_status": False,
        "signature_required": metadata["signature_required"],
        "identity_state": None
    }
    return build_ui_response(
        display_text=output,
        reasoning_trace=reasoning_trace,
        metadata=metadata,
        persona_snapshot=persona_snapshot_dict,
        web3_context=web3_context
    )

def get_trace_for_ui(agent: SingleUseAgent):
    if hasattr(agent, 'get_mode_log'):
        return agent.get_mode_log()
    return []

def get_persona_state_for_ui(agent: SingleUseAgent):
    return getattr(agent, 'persona_context', None)
