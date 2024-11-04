from dataclasses import dataclass, field
from datetime import datetime
import os
from typing import List, Optional, Set
import json

@dataclass
class PriceSource:
    source: str
    timespan_ms: int
    open: float
    close: float
    vwap: Optional[float]
    high: float
    low: float
    start_ms: int
    websocket: bool
    lag_ms: int
    volume: Optional[float]

@dataclass
class Order:
    order_type: str
    leverage: float
    price: float
    processed_ms: int
    order_uuid: str
    price_sources: List[PriceSource]
    src: int
    trade_pair: List[str] | None = None
    muid: str | None = None
    position_uuid: str | None  = None
    position_type: str | None  = None
    net_leverage: str | None  = None
    rank: int | None  = None

@dataclass
class Position:
    miner_hotkey: str
    position_uuid: str
    open_ms: int
    trade_pair: List[float]
    orders: List[Order]
    current_return: float
    close_ms: int
    return_at_close: float
    net_leverage: int
    average_entry_price: float
    position_type: str
    is_closed_position: bool

@dataclass
class AccountData:
    positions: List[Position]
    thirty_day_returns: float
    all_time_returns: float
    n_positions: int
    percentage_profitable: float
    tier: int

def parse_price_source(data: dict) -> PriceSource:
    return PriceSource(**data)

def parse_order(data: dict, p: Position) -> Order:
    r = Order(**data)
    r.price_sources = [parse_price_source(ps) for ps in data['price_sources']]
    r.trade_pair = r.trade_pair or p.trade_pair
    return r

def parse_position(data: dict) -> Position:
    r = Position(**data)
    r.orders = [parse_order(order, r) for order in data['orders']]
    return r

def parse_account_data(data: dict) -> AccountData:
    r = AccountData(**data)
    r.positions = [parse_position(pos) for pos in data['positions']]
    return r 

def load_json_to_dataclass(file_path: str) -> List[AccountData]:
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    root_data = [parse_account_data(account) for _, account in json_data.items()]
    return root_data



def miner_hotkeys_set(parsed_data) -> List[str]:
    miner_hotkeys = [ [p.miner_hotkey for p in a.positions] for a in parsed_data]
    return set(flatten(miner_hotkeys))

def trade_pair_set(parsed_data) -> List[str]:
    trade_pair = [ [p.trade_pair[0] for p in a.positions] for a in parsed_data]
    return set(flatten(trade_pair))

##################################
def flatten(xss):
    return [x for xs in xss for x in xs]

def to_date(order:Order):
    return datetime.fromtimestamp(order.processed_ms / 1000)

def orders_by_pair(parsed_data, miner: str, trade_pairs_set: Set[str]) -> List[Order]:
    positions = flatten([ a.positions for a in parsed_data if miner in set([p.miner_hotkey for p in a.positions])])
    orders = flatten([p.orders for p in positions])
    orders_filtered = [o for o in orders if (o.trade_pair)[0] in trade_pairs_set]
    return orders_filtered