import io
from data_class import Order, to_date


class SimulatedExchange:
    
    

    def __init__(self, miner:str, trading_pair:str, 
                 initial_balance_asset1 : float,
                 initial_balance_asset2: float):
        self.balance_asset1 = initial_balance_asset1
        self.balance_asset2 = initial_balance_asset2
        
        self.trading_pair = trading_pair
        self.miner = miner
        self.buffer =  io.StringIO()
        self.buffer.write(f"Date, Price, OrderType, Leverage, asset1/asset2, value, balance1/balance2\n")

    def balances(self ):
        return self.balance_asset1, self.balance_asset2
    
    def trade(self, order:Order): 
        if order.order_type not in set(["LONG","SHORT"]):
            return
        balance_asset1, balance_asset2 = self.balances() 

        if order.leverage > 0:
            a2 = min(order.leverage * balance_asset2, balance_asset2)
            a1 = a2 / order.price
        else:
            a1 = min(-order.leverage * balance_asset1, balance_asset1)
            a2 = a1 * order.price
        
        prefix =  f"{to_date(order)}, {order.price}, {order.order_type}, {order.leverage}"
        if a1 > 0 and a2 > 0: 
            if order.order_type=="LONG":
                self.buy(a1,a2,order.price,  prefix)
            elif order.order_type=="SHORT":
                self.sell(a1,a2,order.price,  prefix)
        else:
            self.buffer.write (f"{prefix} balances are not sufficient")
            
    def buy(self, asset1: float, asset2: float, price: float, prefix:str):
        self.balance_asset1 +=asset1
        self.balance_asset2 -=asset2
       
        self.buffer.write(f"BUY {prefix} +{asset1:.6f}/-{asset2:.1f} value: {self.value(price)} assets: {self.balance_asset1:.6f}/{self.balance_asset2:.1f}\n")

    def sell(self, asset1: float, asset2: float, price: float, prefix:str):
        self.balance_asset1 -=asset1
        self.balance_asset2 +=asset2
        self.buffer.write(f"SELL {prefix} +{asset1:.6f}/-{asset2:.1f} value: {self.value(price)} assets: {self.balance_asset1:.6f}/{self.balance_asset2:.1f}\n")

    def value(self, price:float):
        return int(self.balance_asset1 * price + self.balance_asset2)
    
    def trace(self)-> str:
        return self.buffer.getvalue()