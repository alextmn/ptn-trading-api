import io
import time
import json
import os
from typing import List, Optional
import requests
from data_class import Order, load_json_to_dataclass, load_json_to_dataclass_from_dict, orders_all, orders_by_pair, to_date
from similated_exchange import SimulatedExchange
from utils.logger_util import LoggerUtil
from utils.order_util import OrderUtil
from utils.time_util import TimeUtil
import threading
import logging

logger = logging.getLogger("app-main.signals")

API_KEY = os.environ.get("API_KEY", "req_3ZPrqqnZuuNDyPTf7DTcWGGo")
URL = os.environ.get("MINER_POSITIONS_ENDPOINT_URL", "https://request.wildsage.io/miner-positions?tier=0")
RUN_SLEEP_TIME = 60

FILE_PATH = 'miner_positions.json'

data_lock = threading.Lock()

user_exchange_list = []

##############################
def get_last_line(text):
    lines = text.strip().splitlines()
    return lines[-1] if lines else ""

def add_user_exchange_list(exchange:str, tarde_pair:str, miner:str,  
						   asset1:float, asset2:float, binance_api_key: str, binance_secret_key: str):
  global user_exchange_list
  with data_lock:
	  if exchange == "simulated":
  			user_exchange_list.append(SimulatedExchange(miner, tarde_pair, asset1, asset2))

def delete_user_exchange_list(i: int):
	global user_exchange_list
	with data_lock:
		del user_exchange_list[i]

#############################

def get_user_exchange_list() -> dict:
  global user_exchange_list
  r = [{ "id":i, "trading_pair":e.trading_pair, 
		"miner": e.miner, "last":get_last_line(e.trace()) } for i, e in  enumerate(user_exchange_list)]
  
  return r

def get_user_exchange_log_by_id(id: int) -> dict:
  global user_exchange_list
  with data_lock:
    it =  user_exchange_list[id]
  return { "id":id, "trading_pair":it.trading_pair, 
		"miner": it.miner, "trace":it.trace() }
  

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
		logger.info("GET request was successful.")
		return response.json()
	else:
		logger.info(response.__dict__)
		logger.info("GET request failed with status code: " + str(response.status_code))

		return None

def write_json_file(data: dict, file_path: str = "miner_positions.json") -> None:
    """Writes a dictionary to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)
    logger.info(f"Data successfully written to '{file_path}'.")
    time.sleep(1) 
        
def on_new_orders(orders: List[Order]):
	logger.info (f"new orders: {len(orders)}")
	for o in orders:
		for e in user_exchange_list:
			if o.muid ==  e.miner:
				e.trade(o)

def background_task():
	EXISTING_ORDERS_UUID = set([])
	while True:
		# Simulate periodic data processing
		new_data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
		logger.info(f"Background task updated shared data: {new_data}")
		response = get_new_orders()
		if response is not None:
			with data_lock:
				write_json_file(response)
			
			# get all the orders
			parsed_data = load_json_to_dataclass_from_dict(response)
			orders = orders_all(parsed_data)
			uuid_set = set([o.order_uuid for o in orders])
			logger.info (f"api orders: {len(uuid_set)}, total: {len(EXISTING_ORDERS_UUID)}")
			# set intersection diff
			if len(EXISTING_ORDERS_UUID) > 0:
				new_uuid_set = EXISTING_ORDERS_UUID - uuid_set
				on_new_orders([o for o in orders if o.order_uuid in new_uuid_set])

			EXISTING_ORDERS_UUID.update(uuid_set)

		time.sleep(RUN_SLEEP_TIME)  # Run every 60 seconds
      

def back_test(trade_pair: str = "BTCUSD", 
			  miner: str="5Exax1W9RiNbARDejrthf4SK1FQ2u9DPUhCq9jm58gUysTy4", 
			  asset1: float=0.0146, asset2: float=1000) -> str:
	
	with data_lock:
		parsed_data = load_json_to_dataclass(FILE_PATH)

	exchange = SimulatedExchange(miner, trade_pair,asset1, asset2 )
	orders = orders_by_pair(parsed_data, miner, set([trade_pair]))
	
	for o in orders:
		exchange.trade(o)
	return f"trades: {len(orders)}\n{exchange.trace()}"

