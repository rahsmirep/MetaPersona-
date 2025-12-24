# Persona State Flow Diagram (Visual UI v0.8.2)

## State Transitions
- Initial: Persona loaded from backend
- Persona updated by agent turn → PersonaSnapshotCard updates
- Wallet/signature changes may affect persona state
- Metadata toggled → MetadataToggle updates display
- HeaderBar hover: AuthButtons (login/signup) change color on hover
- LanguageSelector: language state changes update UI
- Homepage panel visibility toggled by navigation

## UIState ↔ Web3Context
- Persona state may reference wallet/signature from Web3Context
- UIState updates persona view on agent turn

## Agent Turns & UI Updates
- Agent turn may update persona, triggering UI update
- Signature requirements may pause persona update until signed

## Visual UI Interactions
- HeaderBar: hover states for AuthButtons
- LanguageSelector: updates global language
- RoundedGlowPanel: visible on homepage/persona

No rendering logic yet.
