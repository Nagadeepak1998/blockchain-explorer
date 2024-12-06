from flask import Flask, jsonify, request, render_template
import hashlib
import json
from time import time
import os

app = Flask(__name__)

class Blockchain:
    def __init__(self, chain_file='blockchain.json'):
        """
        Initialize the blockchain.
        :param chain_file: The filename where the blockchain is stored.
        """
        self.chain = []
        self.current_transactions = []
        self.chain_file = chain_file

        # Load existing blockchain if available, else create genesis block
        if os.path.exists(self.chain_file):
            self.load_chain()
        else:
            self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block and add it to the chain.
        :param proof: The proof given by the Proof of Work algorithm.
        :param previous_hash: Hash of previous block.
        :return: New block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        self.save_chain()
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block.
        :param sender: Address of the Sender.
        :param recipient: Address of the Recipient.
        :param amount: Amount.
        :return: The index of the Block that will hold this transaction.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block.
        :param block: Block.
        :return: Hash string.
        """
        # Ensure the dictionary is ordered to have consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """Returns the last Block in the chain."""
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: Previous proof.
        :return: New proof.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof.
        :param last_proof: Previous proof.
        :param proof: Current proof.
        :return: True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def save_chain(self):
        """
        Save the blockchain to a JSON file.
        """
        with open(self.chain_file, 'w') as f:
            json.dump(self.chain, f, indent=4)

    def load_chain(self):
        """
        Load the blockchain from a JSON file.
        """
        with open(self.chain_file, 'r') as f:
            self.chain = json.load(f)

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def index():
    """
    Serve the frontend interface.
    """
    return render_template('index.html')

@app.route('/mine', methods=['GET'])
def mine():
    """
    Endpoint to mine a new block.
    """
    # Run the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Reward the miner for finding the proof (sender "0")
    blockchain.new_transaction(
        sender="0",
        recipient="c070a4ae77fa41928efadd9a12fc2ed4",
        amount=1,
    )

    # Forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "index": block['index'],
        "message": "New Block Forged",
        "previous_hash": block['previous_hash'],
        "proof": block['proof'],
        "transactions": block['transactions'],
    }

    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Endpoint to return the full blockchain.
    """
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Endpoint to add a new transaction to the blockchain.
    """
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

# Remove or comment out the following lines when deploying with Gunicorn
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
