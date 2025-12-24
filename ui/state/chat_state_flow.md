# Chat State Flow Diagram (Visual UI v0.8.2)

## State Transitions
- Initial: Awaiting user input
- User sends message → agent processes turn
- Agent response received → UI updates chat history
- Signature required → SignaturePrompt shown
- Wallet status changes → WalletStatusIndicator updates
- Metadata toggled → MetadataToggle updates display
- HeaderBar hover: AuthButtons (login/signup) change color on hover
- LanguageSelector: language state changes update UI
- Homepage panel visibility toggled by navigation

## UIState ↔ Web3Context
- UIState listens for wallet/signature changes in Web3Context
- Agent turns may trigger signature flow via Web3Context
- Wallet connection/disconnection updates chat state

## Agent Turns & UI Updates
- Each agent turn updates chat history, persona, and metadata
- Signature requirements pause chat flow until signed

## Signature Flow
- If signature_required, SignaturePrompt is shown
- On signature, agent turn resumes and UI updates

## Visual UI Interactions
- HeaderBar: hover states for AuthButtons
- LanguageSelector: updates global language
- RoundedGlowPanel: visible on homepage/chat

No rendering logic yet.
