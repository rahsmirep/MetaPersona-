from src.single_use_agent import SingleUseAgent
from ui.formatters.web3_formatters import format_web3_output
from ui.hooks.agent_hooks import run_turn_for_ui
from ui.web3.wallet_manager import WalletManager
from ui.web3.signature_flow import SignatureFlow
from ui.web3.user_identity import UserIdentity

def test_web3_formatter_structure():
    output = format_web3_output(
        display_text="Hello, Web3!",
        persona_tone=["neutral"],
        reasoning_trace="Reasoning here",
        mode="chat",
        metadata={"mode": "chat", "signature_required": True},
        signature_required=True,
        wallet_context={"address": "0x123"}
    )
    assert output["display_text"] == "Hello, Web3!"
    assert output["signature_required"] is True
    assert output["wallet_context"]["address"] == "0x123"

def test_run_turn_for_ui_web3():
    agent = SingleUseAgent(agent_id="web3_agent")
    wallet = WalletManager()
    wallet.connect("0xabc")
    result = run_turn_for_ui(agent, "Test Web3", wallet_context=wallet.get_context())
    assert "display_text" in result
    assert "wallet_context" in result
    assert result["wallet_context"]["address"] == "0xabc"

def test_web3_metadata_integration():
    agent = SingleUseAgent(agent_id="web3_agent")
    result = run_turn_for_ui(agent, "Test Meta", wallet_context=None)
    assert "metadata" in result
    assert "mode" in result["metadata"]
    assert "signature_required" in result["metadata"]

def test_wallet_manager_identity():
    wallet = WalletManager()
    wallet.connect("0xdef")
    identity = UserIdentity(address=wallet.address)
    assert identity.get_address() == "0xdef"
    identity.set_profile({"nickname": "Alice"})
    assert identity.get_profile()["nickname"] == "Alice"

def test_signature_flow():
    sig_flow = SignatureFlow()
    req = sig_flow.request_signature({"data": "sign me"})
    assert req["signature_required"] is True
    resp = sig_flow.receive_signature("signed_data")
    assert resp["signature"] == "signed_data"
