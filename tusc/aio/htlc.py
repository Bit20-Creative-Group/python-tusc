# -*- coding: utf-8 -*-
from ..exceptions import HtlcDoesNotExistException
from .blockchainobject import BlockchainObject


class Htlc(BlockchainObject):
    """
    Read data about an HTLC contract on the chain.

    :param str id: id of the HTLC
    :param tusc blockchain_instance: TUSC() instance to use when
        accessing a RPC
    """

    type_id = 16

    async def refresh(self):
        data = await self.blockchain.rpc.get_object(self.identifier)
        if not data:
            raise HtlcDoesNotExistException(self.identifier)
        await super(Htlc, self).__init__(data)
