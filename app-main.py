import logging
import sys
import threading
from flask import Flask, request, jsonify, send_from_directory
from eth_account import Account
import json
import os
from eth_account.messages import encode_defunct

from signals_engine import back_test, background_task

app = Flask("app-main", static_folder='ptn-trading-ui/browser')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Hardcoded Ethereum address to check against
HARDCODED_ADDRESS = os.environ.get("HARDCODED_ADDRESS","0xe0a5cfa76Fde7Df6b4159dF6DCC2c309f9b3d5E1")  # Replace with the actual address
HARDCODED_MESSAGE= "Authentication Message"

@app.route('/api/verify-signature', methods=['POST'])
def verify_signature():
    try:
        data = request.json
        signature = data.get('signature')

        # Recover the address from the signature
        recovered_address = Account.recover_message(
            encode_defunct(text=HARDCODED_MESSAGE),
            signature=signature
        )

        if recovered_address.lower() == HARDCODED_ADDRESS.lower():
            return jsonify({"message": "Signature is valid", "address": recovered_address}), 200
        else:
            return jsonify({"message": "Invalid signature"}), 401
    except Exception as e:
        logging.info(e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/back-test', methods=['POST'])
def api_back_test():
    data = request.json
    text = back_test(data.get('trade_pair'), data.get('miner'), 
                     float(data.get('asset1')),
                     float(data.get('asset2')),
                     )
    return jsonify({"text": text}), 200

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
    app.run(host='0.0.0.0', port=8080, debug=True)
