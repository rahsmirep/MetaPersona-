# Memory Timeline View (Updated for Visual Design)

## Components Used
- HeaderBar (MetaPersonaLogo, AuthButtons, LanguageSelector, RadiantGlow)
- MemoryEntry
- ModeBadge
- MetadataToggle
- WalletStatusIndicator

## Data Flow
- HeaderBar composes MetaPersonaLogo (black, Copilot-style font), AuthButtons (login/signup, black→white on hover), LanguageSelector (global language state), and RadiantGlow (bottom edge)
- Memory entries (from UIAgentTurn/UIAgentMetadata) flow into MemoryEntry
- UIWeb3Context can be referenced for Web3-linked memory events
- ModeBadge displays current mode from UIAgentMetadata
- MetadataToggle controls visibility of memory metadata

## Web3 Context Effects
- MemoryEntry can show wallet/signature-linked memory events
- WalletStatusIndicator updates if memory entry involves wallet actions

## Persona/Memory/Trace/Mode/Metadata Display
- MemoryEntry displays memory entry and metadata
- ModeBadge and MetadataToggle provide mode and metadata controls

## Visual Design
- Light grey background
- Thin white header bar with radiant glow
- Centered rounded white panel with radiant glow
- Login/Signup: black text, white on hover
- Language selector below buttons

No rendering logic yet.
