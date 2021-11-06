import json
import logging
import os
import requests
import hashlib

def open_json(path):
    if path:
        try:
            tables = json.load(open(path))
        except FileNotFoundError:
            print(
                '-- WARNING: User ' + path + 'file failed to load.\n')
        else:
            for key, value in tables.items():
                tables[key] = value
        return tables
    else:
        logging.warning('-- WARNING: User' + path + 'was not found.\n')

data = os.listdir('data')

initial = data[:4]
update = data[5:7]
update_second = data[8:]

# register node
d = {"nodes": ["http://0.0.0.0:5000"]}
reg_response = requests.post("http://0.0.0.0:5000/nodes/register", data=json.dumps(d))
print(reg_response)

# mine genesis block
mine_response = requests.get("http://0.0.0.0:5000/mine")
print(mine_response)

# add script blocks
for i in initial:
    d = open_json(f'data/{i}')
    add_response = requests.post("http://0.0.0.0:5000/transactions/new", data=json.dumps(d))
    print(add_response)
    mine_response = requests.get("http://0.0.0.0:5000/mine")
    print(mine_response)

    chain_response = requests.get("http://0.0.0.0:5000/chain")

# register second node
d = {"nodes": ["http://0.0.0.0:5001"]}
reg_response = requests.post("http://0.0.0.0:5000/nodes/register", data=json.dumps(d))
print(reg_response)

d = {"nodes": ["http://0.0.0.0:5000"]}
reg_response = requests.post("http://0.0.0.0:5001/nodes/register", data=json.dumps(d))
print(reg_response)

d = {"nodes": ["http://0.0.0.0:5001"]}
reg_response = requests.post("http://0.0.0.0:5001/nodes/register", data=json.dumps(d))
print(reg_response)

# resolve conflicts
resolve_response = requests.get("http://0.0.0.0:5001/nodes/resolve")
print(resolve_response)

# validation
print('\n ------ Test the proofs and hashes ------- \n')
for i in range(1, len(json.loads(chain_response.text).get('chain'))):
    print(f'Test block {i} proof: \n')
    previous_hash = json.loads(chain_response.text).get('chain')[i].get('previous_hash')
    proof = json.loads(chain_response.text).get('chain')[i].get('proof')
    last_proof = json.loads(chain_response.text).get('chain')[i-1].get('proof')

    string = f'{last_proof}{proof}{previous_hash}'.encode()
    hashed = hashlib.sha256(string).hexdigest()
    print(f'Test pass: {hashed[0:4] == "0000"}. Val: {hashed}\n')
    print('-----------------')

    print(f'Test block {i} hash" \n')
    block = json.dumps(json.loads(chain_response.text).get('chain')[i-1]).encode()
    prev_block_hash = hashlib.sha3_256(block).hexdigest()
    prev_hash = json.loads(chain_response.text).get('chain')[i].get('previous_hash')
    print(f'Test pass: {previous_hash == prev_block_hash}. Val: {previous_hash}. Comp to: {prev_block_hash}\n')
    print('-----------------')

    # check the hashes


# resolve conflicts

# add updated to second node

# resolve conflicts