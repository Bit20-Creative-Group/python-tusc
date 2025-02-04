# -*- coding: utf-8 -*-
from .account import Account
from .blockchainobject import BlockchainObject
from .instance import BlockchainInstance
from graphenecommon.worker import Worker as GrapheneWorker, Workers as GrapheneWorkers


@BlockchainInstance.inject
class Worker(GrapheneWorker):
    """
    Read data about a worker in the chain.

    :param str id: id of the worker
    :param tusc blockchain_instance: TUSC() instance to use when
        accessing a RPC
    """

    def define_classes(self):
        self.account_class = Account
        self.type_id = 14


@BlockchainInstance.inject
class Workers(GrapheneWorkers):
    """
    Obtain a list of workers for an account.

    :param str account_name/id: Name/id of the account (optional)
    :param tusc blockchain_instance: TUSC() instance to use when
        accessing a RPC
    """

    def define_classes(self):
        self.account_class = Account
        self.worker_class = Worker
