# Homepage View

## Components Used
- HeaderBar (MetaPersonaLogo, AuthButtons, LanguageSelector, RadiantGlow)
- RoundedGlowPanel

## Data Flow
- HeaderBar composes MetaPersonaLogo (black, Copilot-style font), AuthButtons (login/signup, black→white on hover), LanguageSelector (global language state), and RadiantGlow (bottom edge)
- RoundedGlowPanel displays homepage content, with RadiantGlow around edges

## Web3 Context Effects
- AuthButtons may trigger wallet connect if login is Web3-based
- HeaderBar can display wallet status if user is logged in

## Visual Design
- Light grey background
- Thin white header bar with radiant glow
- Centered rounded white panel with radiant glow
- Login/Signup: black text, white on hover
- Language selector below buttons

No rendering logic yet.
