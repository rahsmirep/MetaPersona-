from src.single_use_agent import SingleUseAgent
from ui.formatters.ui_response_builder import build_ui_response
from ui.hooks.agent_hooks import run_turn_for_ui
from ui.web3.wallet_manager import WalletManager
from ui.web3.signature_flow import SignatureFlow
from ui.web3.user_identity import UserIdentity
from ui.formatters.ui_schema import UIAgentTurn

def test_unified_ui_response_structure():
    agent = SingleUseAgent(agent_id="step5_agent")
    wallet = WalletManager()
    wallet.connect("0xstep5")
    result = run_turn_for_ui(agent, "Step 5 test", wallet_context=wallet.get_context())
    assert isinstance(result, UIAgentTurn)
    assert result.display_text is not None
    assert result.metadata is not None
    assert result.persona_snapshot is not None
    assert result.web3_context is not None
    assert result.web3_context.wallet_address == "0xstep5"

def test_metadata_persona_web3_present():
    agent = SingleUseAgent(agent_id="step5_agent")
    wallet = WalletManager()
    wallet.connect("0xmeta")
    result = run_turn_for_ui(agent, "Meta test", wallet_context=wallet.get_context())
    assert result.metadata.mode is not None
    assert result.persona_snapshot.voice_style is not None
    assert result.web3_context.wallet_address == "0xmeta"

def test_hooks_return_unified_response():
    agent = SingleUseAgent(agent_id="step5_agent")
    result = run_turn_for_ui(agent, "Hooks test", wallet_context=None)
    assert isinstance(result, UIAgentTurn)

def test_no_cognitive_logic_modified():
    agent = SingleUseAgent(agent_id="step5_agent")
    # Direct cognitive output should match UI response display_text
    direct = agent.process_turn("Direct test")
    ui_result = run_turn_for_ui(agent, "Direct test", wallet_context=None)
    assert ui_result.display_text == direct.payload.get('result')

def test_all_tests_use_single_use_agent():
    agent = SingleUseAgent(agent_id="step5_agent")
    wallet = WalletManager()
    wallet.connect("0xall")
    result = run_turn_for_ui(agent, "All test", wallet_context=wallet.get_context())
    assert isinstance(agent, SingleUseAgent)
    assert result.web3_context.wallet_address == "0xall"
