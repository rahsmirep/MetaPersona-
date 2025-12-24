"""
TraceEntry Component

Description:
Represents a single trace log entry in the reasoning or memory timeline.

Expected Props/State:
- trace: dict (from UIAgentTurn or UIAgentMetadata)
- timestamp: str
- metadata: UIAgentMetadata

Web3 Context Interaction:
- Can show trace of Web3 events (signatures, wallet changes)

UI Schema Models Consumed:
- UIAgentTurn
- UIAgentMetadata
- UIWeb3Context

No rendering logic yet.
"""
