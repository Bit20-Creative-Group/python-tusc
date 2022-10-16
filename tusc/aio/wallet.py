# -*- coding: utf-8 -*-
from tuscbase.account import PrivateKey
from graphenecommon.aio.wallet import Wallet as GrapheneWallet
from ..instance import BlockchainInstance


# Uses synchronous BlockchainInstance because it's __init__ is synchronous.
# Other methods will use async Instance.
@BlockchainInstance.inject
class Wallet(GrapheneWallet):
    def define_classes(self):
        # identical to those in tusc.py!
        self.default_key_store_app_name = "tusc"
        self.privatekey_class = PrivateKey
