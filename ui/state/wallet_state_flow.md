# Wallet State Flow Diagram (Visual UI v0.8.2)

## State Transitions
- Initial: Wallet disconnected
- Connect wallet → WalletStatusIndicator updates
- Wallet connected → UIWeb3Context updated
- Signature required for wallet action → SignaturePrompt shown
- Wallet disconnected → UIWeb3Context cleared
- HeaderBar hover: AuthButtons (login/signup) change color on hover
- LanguageSelector: language state changes update UI
- Homepage panel visibility toggled by navigation

## UIState ↔ Web3Context
- UIState updates on wallet connect/disconnect
- Signature requirements modify wallet state

## Agent Turns & UI Updates
- Agent may request wallet connection or signature
- UI updates WalletStatusIndicator and SignaturePrompt accordingly

## Signature Flow
- SignaturePrompt shown for wallet actions
- On signature, wallet state updates

## Visual UI Interactions
- HeaderBar: hover states for AuthButtons
- LanguageSelector: updates global language
- RoundedGlowPanel: visible on homepage/wallet

No rendering logic yet.
