# Wallet View (Updated for Visual Design)

## Components Used
- HeaderBar (MetaPersonaLogo, AuthButtons, LanguageSelector, RadiantGlow)
- WalletStatusIndicator
- SignaturePrompt
- ModeBadge
- MetadataToggle

## Data Flow
- HeaderBar composes MetaPersonaLogo (black, Copilot-style font), AuthButtons (login/signup, black→white on hover), LanguageSelector (global language state), and RadiantGlow (bottom edge)
- UIWeb3Context flows into WalletStatusIndicator and SignaturePrompt
- ModeBadge displays current mode from UIAgentMetadata
- MetadataToggle controls visibility of wallet-related metadata

## Web3 Context Effects
- WalletStatusIndicator updates on wallet connection/disconnection
- SignaturePrompt appears when signature is required for wallet actions

## Persona/Memory/Trace/Mode/Metadata Display
- PersonaSnapshotCard may show wallet-linked persona state
- TraceEntry can show wallet-related trace logs
- ModeBadge and MetadataToggle provide mode and metadata controls

## Visual Design
- Light grey background
- Thin white header bar with radiant glow
- Centered rounded white panel with radiant glow
- Login/Signup: black text, white on hover
- Language selector below buttons

No rendering logic yet.
