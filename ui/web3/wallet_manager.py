class WalletManager:
    """
    Stub for wallet logic (connect, get address, etc).
    """
    def __init__(self):
        self.connected = False
        self.address = None
        self.context = {}

    def connect(self, address):
        self.connected = True
        self.address = address
        self.context = {"address": address}

    def disconnect(self):
        self.connected = False
        self.address = None
        self.context = {}

    def get_context(self):
        from ui.web3.web3_context import Web3Context
        return Web3Context(
            wallet_address=self.address,
            connection_status=self.connected,
            signature_required=False,
            identity_state={"address": self.address}
        ).to_dict()
