class Web3Context:
    """
    Tracks wallet address, connection status, signature requirements, and identity state for UI.
    """
    def __init__(self, wallet_address=None, connection_status=False, signature_required=False, identity_state=None):
        self.wallet_address = wallet_address
        self.connection_status = connection_status
        self.signature_required = signature_required
        self.identity_state = identity_state or {}

    def to_dict(self):
        return {
            "wallet_address": self.wallet_address,
            "connection_status": self.connection_status,
            "signature_required": self.signature_required,
            "identity_state": self.identity_state
        }
