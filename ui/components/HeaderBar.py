"""
HeaderBar Component

Description:
Top header bar for the MetaPersona homepage and app. Thin white bar with radiant glow at the bottom edge.

Expected Props/State:
- children: list (MetaPersonaLogo, AuthButtons, LanguageSelector)
- glow: bool (enables RadiantGlow at bottom)

UI State Interactions:
- Responds to login/signup hover state
- Language selection updates global UI state

UI Schema Usage:
- None directly, but passes context to children

Web3 Context Usage:
- Can display wallet status if user is logged in

No rendering logic yet.
"""
