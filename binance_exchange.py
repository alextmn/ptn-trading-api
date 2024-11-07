import io
from binance.client import Client
from data_class import Order, to_date
from similated_exchange import Exchange  # Assuming Order and to_date are defined elsewhere

class BinanceExchange(Exchange):

    def __init__(self, api_key: str, api_secret: str, trading_pair: str):
        super().__init__()
        self.client = Client(api_key, api_secret)
        self.trading_pair = trading_pair
        self.buffer.write("Date, Price, OrderType, Leverage, asset1/asset2, value, balance1/balance2\n")

    def balances(self):
        """TODO: fix it: Retrieve balances for the trading pair's assets on Binance."""

        asset1, asset2 = self.trading_pair.split("/")
        balance_asset1 = float(self.client.get_asset_balance(asset=asset1)['free'])
        balance_asset2 = float(self.client.get_asset_balance(asset=asset2)['free'])
        return balance_asset1, balance_asset2

    def buy(self, asset1: float, asset2: float, price: float, prefix: str):
        """Execute a buy order on Binance."""
        try:
            order = self.client.order_market_buy(
                symbol=self.trading_pair,
                quantity=round(asset1, 6)  # Binance accepts rounded quantities
            )
            self.buffer.write(
                f"BUY {prefix} +{asset1:.6f}/-{asset2:.1f} value: {self.value(price)} "
                f"assets: {order['executedQty']}/{order['cummulativeQuoteQty']}\n"
            )
        except Exception as e:
            self.buffer.write(f"BUY FAILED {prefix}: {e}\n")

    def sell(self, asset1: float, asset2: float, price: float, prefix: str):
        """Execute a sell order on Binance."""
        try:
            order = self.client.order_market_sell(
                symbol=self.trading_pair,
                quantity=round(asset1, 6)
            )
            self.buffer.write(
                f"SELL {prefix} -{asset1:.6f}/+{asset2:.1f} value: {self.value(price)} "
                f"assets: {order['executedQty']}/{order['cummulativeQuoteQty']}\n"
            )
        except Exception as e:
            self.buffer.write(f"SELL FAILED {prefix}: {e}\n")

    def value(self, price: float):
        """Calculate the current portfolio value in terms of asset2."""
        balance_asset1, balance_asset2 = self.balances()
        return round(balance_asset1 * price + balance_asset2, 2)
