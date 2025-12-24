from ui.formatters.ui_schema import UIAgentTurn, UIAgentMetadata, UIPersonaSnapshot, UIWeb3Context

def build_ui_response(display_text, reasoning_trace, metadata, persona_snapshot, web3_context):
    """
    Combines agent output, metadata, persona snapshot, and Web3 context into a unified UIAgentTurn object.
    """
    return UIAgentTurn(
        display_text=display_text,
        reasoning_trace=reasoning_trace,
        metadata=UIAgentMetadata(**metadata),
        persona_snapshot=UIPersonaSnapshot(**persona_snapshot),
        web3_context=UIWeb3Context(**web3_context)
    )
