# -*- coding: utf-8 -*-
from asyncinit import asyncinit
from fractions import Fraction

from .account import Account
from .amount import Amount
from .asset import Asset
from ..exceptions import InvalidAssetException
from .instance import BlockchainInstance
from ..utils import assets_from_string, formatTimeString, parse_time

from graphenecommon.aio.price import Price as GraphenePrice


@BlockchainInstance.inject
class Price(GraphenePrice):
    """
    This class deals with all sorts of prices of any pair of assets to simplify dealing
    with the tuple::

            (quote, base)

        each being an instance of :class:`tusc.amount.Amount`. The
        amount themselves define the price.

        .. note::

            The price (floating) is derived as ``base/quote``

        :param list args: Allows to deal with different representations of a price
        :param tusc.aio.asset.Asset base: Base asset
        :param tusc.aio.asset.Asset quote: Quote asset
        :param tusc.aio.tusc.TUSC blockchain_instance: TUSC instance
        :returns: All data required to represent a price
        :rtype: dict

        Way to obtain a proper instance:

            * ``args`` is a str with a price and two assets
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of :class:`tusc.aio.asset.Asset`
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of ``str``
            * ``args`` can be dict with keys ``price``, ``base``, and ``quote`` (*graphene balances*)
            * ``args`` can be dict with keys ``base`` and ``quote``
            * ``args`` can be dict with key ``receives`` (filled orders)
            * ``args`` being a list of ``[quote, base]`` both being instances of :class:`tusc.aio.amount.Amount`
            * ``args`` being a list of ``[quote, base]`` both being instances of ``str`` (``amount symbol``)
            * ``base`` and ``quote`` being instances of :class:`tusc.aio.asset.Amount`

        This allows instanciations like:

        * ``Price("0.315 USD/TUSC")``
        * ``Price(0.315, base="USD", quote="TUSC")``
        * ``Price(0.315, base=Asset("USD"), quote=Asset("TUSC"))``
        * ``Price({"base": {"amount": 1, "asset_id": "1.3.0"}, "quote": {"amount": 10, "asset_id": "1.3.106"}})``
        * ``Price({"receives": {"amount": 1, "asset_id": "1.3.0"}, "pays": {"amount": 10, "asset_id": "1.3.106"}}, base_asset=Asset("1.3.0"))``
        * ``Price(quote="10 GOLD", base="1 USD")``
        * ``Price("10 GOLD", "1 USD")``
        * ``Price(Amount("10 GOLD"), Amount("1 USD"))``
        * ``Price(1.0, "USD/GOLD")``

        Instances of this class can be used in regular mathematical expressions
        (``+-*/%``) such as:

        .. code-block:: python

            >>> from tusc.aio.price import Price
            >>> await Price("0.3314 USD/TUSC") * 2
            0.662600000 USD/TUSC
    """

    def define_classes(self):
        self.amount_class = Amount
        self.asset_class = Asset

    @property
    async def market(self):
        """
        Open the corresponding market.

        :returns: Instance of :class:`tusc.aio.market.Market` for the
                  corresponding pair of assets.
        """
        from .market import Market

        return await Market(
            base=self["base"]["asset"],
            quote=self["quote"]["asset"],
            blockchain_instance=self.blockchain,
        )


class Order(Price):
    """
    This class inherits :class:`tusc.aio.price.Price` but has the ``base`` and
    ``quote`` Amounts not only be used to represent the price (as a ratio of base and
    quote) but instead has those amounts represent the amounts of an actual order!

    :param tusc.aio.tusc.TUSC blockchain_instance: TUSC instance

    .. note::

            If an order is marked as deleted, it will carry the
            'deleted' key which is set to ``True`` and all other
            data be ``None``.
    """

    async def __init__(self, *args, **kwargs):
        # This class does not have @BlockchainInstance.inject because of MRO, so we need
        # to init BlockchainInstance manually! Fixes
        # https://github.com/tusc/python-tusc/issues/234
        BlockchainInstance.__init__(self, **kwargs)

        if len(args) == 1 and isinstance(args[0], str):
            """Load from id."""
            result = await self.blockchain.rpc.get_objects([args[0]])
            order = result[0]
            if order:
                await Price.__init__(
                    self, order["sell_price"], blockchain_instance=self.blockchain
                )
                self.update(order)
                self["deleted"] = False
            else:
                self["id"] = args[0]
                self["deleted"] = True
                self["quote"] = None
                self["base"] = None
                self["price"] = None
                self["seller"] = None
        elif len(args) == 1 and isinstance(args[0], dict) and "sell_price" in args[0]:
            """Load from object 1.7.xxx."""
            # Take all the arguments with us
            self.update(args[0])
            await Price.__init__(
                self, args[0]["sell_price"], blockchain_instance=self.blockchain
            )

        elif (
            len(args) == 1
            and isinstance(args[0], dict)
            and "min_to_receive" in args[0]
            and "amount_to_sell" in args[0]
        ):
            """Load from an operation."""
            # Take all the arguments with us
            self.update(args[0])
            await Price.__init__(
                self,
                await Amount(
                    args[0]["min_to_receive"], blockchain_instance=self.blockchain
                ),
                await Amount(
                    args[0]["amount_to_sell"], blockchain_instance=self.blockchain
                ),
            )
        else:
            # Try load Order as Price
            await Price.__init__(self, *args, **kwargs)

        if "for_sale" in self:
            self["for_sale"] = await Amount(
                {"amount": self["for_sale"], "asset_id": self["base"]["asset"]["id"]},
                blockchain_instance=self.blockchain,
            )

    def __repr__(self):
        """Asyncio version uses simplified mechanics to display details."""
        if "deleted" in self and self["deleted"]:
            return "deleted order %s" % self["id"]
        else:
            t = ""
            if "time" in self and self["time"]:
                t += "(%s) " % self["time"]
            if "type" in self and self["type"]:
                t += "%s " % str(self["type"])
            if "for_sale" in self and self["for_sale"]:
                t += "{} {} for {} ".format(
                    float(self["for_sale"]) / self["price"],
                    self["quote"]["asset"]["symbol"],
                    str(self["for_sale"]),
                )
            elif "amount_to_sell" in self:
                t += "{} for {} ".format(self["amount_to_sell"], self["min_to_receive"])
            elif "quote" in self and "base" in self:
                t += "{} for {} ".format(self["quote"], self["base"])
            return t + "@ " + Price.__repr__(self)

    __str__ = __repr__


class FilledOrder(Price):
    """
    This class inherits :class:`tusc.aio.price.Price` but has the ``base`` and
    ``quote`` Amounts not only be used to represent the price (as a ratio of base and
    quote) but instead has those amounts represent the amounts of an actually filled
    order!

    :param tusc.aio.tusc.TUSC blockchain_instance: TUSC instance

    .. note:: Instances of this class come with an additional ``time`` key
              that shows when the order has been filled!
    """

    async def copy(self):
        return await self.__class__(
            self.order, base=await self["base"].copy(), quote=await self["quote"].copy()
        )

    async def __init__(self, order, **kwargs):
        self.order = order

        if isinstance(order, dict) and "price" in order:
            await Price.__init__(
                self,
                order.get("price"),
                base=kwargs.get("base"),
                quote=kwargs.get("quote"),
            )
            self.update(order)
            self["time"] = formatTimeString(order["date"])

        elif isinstance(order, dict):
            # filled orders from account history
            if "op" in order:
                if isinstance(order["op"], (list, set)):
                    order = order["op"][1]
                elif isinstance(order["op"], dict):
                    order = order["op"]

            base_asset = kwargs.get("base_asset", order["receives"]["asset_id"])
            await Price.__init__(self, order, base_asset=base_asset)

            # To be on the save side, store the entire order object in this
            # dict as well
            self.update(order)

            # Post-Process some additional stuff
            if "time" in order:
                self["time"] = formatTimeString(order["time"])
            if "account_id" in order:
                self["account_id"] = order["account_id"]

        else:
            raise ValueError("Couldn't parse 'Price'.")

    def __repr__(self):
        t = ""
        if "time" in self and self["time"]:
            t += "(%s) " % self["time"]
        if "type" in self and self["type"]:
            t += "%s " % str(self["type"])
        if "quote" in self and self["quote"]:
            t += "%s " % str(self["quote"])
        if "base" in self and self["base"]:
            t += "for %s " % str(self["base"])
        return t + "@ " + Price.__repr__(self)

    __str__ = __repr__


class UpdateCallOrder(Price):
    """This class inherits :class:`tusc.price.Price` but has the ``base``
    and ``quote`` Amounts not only be used to represent the **call
    price** (as a ratio of base and quote).

    :param tusc.aio.tusc.TUSC blockchain_instance: TUSC instance
    """

    async def __init__(self, call, **kwargs):

        BlockchainInstance.__init__(self, **kwargs)

        if isinstance(call, dict) and "call_price" in call:
            await Price.__init__(
                self,
                call.get("call_price"),
                base=call["call_price"].get("base"),
                quote=call["call_price"].get("quote"),
            )

        else:
            raise ValueError("Couldn't parse 'Call'.")

    def __repr__(self):
        t = "Margin Call: "
        if "quote" in self and self["quote"]:
            t += "%s " % str(self["quote"])
        if "base" in self and self["base"]:
            t += "%s " % str(self["base"])
        return t + "@ " + Price.__repr__(self)

    __str__ = __repr__


@asyncinit
@BlockchainInstance.inject
class PriceFeed(dict):
    """
    This class is used to represent a price feed consisting of.

    * a witness,
    * a symbol,
    * a core exchange rate,
    * the maintenance collateral ratio,
    * the max short squeeze ratio,
    * a settlement price, and
    * a date

    :param tusc.aio.tusc.TUSC blockchain_instance: TUSC instance
    """

    async def __init__(self, feed, **kwargs):

        if len(feed) == 2:
            dict.__init__(
                self,
                {
                    "producer": await Account(
                        feed[0], lazy=True, blockchain_instance=self.blockchain
                    ),
                    "date": parse_time(feed[1][0]),
                    "maintenance_collateral_ratio": feed[1][1][
                        "maintenance_collateral_ratio"
                    ],
                    "maximum_short_squeeze_ratio": feed[1][1][
                        "maximum_short_squeeze_ratio"
                    ],
                    "settlement_price": await Price(
                        feed[1][1]["settlement_price"],
                        blockchain_instance=self.blockchain,
                    ),
                    "core_exchange_rate": await Price(
                        feed[1][1]["core_exchange_rate"],
                        blockchain_instance=self.blockchain,
                    ),
                },
            )
        else:
            dict.__init__(
                self,
                {
                    "maintenance_collateral_ratio": feed[
                        "maintenance_collateral_ratio"
                    ],
                    "maximum_short_squeeze_ratio": feed["maximum_short_squeeze_ratio"],
                    "settlement_price": await Price(
                        feed["settlement_price"], blockchain_instance=self.blockchain
                    ),
                    "core_exchange_rate": await Price(
                        feed["core_exchange_rate"], blockchain_instance=self.blockchain
                    ),
                },
            )
