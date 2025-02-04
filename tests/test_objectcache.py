# -*- coding: utf-8 -*-
import time
import unittest
from tusc import TUSC, exceptions
from tusc.instance import set_shared_bitshares_instance
from tusc.blockchainobject import ObjectCache


class Testcases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = TUSC(
            nobroadcast=True,
        )
        set_shared_bitshares_instance(self.bts)

    def test_cache(self):
        cache = ObjectCache(default_expiration=1)
        self.assertEqual(str(cache), "ObjectCacheInMemory(default_expiration=1)")

        # Data
        cache["foo"] = "bar"
        self.assertIn("foo", cache)
        self.assertEqual(cache["foo"], "bar")
        self.assertEqual(cache.get("foo", "New"), "bar")

        # Expiration
        time.sleep(2)
        self.assertNotIn("foo", cache)

        # Get
        self.assertEqual(cache.get("foo", "New"), "New")
