# -*- coding: utf-8 -*-
import unittest
from tusc import TUSC
from tusc.asset import Asset
from tusc.instance import set_shared_bitshares_instance, SharedInstance
from tusc.blockchainobject import BlockchainObject

import logging

log = logging.getLogger()


class Testcases(unittest.TestCase):
    def test_default_connection(self):
        b1 = TUSC("wss://eu.nodes.tusc.ws", nobroadcast=True)
        set_shared_bitshares_instance(b1)
        test = Asset("1.3.0", blockchain_instance=b1)
        # Needed to clear cache
        test.refresh()

        """
        b2 = BitShares("wss://node.tusc.eu", nobroadcast=True)
        set_shared_bitshares_instance(b2)
        bts = Asset("1.3.0", blockchain_instance=b2)
        # Needed to clear cache
        bts.refresh()

        self.assertEqual(test["symbol"], "TEST")
        self.assertEqual(bts["symbol"], "BTS")
        """

    def test_default_connection2(self):
        b1 = TUSC("wss://eu.nodes.tusc.ws", nobroadcast=True)
        test = Asset("1.3.0", blockchain_instance=b1)
        test.refresh()

        """
        b2 = BitShares("wss://node.tusc.eu", nobroadcast=True)
        bts = Asset("1.3.0", blockchain_instance=b2)
        bts.refresh()

        self.assertEqual(test["symbol"], "TEST")
        self.assertEqual(bts["symbol"], "BTS")
        """
