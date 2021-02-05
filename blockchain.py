import json
import requests

from functools import reduce
from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet


# Reward that we give to miners for creating a new block
MINING_REWARD = 10


class BlockChain:
    def __init__(self, public_key, node_id):
        """
        Constructor of the Chain class
        :param public_key: the unique ID of the host of the node
        :var blockchain: the list of blocks of the blockchain
        :var open_transactions: the list of transactions
        :var load_data: load the data from file if it exists
        :var public_key: the unique ID of the node
        """
        # The starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Initializing the blockchain list with genesis block
        self.chain = [genesis_block]
        # Unhandled transactions, private attribute
        self.__open_transactions = []
        # Name of the host of the blockchain
        self.public_key = public_key
        # Set of all the participants (nodes) in the network, private attribute
        self.__peer_nodes = set()
        #ID of the node
        self.node_id = node_id
       # Loading the data from file if it exists, must be at the end, after doing all above initialisations
        self.load_data()

    @property
    def chain(self):
        """
        Getter of the chain
        :return: chain of the blockchain
        """
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        """
        Setter of the chain
        :param val: New value of the chain
        :return: Nothing
        """
        self.__chain = val

    def get_open_transactions(self):
        """
        Getter of the open transactions
        :return: the open transactions
        """
        return self.__open_transactions[:]

    def save_data(self):
        """
        Saves the whole blockchain into a file named blockchain.txt
        :return: A file blockchain.txt if it does not exists or write the new data of the blockchain into the file
        """
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as file:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions] , block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                file.write(json.dumps(saveable_chain))
                file.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                file.write(json.dumps(saveable_tx))
                file.write('\n')
                file.write(json.dumps(list(self.__peer_nodes))) # Updates the number of nodes in the network
        except IOError:
            print('Saving failed!')

            
    def load_data(self):
        """
        loads the blockchain from the blockchain.txt file
        :return: Displays a message if the file is not found
        """
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as file:
                file_content = file.readlines()

                # Part of the blockchain
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                # Part of the transaction
                self.__open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in self.__open_transactions:
                    updated_tx = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_tx)
                self.__open_transactions = updated_transactions  # Loads the connected nodes
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            print('File not found!')

    def proof_of_work(self):
        """
        Verify the integrity of the blockchain
        :return: the proof number of the blockchain
        """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_last_blockchain_value(self):
        """
        Get last value of the blockchain
        :return: the last value to the block chain
        """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """
        Add a value to the block chain list
        :param sender: the sender's name of the transaction
        :param recipient: the recipient's name of the transaction
        :param amount: the amount of the transaction (default = 1.0)
        :param is_receiving: False when creating a new transaction on this node, True when receiving a broadcast transaction
        :return: True if transaction if verified, False if not
        """
        if self.public_key == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                #Looping through all nodes to broadcast the infos:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
                    return True
                else:
                    return False
                

    def mine_block(self):
        """
        Mine a block to the blockchain
        :return: True if the block has been successfully added to the blockchain
        """
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        proof = self.proof_of_work()

        reward_transaction = Transaction('MINING', self.public_key, '', MINING_REWARD)
        copied_transaction = self.__open_transactions[:]
        for tx in copied_transaction:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transaction.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transaction, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block

    def get_balance(self, sender=None):
        """
        Get the balance of a participant via his transactions
        :return: the balance between the amount received and the amount sent
        """
        if sender == None:
            if self.public_key == None: # This tests if the public key exists (referenced by hositng_node)
                return None
            participant = self.public_key # Participant is a unique ID
        else:
            participant = sender
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions
                          if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        return amount_received - amount_sent


    def add_peer_node(self, node):
        """
        Adds a new node to the network
        :return: None
        :param node: The node URL which should be added
        """
        self.__peer_nodes.add(node)
        self.save_data()

    
    def remove_peer_node(self, node):
        """
        Removes a node to the network
        :return: None
        :param node: The node URL which should be removed
        """
        self.__peer_nodes.discard(node)
        self.save_data()


    def get_peer_nodes(self):
        """
        Function that gives all the connected peer nodes in the network
        :return: a list of all connected peer nodes.
        """
        return list(self.__peer_nodes)


    def add_block(self, block):
        """
        Function that adds a block to the blockchain
        :param block: the block to add to the blockchain
        :returns: false if the block has not been added, true if it has
        """
        #Validation of the block
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transaction']]
        proof_is_valid = Verification.valid_proof(transactions, block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        #Add the block
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        self.save_data() 
        return True
