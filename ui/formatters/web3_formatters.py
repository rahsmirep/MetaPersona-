def format_web3_output(display_text, persona_tone, reasoning_trace, mode, metadata=None, signature_required=False, wallet_context=None):
    """
    Wraps cognitive outputs into a Web3-friendly structure for UI.
    """
    return {
        "display_text": display_text,
        "persona_tone": persona_tone,
        "reasoning_trace": reasoning_trace,
        "mode": mode,
        "metadata": metadata or {},
        "signature_required": signature_required,
        "wallet_context": wallet_context
    }
