# -*- coding: utf-8 -*-
from graphenecommon.transactionbuilder import (
    TransactionBuilder as GrapheneTransactionBuilder,
    ProposalBuilder as GrapheneProposalBuilder,
)

from tuscbase import operations, transactions
from tuscbase.account import PrivateKey, PublicKey
from tuscbase.objects import Operation
from tuscbase.signedtransactions import Signed_Transaction

from .amount import Amount
from .asset import Asset
from .account import Account
from .instance import BlockchainInstance


@BlockchainInstance.inject
class ProposalBuilder(GrapheneProposalBuilder):
    """
    Proposal Builder allows us to construct an independent Proposal that may later be
    added to an instance ot TransactionBuilder.

    :param str proposer: Account name of the proposing user
    :param int proposal_expiration: Number seconds until the proposal is
        supposed to expire
    :param int proposal_review: Number of seconds for review of the
        proposal
    :param tusc.transactionbuilder.TransactionBuilder: Specify
        your own instance of transaction builder (optional)
    :param tusc instance blockchain_instance: TUSC() Blockchain instance
    """

    def define_classes(self):
        self.operation_class = Operation
        self.operations = operations
        self.account_class = Account


@BlockchainInstance.inject
class TransactionBuilder(GrapheneTransactionBuilder):
    """This class simplifies the creation of transactions by adding operations and
    signers."""

    def define_classes(self):
        self.account_class = Account
        self.asset_class = Asset
        self.operation_class = Operation
        self.operations = operations
        self.privatekey_class = PrivateKey
        self.publickey_class = PublicKey
        self.signed_transaction_class = Signed_Transaction
        self.amount_class = Amount
