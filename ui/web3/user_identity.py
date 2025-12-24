class UserIdentity:
    """
    Stub for user identity logic (Web3 address, profile, etc).
    """
    def __init__(self, address=None):
        self.address = address
        self.profile = {}

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def set_profile(self, profile):
        self.profile = profile

    def get_profile(self):
        from ui.web3.web3_context import Web3Context
        return Web3Context(identity_state=self.profile, wallet_address=self.address).to_dict()
