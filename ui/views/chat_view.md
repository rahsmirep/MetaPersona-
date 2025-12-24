# Chat View (Updated for Visual Design)

## Components Used
- HeaderBar (MetaPersonaLogo, AuthButtons, LanguageSelector, RadiantGlow)
- RoundedGlowPanel
- ChatMessage
- AgentBubble
- UserBubble
- WalletStatusIndicator
- SignaturePrompt
- ModeBadge
- MetadataToggle

## Data Flow
- HeaderBar composes MetaPersonaLogo (black, Copilot-style font), AuthButtons (login/signup, black→white on hover), LanguageSelector (global language state), and RadiantGlow (bottom edge)
- RoundedGlowPanel contains chat content, with RadiantGlow around edges
- UIAgentTurn objects flow into ChatMessage, AgentBubble, and UserBubble
- WalletStatusIndicator receives UIWeb3Context from backend
- SignaturePrompt is shown when signature_required is true in UIWeb3Context or UIAgentMetadata
- ModeBadge displays current mode from UIAgentMetadata
- MetadataToggle controls visibility of metadata in all components

## Web3 Context Effects
- WalletStatusIndicator and SignaturePrompt update based on wallet/signature state
- ChatMessage, AgentBubble, and UserBubble display wallet/signature info if present in metadata

## Persona/Memory/Trace/Mode/Metadata Display
- PersonaSnapshotCard can be shown for agent turns with persona changes
- MemoryEntry and TraceEntry are referenced in timeline views, not main chat
- ModeBadge and MetadataToggle provide mode and metadata visibility controls

## Visual Design
- Light grey background
- Thin white header bar with radiant glow
- Centered rounded white panel with radiant glow
- Login/Signup: black text, white on hover
- Language selector below buttons

No rendering logic yet.
