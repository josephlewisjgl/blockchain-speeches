from uuid import uuid4
from flask import Flask, jsonify, request

from chain import Blockchain

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine ():
    """
    Route the mining function
    :return:
    """

    # set the block
    last_block = blockchain.last_block
    last_proof = last_block['proof']

    # add a proof
    proof = blockchain.proof_of_work(last_proof, last_block)

    # add all new transactions to the new block
    blockchain.new_transactions(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    # set the hash of the block
    previous_hash = blockchain.hash(last_block)

    # set up a new block with the proof of work and the hash
    block = blockchain.new_block(proof, previous_hash)

    # build response
    response = {
        'message': 'New block forged',
        'index': block['index'],
        'transaction': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Add transactions
    :return:
    """

    # read in json with transaction data
    values = request.get_json()

    # check request contains required data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # add the transaction under a new index/the same new index
    index = blockchain.new_transactions(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Display a chain
    :return:
    """

    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    Register a new node
    :return:
    """

    # read in values for new node
    values = request.get_json()

    nodes = values.get('nodes')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def conflicts():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }

    else:
        response = {
            'message': 'Our chain is authoritative',
            'new_chain': blockchain.chain
        }

    return jsonify(response), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)