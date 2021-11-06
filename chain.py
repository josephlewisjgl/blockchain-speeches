import hashlib
from time import time
import json
from urllib.parse import urlparse
import requests


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.new_block(previous_hash=1, proof=100)

        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        """
        Set up a new block that stores added transactions before the block was mined
        :param proof: proof from PoW algorithm
        :param previous_hash: hash of previous block in chain
        :return:
        """

        # block to add containing an index starting at one, unix timestamp, transactions, proof and the hash of the prev
        # block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # empty the current transactions
        self.current_transactions = []

        # append new block to chain
        self.chain.append(block)

        return block

    def new_transactions(self, se_ep, script):
        """
        Appending new transactions to add to the new block
        :param se_ep: sender string
        :param script: recipient string
        :return:
        """

        self.current_transactions.append({
            'se_ep': se_ep,
            'script': script,
        })

        # return the block to append to (a new index)
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Create a sha-256 hash of a block
        :param block:
        :return:
        """
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha3_256(block_string).hexdigest()


    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof, last_block):
        """
        Trial and error each number for proof until proven
        :param last_proof: proof of last block
        :return:
        """

        proof = 0
        last_hash = self.hash(last_block)
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Combine last proof and proof in a way that the sha-256 hash of the combination has four 0s at the start
        :param last_proof: proof of last block
        :param proof: proof to test
        :return:
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        """
        Check a blockchain is valid
        :param chain: chain to check
        :return:
        """

        # last block is the oldest on the chain
        last_block = chain[0]
        current_index = 1

        # start at block one and loop to the end of the chain
        while current_index < len(chain):

            # block to check
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n___________\n')
            last_block_hash = self.hash(last_block)

            # check the hash in the block and check by hashing the block they should be the same
            if block['previous_hash'] != last_block_hash:
                return False

            # check the proof is valid on the block
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            # update all the block items
            last_block = block
            current_index += 1

        return True

    def register_node(self, address):
        """
        Register a node on a different machine/port
        :param address: address to register
        :return:
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def resolve_conflicts(self):
        """
        Resolve conflicts between nodes and overwrite the outdated one if the new one has a valid chain
        :return:
        """

        # get a list of nodes
        neighbours = self.nodes
        new_chain = None

        # check chain length
        max_length = len(self.chain)

        # get the chain from the new node for each new node
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            # if valid response
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # if the new chain is longer and is valid
                if length > max_length and self.valid_chain(chain):
                    # set a new max length and chain to check against the other chains
                    max_length = length
                    new_chain = chain

        # if there is a new chain update the chain
        if new_chain:
            self.chain = new_chain
            return True

        return False
