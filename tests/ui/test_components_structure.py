import os
import importlib
import inspect

COMPONENTS = [
    "ChatMessage",
    "AgentBubble",
    "UserBubble",
    "WalletStatusIndicator",
    "SignaturePrompt",
    "PersonaSnapshotCard",
    "TraceEntry",
    "MemoryEntry",
    "ModeBadge",
    "MetadataToggle",
    # New design-aware components
    "HeaderBar",
    "MetaPersonaLogo",
    "AuthButtons",
    "LanguageSelector",
    "RoundedGlowPanel",
    "RadiantGlow",
]
COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ui", "components")
SCHEMA_MODELS = [
    "UIAgentTurn",
    "UIAgentMetadata",
    "UIWeb3Context",
    "UIPersonaSnapshot",
]

def test_component_files_exist():
    for comp in COMPONENTS:
        fname = os.path.join(COMPONENT_DIR, f"{comp}.py")
        assert os.path.exists(fname), f"Component file missing: {fname}"

def test_component_structure():
    for comp in COMPONENTS:
        module_name = f"ui.components.{comp}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            # Only check file content, not import errors
            fname = os.path.join(COMPONENT_DIR, f"{comp}.py")
            with open(fname, "r", encoding="utf-8") as f:
                content = f.read().lower()
                # Check for 'props' or 'state' description
                assert "props" in content or "state" in content, f"Props/state missing in {comp}"
                # Check for schema model references (except for utility/header components)
                if comp not in ["HeaderBar", "MetaPersonaLogo", "AuthButtons", "LanguageSelector", "RoundedGlowPanel", "RadiantGlow"]:
                    found = any(model.lower() in content for model in SCHEMA_MODELS)
                    assert found, f"Schema model missing in {comp}"
                # Check for web3 context mention (if applicable)
                if comp not in ["MetaPersonaLogo", "LanguageSelector", "RadiantGlow"]:
                    assert "web3" in content, f"Web3 context missing in {comp}"
                # MetaPersonaLogo must specify black text color
                if comp == "MetaPersonaLogo":
                    assert "black" in content, "MetaPersonaLogo must specify black text color"
                # RadiantGlow must mention gradient
                if comp == "RadiantGlow":
                    assert "gradient" in content or "purple" in content, "RadiantGlow must reference gradient colors"
                # HeaderBar must mention composition of logo/buttons/selector/glow
                if comp == "HeaderBar":
                    assert "metapersona" in content and "auth" in content and "language" in content and "glow" in content, "HeaderBar must mention logo, auth, language, glow"
                # LanguageSelector must be present
                if comp == "LanguageSelector":
                    assert "language" in content, "LanguageSelector must mention language selection"
                # Ensure no rendering logic
                assert "def " not in content and "class " not in content, f"Rendering logic found in {comp}"
        else:
            # If import works, check docstring
            doc = inspect.getdoc(module)
            assert doc and "props" in doc.lower(), f"Props/state missing in {comp}"
            if comp not in ["HeaderBar", "MetaPersonaLogo", "AuthButtons", "LanguageSelector", "RoundedGlowPanel", "RadiantGlow"]:
                found = any(model.lower() in doc.lower() for model in SCHEMA_MODELS)
                assert found, f"Schema model missing in {comp}"
            if comp not in ["MetaPersonaLogo", "LanguageSelector", "RadiantGlow"]:
                assert "web3" in doc.lower(), f"Web3 context missing in {comp}"
            if comp == "MetaPersonaLogo":
                assert "black" in doc.lower(), "MetaPersonaLogo must specify black text color"
            if comp == "RadiantGlow":
                assert "gradient" in doc.lower() or "purple" in doc.lower(), "RadiantGlow must reference gradient colors"
            if comp == "HeaderBar":
                assert "metapersona" in doc.lower() and "auth" in doc.lower() and "language" in doc.lower() and "glow" in doc.lower(), "HeaderBar must mention logo, auth, language, glow"
            if comp == "LanguageSelector":
                assert "language" in doc.lower(), "LanguageSelector must mention language selection"
            assert not any(hasattr(module, attr) for attr in dir(module) if callable(getattr(module, attr))), f"Rendering logic found in {comp}"
