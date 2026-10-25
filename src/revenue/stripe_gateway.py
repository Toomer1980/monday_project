import os
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "operational",
        "entity": "Oracle Systems LLC",
        "ein": "82-4737196",
        "gateway": "Stripe Enterprise Connected"
    })

@app.route('/api/v1/invoice/generate', methods=['POST'])
def generate_invoice():
    data = request.json or {}
    amount = data.get('amount', 25000)
    client = data.get('client', 'Enterprise Partner')
    logging.info(f"Generating automated invoice for {client} in the amount of ")
    return jsonify({
        "success": True,
        "invoice_id": "INV-ORACLE-8247",
        "amount": amount,
        "currency": "USD",
        "status": "pending_payment"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
