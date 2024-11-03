from utils.logger_util import LoggerUtil
from utils.order_util import OrderUtil
from utils.time_util import TimeUtil


API_KEY = ""
RUN_SLEEP_TIME = 60



if __name__ == "__main__":
	logger = LoggerUtil.init_logger()
	while True:
		logger.info("starting another check for new orders...")
		new_orders = OrderUtil.get_new_orders(API_KEY, "", logger)
		if new_orders is not None:
			print("ORDER LEN =>", len(new_orders))
			for new_order in new_orders:
				print(new_order)
				#send_new_miner_order(new_order, logger)
		TimeUtil.sleeper(RUN_SLEEP_TIME, "completed request", logger)