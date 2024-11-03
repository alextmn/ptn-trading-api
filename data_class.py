from dataclasses import dataclass, field
from typing import List, Optional

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
    
import json
# Load JSON data from a file and parse it to the Root dataclass
def load_json_to_dataclass(file_path: str) -> List[AccountData]:
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    root_data = [ AccountData(**value) for _, value in json_data.items()]
    return root_data

file_path = 'miner_positions\\miner_positions_.json'  # Path to your JSON file
#file_path = "1.json"
parsed_data = load_json_to_dataclass(file_path)

# Print parsed data as a dictionary for verification
print(len(parsed_data))