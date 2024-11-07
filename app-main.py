from functools import wraps
import logging
import sys
import threading
from flask import Flask, request, jsonify, send_from_directory
from eth_account import Account
import json
import os
from eth_account.messages import encode_defunct

from signals_engine import add_user_exchange_list, back_test, background_task, delete_user_exchange_list, get_user_exchange_list, get_user_exchange_log_by_id

app = Flask("app-main", static_folder='ptn-trading-ui/browser')

# Remove any existing handlers from the Flask app's logger
app.logger.handlers.clear()

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Hardcoded Ethereum address split by comma
HARDCODED_ADDRESS_LIST = [ a.lower() for a in os.environ.get("HARDCODED_ADDRESS",\
                                   "0xe0a5cfa76Fde7Df6b4159dF6DCC2c309f9b3d5E1,0x1b53aBebFA996203feF4d5EBa3c79E7bf63177B0") \
                                    .split(",")]   # Replace with the actual address
HARDCODED_MESSAGE= "Authentication Message"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            signature = request.headers.get("Authorization","")
            if len(signature) == 0:
                return jsonify({"message": "Authorization is missing"}), 401

            # Recover the address from the signature
            recovered_address = Account.recover_message(
                encode_defunct(text=HARDCODED_MESSAGE),
                signature=signature
            )

            app.logger.info(f"verification: recovered_address: {recovered_address}")
            if recovered_address.lower() not in HARDCODED_ADDRESS_LIST:
                return jsonify({"message": "Invalid signature"}), 401
        except Exception as e:
            logging.error(e)
            return jsonify({"error": str(e)}), 500

        return f(*args, **kwargs)
    return decorated

@app.route('/api/verify-signature', methods=['POST'])
@token_required
def verify_signature():
     return jsonify({"ok": True}), 200

@app.route('/api/back-test', methods=['POST'])
@token_required
def api_back_test():
    data = request.json
    text = back_test(data.get('trade_pair'), data.get('miner'), 
                     float(data.get('asset1')),
                     float(data.get('asset2')),
                     )
    return jsonify({"text": text}), 200

@app.route('/api/add-pair', methods=['POST'])
@token_required
def add_pair():
    data = request.json
    text = add_user_exchange_list(data.get('exchange'),
                                  data.get('trade_pair'), data.get('miner'), 
                     float(data.get('asset1')),
                     float(data.get('asset2')),
                     data.get('binance_api_key'),
                     data.get('binance_secret_key'),
                     )
    return jsonify({"ok": True}), 200

@app.route('/api/delete-pair', methods=['POST'])
@token_required
def delete_pair():
    data = request.json
    delete_user_exchange_list(data.get('id'))
    return jsonify({"ok": True}), 200

@app.route('/api/pair-list', methods=['GET'])
@token_required
def pair_list():
    d = get_user_exchange_list()
    return jsonify(d), 200

@app.route('/api/trace', methods=['POST'])
@token_required
def pair_logs():
    data = request.json
    d = get_user_exchange_log_by_id(data.get('id'))
    return jsonify(d), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Start background thread
    background_thread = threading.Thread(target=background_task, daemon=True)
    background_thread.start()
    app.run(host='0.0.0.0', port=8080, debug=False)


