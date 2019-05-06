# initialization of the blockchain

blockchain = []


def get_last_blockchain_value():
    """
    Get last value of the blockchain
    :return: the last value to the block chain
    """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(transaction_amount, last_transaction=[1]):
    """
    Add a value to the block chain list
    :param transaction_amount: the amount of the transaction
    :param last_transaction: the last transaction in the block chain
    :return: void
    """
    if last_transaction == None:
        last_transaction = [1]
    blockchain.append([last_transaction, transaction_amount])


def get_transaction_value():
    """
    Get the user input for the transaction amount
    :return: (float) amount of the transaction of the user
    """
    return float(input('Your transaction amount please: '))


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


def verify_chain():
    """
    Verify if the previous element of a blockchain is intact
    :return: True if it is or false if not
    """
    is_valid = True
    for block_index in range(len(blockchain)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
            is_valid = True
        else:
            is_valid = False
    return is_valid


waiting_for_input = True

while waiting_for_input:
    print('Please choose an option:')
    print('1: Add a new transaction value')
    print('2: Print the block chain')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_amount  = get_transaction_value()
        add_transaction(tx_amount, get_last_blockchain_value())
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list')
    if not verify_chain():
        print(print_blockchain_elements())
        print('Invalid blockchain!')
        break
    print('Choice registered')
else:
    print('User left!')

print('Done!')
