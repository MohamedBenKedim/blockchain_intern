from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import base64
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import Manifacturer


class Blockchain:

    def __init__(self):
        
        self.transactions = []
        self.chain = []
        self.nodes = set()
        self.node_id ="Man-ID1100"
        self.create_block('00')


    def register_node(self, node_url):
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def verify_transaction_signature(self, sender_address, signature, transaction):
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))

    def submit_transaction(self, sender_address, recipient_address, value,privacy, signature):
        transaction = OrderedDict({'sender_address': sender_address, 
                                    'recipient_address': recipient_address,
                                    'Product_UniCode': value,
                                    'hashed_privacy': privacy})
        transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
        if transaction_verification:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            return False


    def create_block(self, previous_hash):
        """
        Add a block of transactions to the blockchain
        """
        block = {'block_number': len(self.chain) + 1,
                'timestamp': time(),
                'transactions': self.transactions,
                'previous_hash': previous_hash}

        # Reset the current list of transactions
        self.transactions = []

        self.chain.append(block)
        return block


    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()

    def get_component(self,transaction):
        with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\Manifacturer_node\\nodes_listing.json', 'r') as json_file:
            data = json.load(json_file)
        for component_data in data:
            if transaction["sender_address"]==component_data["public_adr"]:
                return str(component_data)

    def proof_of_privacy(self,transaction): 
        private_data = str(base64.b64decode(transaction["hashed_privacy"][2:]))
        component = self.get_component(transaction)
        if private_data == component:
            return True
    
    def valid_proof(self):
        for transaction in self.transactions:
            print(transaction)
            if not self.proof_of_privacy(transaction) :
                return False
        return True

    def valid_chain(self, chain):
        """
        check if a bockchain is valid
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            transactions = block['transactions']
            # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
            transaction_elements = ['sender_address', 'recipient_address', 'Product_UniCode']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]

            '''if not self.valid_proof(transactions):
                return False'''

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            print('http://' + node + '/chain')
            response = requests.get('http://' + node + '/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

# Instantiate the Node
app = Flask(__name__)
CORS(app)

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/configure')
def configure():
    return render_template('./configure.html')

    
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    print(values)
    # Check that the required fields are in the POST'ed data
    required = ['sender_address', 'recipient_address', 'Product_UniCode', 'signature','hashed_privacy']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    transaction_result = blockchain.submit_transaction(values['sender_address'], values['recipient_address'], values['Product_UniCode'],values['hashed_privacy'] ,values['signature'])
    print(values['Product_UniCode'])
    if transaction_result == False:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to Block '+ str(transaction_result)}
        return jsonify(response), 201

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #Get transactions from transactions pool
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    transactions = blockchain.transactions
    last_block = blockchain.chain[-1]
    for trans in transactions:
        if blockchain.proof_of_privacy(trans) :
            print(trans)
            sender_adress = trans["transaction"]["sender_address"]
            recipient_address=trans["transaction"]["recipient_address"]
            Product_UniCode=trans["transaction"]["Product_UniCode"]
            blockchain.submit_transaction(sender_address=sender_adress, recipient_address=blockchain.node_id, value=Product_UniCode, signature="") 
        # Forge the new Block by adding it to the chain'''
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(previous_hash)

    response = {
            'message': "New Block Forged",
            'block_number': block['block_number'],
            'transactions': block['transactions'],
            'previous_hash': block['previous_hash'],
        }
    return jsonify(response), 200

@app.route('/nodeslistingjson')
def serve_json():
    try:
        with open('nodes_lsiting.json', 'r') as json_file:
            data = json.load(json_file)
        return data, 200
    except FileNotFoundError:
        return "JSON file not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    #Running the flask app on the node correspending to the main ID in the 
    #Adding all the nodes to the set of nodes
    with open('c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\Manifacturer_node\\nodes_listing.json', 'r') as json_file:
        data = json.load(json_file)
    for component_data in data:
        node_ip = component_data["node_ip"]
        node_port = component_data["node_port"]
        if blockchain.node_id==component_data["node_ID"]:
            node_ip_id = node_ip
            node_port_id = node_port
        else :
             blockchain.register_node(node_ip+":"+node_port)

    app.run(host=node_ip_id, port=int(node_port_id))