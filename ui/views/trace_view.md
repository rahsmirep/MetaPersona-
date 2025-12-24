# Trace View (Updated for Visual Design)

## Components Used
- HeaderBar (MetaPersonaLogo, AuthButtons, LanguageSelector, RadiantGlow)
- TraceEntry
- ModeBadge
- MetadataToggle
- WalletStatusIndicator

## Data Flow
- HeaderBar composes MetaPersonaLogo (black, Copilot-style font), AuthButtons (login/signup, black→white on hover), LanguageSelector (global language state), and RadiantGlow (bottom edge)
- Trace logs (from UIAgentTurn/UIAgentMetadata) flow into TraceEntry
- UIWeb3Context can be referenced for Web3-related trace events
- ModeBadge displays current mode from UIAgentMetadata
- MetadataToggle controls visibility of trace metadata

## Web3 Context Effects
- TraceEntry can show Web3 event traces (signatures, wallet changes)
- WalletStatusIndicator updates if trace involves wallet actions

## Persona/Memory/Trace/Mode/Metadata Display
- TraceEntry displays trace log and metadata
- ModeBadge and MetadataToggle provide mode and metadata controls

## Visual Design
- Light grey background
- Thin white header bar with radiant glow
- Centered rounded white panel with radiant glow
- Login/Signup: black text, white on hover
- Language selector below buttons

No rendering logic yet.
