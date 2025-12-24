class SignatureFlow:
    """
    Stub for signature request/response logic.
    """
    def __init__(self):
        self.last_request = None
        self.last_response = None

    def request_signature(self, data):
        self.last_request = data
        # Simulate signature required
        from ui.web3.web3_context import Web3Context
        return Web3Context(signature_required=True, identity_state=data).to_dict()

    def receive_signature(self, signature):
        self.last_response = signature
        return {"signature": signature}
