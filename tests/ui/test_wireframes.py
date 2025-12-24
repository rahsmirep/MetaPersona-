import os

WIREFRAME_FILES = [
    "chat_screen.md",
    "wallet_connect.md",
    "persona_viewer.md",
    "reasoning_trace_view.md",
    "memory_timeline.md",
    "settings_screen.md"
]
WIREFRAME_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ui", "wireframes")

REQUIRED_SECTIONS = [
    "Sections",
    "Layout",
    "Notes"
]

def test_wireframe_files_exist():
    for fname in WIREFRAME_FILES:
        path = os.path.join(WIREFRAME_DIR, fname)
        assert os.path.exists(path), f"Wireframe file missing: {fname}"

def test_wireframe_sections_present():
    for fname in WIREFRAME_FILES:
        path = os.path.join(WIREFRAME_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            for section in REQUIRED_SECTIONS:
                assert section in content, f"Section '{section}' missing in {fname}"

def test_no_frontend_framework_reference():
    for fname in WIREFRAME_FILES:
        path = os.path.join(WIREFRAME_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            assert "react" not in content
            assert "vue" not in content
            assert "angular" not in content
            assert "svelte" not in content

def test_wireframes_align_with_backend_schema():
    # Check that wireframes mention persona, wallet, memory, trace, mode, signature, metadata
    keywords = ["persona", "wallet", "memory", "trace", "mode", "signature", "metadata"]
    for fname in WIREFRAME_FILES:
        path = os.path.join(WIREFRAME_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            for kw in keywords:
                assert kw in content, f"Keyword '{kw}' missing in {fname}"
