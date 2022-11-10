# -*- coding: utf-8 -*-
from .amount import Amount
from .account import Account
from .instance import BlockchainInstance
from graphenecommon.aio.vesting import Vesting as GrapheneVesting


@BlockchainInstance.inject
class Vesting(GrapheneVesting):
    """
    Read data about a Vesting Balance in the chain.

    :param str id: Id of the vesting balance
    :param tusc blockchain_instance: TUSC() instance to use when
        accessing a RPC
    """

    def define_classes(self):
        self.type_id = 13
        self.account_class = Account
        self.amount_class = Amount
