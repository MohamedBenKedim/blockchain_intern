from collections import OrderedDict
from pyzbar.pyzbar import decode
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import json
import base64
import numpy as np

from flask import Flask, jsonify, request, render_template , Response

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, Product_UniCode):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.Product_UniCode = Product_UniCode

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'Product_UniCode': self.Product_UniCode,
                            'hashed_privacy':self.get_sender_details_base64()})

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')
    
    def get_sender_details_base64(self):
     with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\DeliveryService\\nodes_listing.json', 'r') as json_file:
        data = json.load(json_file)
     for component_data in data:
        json_string = json.dumps(component_data)
        json_bytes = json_string.encode('utf-8')
        if self.sender_address==component_data["public_adr"]:
            return str(base64.b64encode(json_bytes))


app = Flask(__name__)


with open("c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\DeliveryClient\\private_data.json") as f:
    data_json = json.load(f)

@app.route('/')
def index():
	return render_template('./index.html')

@app.route('/verify/tracability')
def verify_tracability():
	return render_template('./verify_tracability.html')

@app.route('/view/transactions')
def view_transactions():
	return render_template('./view_transactions.html')



@app.route('/make/privatedata')
def get_json():
    with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\DeliveryClient\\private_data.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/make/nodeslist')
def get_node_list():
    with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\DeliveryService\\nodes_listing.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/make/transaction")
def scan_qr_code():
    return render_template("make_transaction.html")

@app.route('/make/camera_feed')
def camera_feed():
    return render_template('camera_feed.html')

@app.route('/make/get_qr_code', methods=['POST'])
def get_qr_code():
    global code
    json_data = request.get_json()
    code = json_data["code"]
    with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\DeliveryClient\\templates\\qr_temp.json', 'w') as json_file:
            json.dump({'code': code}, json_file)
    return jsonify({'message': 'Data saved successfully'}), 200


@app.route('/wallet/new', methods=['GET'])
def new_wallet():
	random_gen = Crypto.Random.new().read
	private_key = RSA.generate(1024, random_gen)
	public_key = private_key.publickey()
	response = {
		'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
		'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
	}
	return jsonify(response), 200

@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
	sender_address = data_json["public_key"]
	sender_private_key =data_json["private_key"]
	recipient_address = request.form['recipient_address']
	Product_UniCode = request.form['Product_UniCode']
    
	transaction = Transaction(sender_address, sender_private_key, recipient_address, Product_UniCode)
   
	response = {'transaction': transaction.to_dict(), 'signature': transaction.sign_transaction()}

	return jsonify(response), 200

id="STR-ID2780"

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\DeliveryService\\nodes_listing.json', 'r') as json_file:
        data = json.load(json_file)
    for component_data in data:
        if id==component_data["node_ID"]:
           node_ip = component_data["node_ip"]
           node_port = component_data["node_cl_port"]

    app.run(host=node_ip, port=int(node_port))
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)