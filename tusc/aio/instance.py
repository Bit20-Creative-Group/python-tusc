# -*- coding: utf-8 -*-
from graphenecommon.aio.instance import AbstractBlockchainInstanceProvider


class SharedInstance:
    """This class merely offers a singelton for the Blockchain Instance."""

    instance = None
    config = {}


class BlockchainInstance(AbstractBlockchainInstanceProvider):
    """This is a class that allows compatibility with previous naming conventions."""

    _sharedInstance = SharedInstance

    def __init__(self, *args, **kwargs):
        # Also allow 'tusc_instance'
        if kwargs.get("tusc_instance"):
            kwargs["blockchain_instance"] = kwargs["tusc_instance"]
        AbstractBlockchainInstanceProvider.__init__(self, *args, **kwargs)

    def get_instance_class(self):
        """Should return the Chain instance class, e.g. `tusc.TUSC`"""
        import tusc.aio as tusc

        return tusc.TUSC

    @property
    def tusc(self):
        """Alias for the specific blockchain."""
        return self.blockchain


def shared_blockchain_instance():
    return BlockchainInstance().shared_blockchain_instance()


def set_shared_blockchain_instance(instance):
    instance.clear_cache()
    # instance.set_shared_instance()
    BlockchainInstance.set_shared_blockchain_instance(instance)


def set_shared_config(config):
    BlockchainInstance.set_shared_config(config)


shared_tusc_instance = shared_blockchain_instance
set_shared_tusc_instance = set_shared_blockchain_instance
