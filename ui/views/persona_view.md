# Persona View (Updated for Visual Design)

## Components Used
- HeaderBar (MetaPersonaLogo, AuthButtons, LanguageSelector, RadiantGlow)
- PersonaSnapshotCard
- ModeBadge
- MetadataToggle
- WalletStatusIndicator

## Data Flow
- HeaderBar composes MetaPersonaLogo (black, Copilot-style font), AuthButtons (login/signup, black→white on hover), LanguageSelector (global language state), and RadiantGlow (bottom edge)
- UIPersonaSnapshot flows into PersonaSnapshotCard
- UIWeb3Context can be referenced for persona-linked wallet info
- ModeBadge displays current mode from UIAgentMetadata
- MetadataToggle controls visibility of persona metadata

## Web3 Context Effects
- PersonaSnapshotCard can show wallet/signature status linked to persona
- WalletStatusIndicator updates if persona is linked to wallet

## Persona/Memory/Trace/Mode/Metadata Display
- PersonaSnapshotCard displays persona state and metadata
- ModeBadge and MetadataToggle provide mode and metadata controls

## Visual Design
- Light grey background
- Thin white header bar with radiant glow
- Centered rounded white panel with radiant glow
- Login/Signup: black text, white on hover
- Language selector below buttons

No rendering logic yet.
