# Trace State Flow Diagram (Visual UI v0.8.2)

## State Transitions
- Initial: Trace log empty
- Agent/user actions generate trace entries
- Web3 events (wallet/signature) add trace entries
- Metadata toggled → MetadataToggle updates display
- HeaderBar hover: AuthButtons (login/signup) change color on hover
- LanguageSelector: language state changes update UI
- Homepage panel visibility toggled by navigation

## UIState ↔ Web3Context
- Trace entries may reference wallet/signature from Web3Context
- UIState updates trace view on new trace entry

## Agent Turns & UI Updates
- Agent turn may generate trace log
- Signature requirements may pause trace entry until signed

## Visual UI Interactions
- HeaderBar: hover states for AuthButtons
- LanguageSelector: updates global language
- RoundedGlowPanel: visible on homepage/trace

No rendering logic yet.
