"""
This module contains the main program of this project.

:function: get_ui()
:function: get_network()
:function: get_open_transation()
:function: create_keys()
:function: load_keys()
:function: add_transaction()
:function: get_chain()
:function: get_balance()
:function: mine()
:function: add_node()
:function: remove_node(node_url)
:function: get_nodes()
:function: broadcast_transaction()
:function: broadcast_block()
:function: resolve_conflicts()
:main: __main__
"""

# request import is usefull to extract incoming requests from servers
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import BlockChain

webApp = Flask(__name__)
CORS(webApp)


@webApp.route('/', methods=['GET'])
def get_ui():
    """
    This GET function controls the UI of the main program via the '/' route.

    :returns: A command that executes the `node.html` file in `~/ui/node.html`.
    """
    return send_from_directory('ui', 'node.html')


@webApp.route('/network', methods=['GET'])
def get_network():
    """
    This GET function controls the UI of the network of nodes via the '/network'.

    :returns: A command that executes the network.html file in `~/ui/network.html`.
    """
    return send_from_directory('ui', 'network.html')


@webApp.route('/transactions', methods=['GET'])
def get_open_transation():
    """
    This GET function gets the open transactions of the blockchain via the '/transactions' route.

    :var all_transactions list: The list of all transactions of the blockchain.
    :var dict_transactions dict: All open transactions transformed into a dictionnary.
    :returns json: A JSON success response (200) of the dictionnary of all transactions.
    """
    all_transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in all_transactions]
    return jsonify(dict_transactions), 200


@webApp.route('/wallet', methods=['POST'])
def create_keys():
    """
    This POST function creates the keys for the wallet via the '/wallet' route.

    :var blockchain BlockChain: Blockchain associated with the wallet (or the node).
    :var response dict: Contains a failure message if the keys are not saved. Contains the public key, private key and the funds of the wallet if the keys are saved successfully.
    :returns json: A JSON response of 500 if there is an error in the key creation, 201 if it succeeds plus the public and private key.
    """
    wallet.create_keys()
    if wallet.save_keys():
        # TODO: why using a global variable?
        global blockchain  # We must define a global variable blockchain because
        blockchain = BlockChain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed'
        }
        return jsonify(response), 500


@webApp.route('/wallet', methods=['GET'])
def load_keys():
    """
    This GET function loads the keys of a wallet via the '/wallet' route.

    :var blockchain BlockChain: The blockchain of the wallet (or of the node).
    :var response dict: Contains a failure message if the keys are not loaded. Contains the public key, private key and the funds of the wallet if the keys are saved successfully.
    :returns json: A JSON response of 500 if the keys failed loading, 201 if it succeeds plus the public key, the private key and the funds.
    """
    if wallet.load_keys():
        # TODO: why using a global variable?
        global blockchain  # We must define a global variable blockchain because
        blockchain = BlockChain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed'
        }
        return jsonify(response), 500


@webApp.route('/transaction', methods=['POST'])
def add_transaction():
    """
    This POST function manages the addition of new transactions into the blockchain via the '/transaction' route.

    :var response dict: Contains the public key, the amount, the signature, the sender,  and the recipient of the transaction plus the funds of the wallet if adding the transaction is a success, contains an error message if not.
    :var required_fields list: List of the required fields to have (the amount and the recipient) in the received data.
    :var incoming_values dict: The actual incoming values of the transaction to be compared with the required_fields var.
    :var recipient str: The recipient of the transaction.
    :var amount float: The amount of the transaction.
    :var signature str: The signature of the transacion.
    :var success bool: True if the transaction has been added successfully into the blockchain, false if not.
    :returns json: A JSON response of 400 if the public key doesn't exists or if a data is missing is the incoming_values var or if incoming_values is empty or of 500 if the creation of the transaction in the blockchain failed, 201 if the transaction is successfully added.
    """

    # Verification of the data
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    incoming_values = request.get_json()
    if not incoming_values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in incoming_values for field in required_fields):
        response = {
            'message': 'Required data is missing',
        }
        return jsonify(response), 400
    # At this stage, we have proper data
    recipient = incoming_values['recipient']
    amount = incoming_values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.',
        }
        return jsonify(response), 500


@webApp.route('/chain', methods=['GET'])
def get_chain():
    """
    This GET function gets the chain of the blockchain via the '/chain' route.

    :var chain_snapshot: The blockchain of the wallet (or the node).
    :var dictionnary_chain list: The list of all blocks in the blockchain transformed into a dictionnary.
    :returns json: A JSON response of 200 with the dictionnary_chain var.
    """

    chain_snapshot = blockchain.chain
    dictionnary_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dictionnary_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dictionnary_chain), 200


@webApp.route('/balance', methods=['GET'])
def get_balance():
    """
    This GET function gets the balance of the funds of the wallet via the '/balance' route.

    :var balance float: The balance  requested by the wallet (or the node).
    :response dict: 
    :returns json:
    """

    balance = blockchain.get_balance()
    if balance != None:  # If the public key exists than we will return a success message and an error message if not
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        # Return the response jsonify and an OK success code
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500  # Return the response and an error code


@webApp.route('/mine', methods=['POST'])
def mine():
    """
    Function that updates the blockchain with mining a block
    """
    # If there is a conflict to solve then we inform the user
    if blockchain.resolve_conflicts:
        response = {
            'message': 'Resolve conflicts first, block not added.'
        }
        # The 409 means that the user might resolve this conflict by himself
        return jsonify(response), 409
    block = blockchain.mine_block()
    if block != None:  # in case of a success
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        # returns the response and a success code indicating that the request has been fulfilled
        return jsonify(response), 201
    else:  # in case of an error
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None
        }
        # returns the response and a server error code of 500
        return jsonify(response), 500


# POST because we want to add something to the server
@webApp.route('/node', methods=['POST'])
def add_node():
    """
    Returns a failure JSON response if there is no values in the request or if the node is not in the request. Returns a successfull JSON response if not with all the nodes on the network.
    """
    # Extracts the values by accessing the request
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data found.'
        }
        return jsonify(response), 400
    node = values.get('node')
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@webApp.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    """
    Returns a message of success and all nodes of the current network if the node's url is correct, returns a message of failure if not
    :param node_url: url of the node to be removed
    """
    if node_url == '' or node_url == None:
        response = {
            'message': 'No node found'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@webApp.route('/nodes', methods=['GET'])
def get_nodes():
    """
    Returns a JSON message with all the nodes in the network
    """
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


@webApp.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    # Verification if the values are not empty
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    # Verification if the values contains a sender, a recipient, an amount and a signature
    if not all(key in values for key in required):
        response = {
            'message': 'Some data is missing'
        }
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        # we return the response and a success code
        return jsonify(response), 201
    else:  # If the transaction failed
        response = {
            'message': 'Creating a transaction failed.',
        }
        # Then we return the response and an internal server error
        return jsonify(response), 500


@webApp.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    """
    Function that manages broadcasting blocks of the blockchain through the network
    :returns: A failure if there is no blocks or if the request doesn't contains a block. A success if 
    """
    values = request.get_json()
    # Verifications of the validity of the block
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    if 'block' not in values:
        response = {
            'message': 'Some data is missing'
        }
        return jsonify(response), 400
    # Getting the block and checking its index with the index of the last block of the blockchain
    block = values['block']
    # Success case: we add the block and return a reponse
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {
                'message': 'Block added'
            }
            return jsonify(response), 201
        else:
            response = {
                'Message': 'Block seems invalid.'
            }
            return jsonify(response), 409  # 409 for indicating a conflict
    #
    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'BlockChain seems to differ from local blockchain'
        }
        blockchain.resolve_conflicts = True  # A conflict happens
        # Returns 200 because the error comes from the local node
        return jsonify(response), 200
    # Error case
    else:
        response = {
            'message': 'BlockChain seems to be shorter, block not added'
        }
        return jsonify(response), 409


@webApp.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    """
    Function that try to solve a conflict in the network
    :returns: a message that the chain was replaced or not
    """
    replaced = blockchain.to_resolve_conflicts()
    if replaced:
        response = {
            'message': 'Chain was replaced'
        }
    else:
        respones = {
            'message': 'Local chain kept'
        }
    return jsonify(response), 200


if __name__ == '__main__':
    """
    Condition to set the flask server to the localhost address in the url bar of a browser:
    `127.0.0.1`
    or 
    `localhost`
    To run it in the terminal, write:
    `FLASK_APP=node.py flask run`
    or:
    `python node.py -p <adress_of_node>`
    """
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)  # Initialize a wallet in the object wallet
    # Initialize the blockchain of the wallet
    blockchain = BlockChain(wallet.public_key, port)
    webApp.run(host='127.0.0.1', port=port)
