from functools import reduce
from collections import OrderedDict
import json
#import pickle

from hash_util import hash_block, hash_string_256


# initialization of the blockchain
MINING_REWARD = 10
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Flavien'
participants = {'Flavien'}


def save_data():
    ####JSON part
    with open('blockchain.txt', mode='w') as file:
        file.write(json.dumps(blockchain))
        file.write('\n')
        file.write(json.dumps(open_transactions))

    ###Pickle part
    # with open('blockchain.p', mode='wb') as file:
    #     save_data = {
    #         'chain': blockchain,
    #         'ot': open_transactions
    #     }
    #     file.write(pickle.dumps(save_data))


def load_data():
    #JSON version
    try:
        with open('blockchain.txt', mode='r') as file:
            file_content = file.readlines()
            global blockchain, open_transactions
            #Part of the blockchain
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict(
                        [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            #Part of the transaction
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_tx =OrderedDict(
                        [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                updated_transactions.append(updated_tx)
            open_transactions = updated_transactions
    except IOError:
        print('File not found!')


    #Pickle version
    # with open('blockchain.p', mode='rb') as file:
        # file_content = pickle.loads(file.read())
        # global blockchain, open_transactions
        # blockchain = file_content['chain']
        # open_transactions = file_content['ot']


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_last_blockchain_value():
    """
    Get last value of the blockchain
    :return: the last value to the block chain
    """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Add a value to the block chain list
    :param sender: the sender's name of the transaction
    :param recipient: the recipient's name of the transaction
    :param amount: the amount of the transaction (default = 1.0)
    :return: True if transaction if verified, False if not
    """
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    else:
        return False


def mine_block():
    """
    Mine a block to the blockchain
    :return: True if the block has been successfully added to the blockchain
    """
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)

    proof = proof_of_work()
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    copied_transaction = open_transactions[:]
    copied_transaction.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transaction,
        'proof': proof
    }
    blockchain.append(block)
    return True


def get_balance(participant):
    """
    Get the balance of a participant via his transactions
    :param participant: the participant who wants to do a transaction
    :return: the balance between the amount received and the amount sent
    """
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    return amount_received - amount_sent


def get_transaction_value():
    """
    Get the user input for the transaction amount and the recipient's name
    :return: (string, float) recipient's name and amount of the transaction of the user
    """
    recipient = input('Enter the recipient of the transaction: ')
    amount = float(input('Enter the amount of the transaction: '))
    return recipient, amount


def get_user_choice():
    """
    Get the choice of the user
    :return: the choice's number
    """
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    """
    Output th block chain list to the console
    :return: print the elements of the blockchain
    """
    for block in blockchain:
        print('Outputting block')
        print(block)
    else:
        print('-' * 20)


def verify_transaction(transaction):
    """
    Verify if a transaction is balanced
    :param transaction: the transaction to verify
    :return: True if the transaction is less or equal to the balance of the sender
    """
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_chain():
    """
    Verify if the previous element of a blockchain is intact
    :return: True if it is or false if not
    """
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        elif block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        elif not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False

    return True


def verify_transactions():
    return all([verify_transactions(tx) for tx in open_transactions])


load_data()
waiting_for_input = True

while waiting_for_input:
    print('Please choose an option:')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Print the block chain')
    print('4: Print the participants')
    print('5: Check transaction validity')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        recipient, amount = get_transaction_value()
        if add_transaction(recipient, amount=amount):
            print('Added transaction')
        else:
            print('Transaction failed!')
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions!')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100.0}]
            }
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list')
    if not verify_chain():
        print(print_blockchain_elements())
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format('Flavien', get_balance('Flavien')))
    print('Choice registered')
else:
    print('User left!')

print('Done!')
