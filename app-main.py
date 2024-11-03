from flask import Flask, request, jsonify
from eth_account import Account
import json
import os
from eth_account.messages import encode_defunct

app = Flask(__name__)

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
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
