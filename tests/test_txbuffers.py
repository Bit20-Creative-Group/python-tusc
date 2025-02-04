# -*- coding: utf-8 -*-
import unittest
from tuscbase import operations
from .fixtures import fixture_data, bitshares


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_add_one_proposal_one_op(self):
        tx1 = bitshares.new_tx()
        proposal1 = bitshares.new_proposal(tx1, proposer="init0")
        op = operations.Transfer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from": "1.2.0",
                "to": "1.2.0",
                "amount": {"amount": 0, "asset_id": "1.3.0"},
                "prefix": "TEST",
            }
        )
        proposal1.appendOps(op)
        tx = tx1.json()
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(len(tx["operations"]), 1)
        ps = tx["operations"][0][1]
        self.assertEqual(len(ps["proposed_ops"]), 1)
        self.assertEqual(ps["proposed_ops"][0]["op"][0], 0)

    def test_add_one_proposal_two_ops(self):
        tx1 = bitshares.new_tx()
        proposal1 = bitshares.new_proposal(tx1, proposer="init0")
        op = operations.Transfer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from": "1.2.0",
                "to": "1.2.0",
                "amount": {"amount": 0, "asset_id": "1.3.0"},
                "prefix": "TEST",
            }
        )
        proposal1.appendOps(op)
        proposal1.appendOps(op)
        tx = tx1.json()
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(len(tx["operations"]), 1)
        ps = tx["operations"][0][1]
        self.assertEqual(len(ps["proposed_ops"]), 2)
        self.assertEqual(ps["proposed_ops"][0]["op"][0], 0)
        self.assertEqual(ps["proposed_ops"][1]["op"][0], 0)

    def test_have_two_proposals(self):
        tx1 = bitshares.new_tx()

        # Proposal 1
        proposal1 = bitshares.new_proposal(tx1, proposer="init0")
        op = operations.Transfer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from": "1.2.0",
                "to": "1.2.0",
                "amount": {"amount": 0, "asset_id": "1.3.0"},
                "prefix": "TEST",
            }
        )
        for _ in range(0, 3):
            proposal1.appendOps(op)

        # Proposal 1
        proposal2 = bitshares.new_proposal(tx1, proposer="init0")
        op = operations.Transfer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from": "1.2.0",
                "to": "1.2.0",
                "amount": {"amount": 5555555, "asset_id": "1.3.0"},
                "prefix": "TEST",
            }
        )
        for _ in range(0, 2):
            proposal2.appendOps(op)
        tx = tx1.json()

        self.assertEqual(len(tx["operations"]), 2)  # 2 proposals

        # Test proposal 1
        prop = tx["operations"][0]
        self.assertEqual(prop[0], 22)
        ps = prop[1]
        self.assertEqual(len(ps["proposed_ops"]), 3)
        for i in range(0, 3):
            self.assertEqual(ps["proposed_ops"][i]["op"][0], 0)

        # Test proposal 2
        prop = tx["operations"][1]
        self.assertEqual(prop[0], 22)
        ps = prop[1]
        self.assertEqual(len(ps["proposed_ops"]), 2)
        for i in range(0, 2):
            self.assertEqual(ps["proposed_ops"][i]["op"][0], 0)
