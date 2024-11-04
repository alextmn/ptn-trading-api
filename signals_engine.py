import io
import time
import json
import os
from typing import Optional
import requests
from data_class import load_json_to_dataclass, orders_by_pair, to_date
from similated_exchange import SimulatedExchange
from utils.logger_util import LoggerUtil
from utils.order_util import OrderUtil
from utils.time_util import TimeUtil
import threading

API_KEY = "req_3ZPrqqnZuuNDyPTf7DTcWGGo"
URL = os.environ.get("MINER_POSITIONS_ENDPOINT_URL", "https://request.wildsage.io/miner-positions?tier=0")
RUN_SLEEP_TIME = 60

data_lock = threading.Lock()

def get_new_orders():
		# Set the headers to specify that the content is in JSON format
	headers = {
		'Content-Type': 'application/json',
		'x-taoshi-consumer-request-key': API_KEY
	}
		# Make the GET request with JSON data
	response = requests.get(OrderUtil.URL, headers=headers)

	# Check if the request was successful (status code 200)
	if response.status_code == 200:
		print("GET request was successful.")
		return response.json()
	else:
		print(response.__dict__)
		print("GET request failed with status code: " + str(response.status_code))

		return None

def write_json_file(data: dict, file_path: str = "miner_positions.json") -> None:
    """Writes a dictionary to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)
    print(f"Data successfully written to '{file_path}'.")
        
def background_task():
	while True:
		# Simulate periodic data processing
		new_data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
		print(f"Background task updated shared data: {new_data}")
		response = get_new_orders()
		with data_lock:
			write_json_file(response)
		time.sleep(RUN_SLEEP_TIME)  # Run every 60 seconds
      

def back_test(trade_pair: str = "BTCUSD", 
			  miner: str="5Exax1W9RiNbARDejrthf4SK1FQ2u9DPUhCq9jm58gUysTy4", 
			  asset1: float=0.0146, asset2: float=1000) -> str:
	
	with data_lock:
		file_path = 'miner_positions.json'  # Path to your JSON file
		parsed_data = load_json_to_dataclass(file_path)

	exchange = SimulatedExchange(trade_pair,asset1, asset2 )
	orders = orders_by_pair(parsed_data, miner, set([trade_pair]))
	buffer = io.StringIO()
	buffer.write(f"trades: {len(orders)}\nDate, Price, OrderType, Leverage, asset1/asset2, value, balance1/balance2\n")
	for o in orders:
		s =  f"{to_date(o)}, {o.price}, {o.order_type}, {o.leverage}"
		exchange.trade(o, s, buffer)
	return buffer.getvalue()

