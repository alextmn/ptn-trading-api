import io

import eth_account
from data_class import Order, to_date  # Assuming these are provided by the user
from eth_account.signers.local import LocalAccount
from hyperliquid.info import Info

from similated_exchange import Exchange  # Hypothetical client library for Hyperliquid

MAINNET_API_URL = "https://api.hyperliquid.xyz"
TESTNET_API_URL = "https://api.hyperliquid-testnet.xyz"

class HyperliquidExchange(Exchange):
    def __init__(self, trading_pair:str, secret_key: str, base_url = TESTNET_API_URL):
        super().__init__()
        account: LocalAccount = eth_account.Account.from_key(secret_key)
        self.account = account
        self.address = account.address
        self.info = Info(base_url, False)
        self.exchange = Exchange(account, base_url, account_address= self.address)

        self.trading_pair = trading_pair
        self.asset1_name, self.asset2_name = self.parse_trading_pair(trading_pair)
        self.buffer = io.StringIO()
        self.buffer.write("Date, Price, OrderType, Leverage, asset1/asset2, value, balance1/balance2\n")

    def balances(self):
        balances = self.info.spot_user_state(self.address)["balances"]
        return balances[self.asset1_name], balances[self.asset2_name]

    def buy(self, asset1: float, asset2: float, price: float, prefix: str):
        # Place a buy order on Hyperliquid
        is_buy = True
        order_result = self.exchange.market_open(self.asset1_name, is_buy, asset1, None, 0.01)
        if order_result["status"] == "ok":
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    self.buffer.write(f'BUY Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
                except KeyError:
                    self.buffer.write(f'BUY Error: {status["error"]}')


    def sell(self, asset1: float, asset2: float, price: float, prefix: str):
        # Place a buy order on Hyperliquid
        is_buy = False
        order_result = self.exchange.market_open(self.asset1_name, is_buy, asset1, None, 0.01)
        if order_result["status"] == "ok":
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    self.buffer.write(f'SELL Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
                except KeyError:
                    self.buffer.write(f'SELL Error: {status["error"]}')


    def value(self, price: float):
        balance_asset1, balance_asset2 = self.balances()
        return int(balance_asset1 * price + balance_asset2)
