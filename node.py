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
    This function controls the UI of the main program
    """
    return send_from_directory('ui', 'node.html')


@webApp.route('/network', methods=['GET'])
def get_network():
    """
    Returns the interface of the network UI
    """
    return send_from_directory('ui', 'network.html')


@webApp.route('/transactions', methods=['GET'])
def get_open_transation():
    """
    Function that returns the open transactions 
    """
    all_transactions = blockchain.get_open_transactions()
    # We need to transform all those transactions into dictionnary format
    dict_transactions = [tx.__dict__ for tx in all_transactions]
    # We convert the dictionnay into JSON and returns it with a OK code
    return jsonify(dict_transactions), 200
        
    
@webApp.route('/wallet', methods=['POST'])
def create_keys():
    """
    Function who creates the keys for the wallet via a POST method in the route /wallet
    """
    wallet.create_keys()
    if wallet.save_keys(): # If the saving key funcitonnality succeed than displays the public and private keys and a success code for the server
        #We must define a global variable blockchain because 
        global blockchain
        blockchain = BlockChain(wallet.public_key, port)
        response = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key,
            'funds' : blockchain.get_balance()
        }
        return jsonify(response), 201
    else: # If the saving key functionnality fails than return a text message and a server error code 
        response = {
            'message' : 'Saving the keys failed'
        }
        return jsonify(response), 500

    
@webApp.route('/wallet', methods=['GET'])
def load_keys():
    """
    Function that load the keys of a wallet via a GET method and a /wallet route
    """
    if wallet.load_keys():
        #We must define a global variable blockchain because 
        global blockchain
        blockchain = BlockChain(wallet.public_key, port)
        response = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key,
            'funds' : blockchain.get_balance()
        }
        return jsonify(response), 201
    else: # If the loading key functionnality fails than return a text message and a server error code 
        response = {
            'message' : 'Loading the keys failed'
        }
        return jsonify(response), 500


@webApp.route('/transaction', methods=['POST'])
def add_transaction():
    """
    Function that manages the addition of new transactions
    """
    if wallet.public_key == None: # If the public key doesn't exists
        response = {
            'message' : 'No wallet set up.'
        }
        return jsonify(response), 400 # then we return the message and a bad request code
    incoming_values = request.get_json() #Flask will use this function to intercept a request in JSON format ; incoming_values is therefore a dictionnay
    if not incoming_values: # If we have no incoming_values then we write an error message
        response = {
            'message' : 'No data found.'
        }
        return jsonify(response), 400 # We return the response and we send a bad request code
    required_fields = ['recipient', 'amount']
    # If all fields in the values doesn't match then  
    if not all(field in incoming_values for field in required_fields):
        response = {
            'message': 'Required data is missing',
        }
        return jsonify(response), 400 # Return the message and a bad request code
    # At this stage, we have proper data
    recipient = incoming_values['recipient']
    amount = incoming_values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
    if success: # If the transaction is added successfully
        response = {
            'message' : 'Successfully added transaction.',
            'transaction' : {
                'sender' : wallet.public_key,
                'recipient' : recipient,
                'amount' : amount,
                'signature' : signature
            },
            'funds' : blockchain.get_balance()
        }
        return jsonify(response), 201 # we return the response and a success code
    else: # If the transaction failed
        response = {
            'message' : 'Creating a transaction failed.',
        }
        return jsonify(response), 500 # Then we return the response and an internal server error 


@webApp.route('/chain', methods=['GET'])
def get_chain():
    """
    This function controls the action of getting the chain of the blockchain and displays it in JSON format
    """
    chain_snapshot = blockchain.chain
    dictionnary_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dictionnary_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dictionnary_chain), 200 #returns the chain in the form of a dictionnary and with a code 


@webApp.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None: #If the public key exists than we will return a success message and an error message if not
        response = {
            'message' : 'Fetched balance successfully.',
            'funds' : balance
        }
        return jsonify(response), 200 # Return the response jsonify and an OK success code
    else:
        response = {
            'message' : 'Loading balance failed.',
            'wallet_set_up' : wallet.public_key != None
        }
        return jsonify(response), 500 #Return the response and an error code
    

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
        return jsonify(response), 409 # The 409 means that the user might resolve this conflict by himself
    block = blockchain.mine_block()
    if block != None: #in case of a success
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message' : 'Block added successfully',
            'block' : dict_block,
            'funds' : blockchain.get_balance() 
        }
        return jsonify(response), 201 #returns the response and a success code indicating that the request has been fulfilled 
    else: #in case of an error
        response={
            'message' : 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500 #returns the response and a server error code of 500


@webApp.route('/node', methods=['POST']) #POST because we want to add something to the server
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
    #Verification if the values are not empty
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    #Verification if the values contains a sender, a recipient, an amount and a signature
    if not all(key in values for key in required):
        response = {
            'message': 'Some data is missing'
        }
        return jsonify(response), 400
    success = blockchain.add_transaction(values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message' : 'Successfully added transaction.',
            'transaction' : {
                'sender' : values['sender'],
                'recipient' : values['recipient'],
                'amount' : values['amount'],
                'signature' : values['signature']
            }
        }
        return jsonify(response), 201 # we return the response and a success code
    else: # If the transaction failed
        response = {
            'message' : 'Creating a transaction failed.',
        }
        return jsonify(response), 500 # Then we return the response and an internal server error 


@webApp.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    """
    Function that manages broadcasting blocks of the blockchain through the network
    :returns: A failure if there is no blocks or if the request doesn't contains a block. A success if 
    """
    values = request.get_json()
    #Verifications of the validity of the block
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
    #Getting the block and checking its index with the index of the last block of the blockchain
    block = values['block']
    #Success case: we add the block and return a reponse
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
            return jsonify(response), 409 #409 for indicating a conflict
    #
    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'BlockChain seems to differ from local blockchain'
        }
        blockchain.resolve_conflicts = True # A conflict happens
        return jsonify(response), 200 #Returns 200 because the error comes from the local node
    #Error case
    else:
        response = {
            'message': 'BlockChain seems to be shorter, block not added'
        }
        return jsonify(response), 409


@webApp.route('/resolve-conflicts', methods = ['POST'])
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
    Condition that set the flask server to the localhost address : 127.0.0.1 or localhost
    To run it in the terminal write:
    FLASK_APP=node.py flask run
    or:
    python node.py -p (adressOfNode)
    
    """
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port) #Initialize a wallet in the object wallet
    blockchain = BlockChain(wallet.public_key, port) #Initialize the blockchain of the wallet
    webApp.run(host='127.0.0.1', port=port)
    
