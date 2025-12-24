"""
ChatMessage Component

Description:
Represents a single chat message in the UI, either from the agent or user.

Expected Props/State:
- message: UIAgentTurn
- sender: str ("agent" or "user")
- timestamp: str
- metadata: UIAgentMetadata

Web3 Context Interaction:
- Displays wallet/signature status if present in message metadata
- Can show signature prompt if required

UI Schema Models Consumed:
- UIAgentTurn
- UIAgentMetadata
- UIWeb3Context (via metadata)

No rendering logic yet.
"""
