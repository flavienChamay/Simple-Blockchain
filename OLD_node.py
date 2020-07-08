from blockchain import BlockChain
#from uuid import uuid4
from utility.verification import Verification
from wallet import Wallet


class Node:
    def __init__(self):
        """
        Constructor of the Node class
        :var id: the unique id of the node
        :var chain: the chain of the blockchain
        """
        # Unique ID
        #self.wallet = str(uuid4())
        self.wallet = Wallet()
        # Initialize the chain with a unique ID
        self.wallet.create_keys()
        self.blockchain = BlockChain(self.wallet.public_key)

    def get_transaction_value(self):
        """
        Get the user input for the transaction amount and the recipient's name
        :return: (string, float) recipient's name and amount of the transaction of the user
        """
        recipient = input('Enter the recipient of the transaction: ')
        amount = float(input('Enter the amount of the transaction: '))
        return recipient, amount

    def print_blockchain_elements(self):
        """
        Output th block chain list to the console
        :return: print the elements of the blockchain
        """
        for block in self.blockchain.chain:
            print('Outputting block')
            print(block)
        else:
            print('-' * 20)

    def get_user_choice(self):
        """
        Get the choice of the user
        :return: the choice's number
        """
        user_input = input('Your choice: ')
        return user_input

    def listen_for_input(self):
        """
        Menu of the node with multiple choices
        :return: Prints the options of the user and infos about the evolution of the blockchain
        """
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose an option:')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Print the block chain')
            print('4: Check transaction validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save keys')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                recipient, amount = self.get_transaction_value()
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Added transaction')
                else:
                    print('Transaction failed!')
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed. Got no wallet?')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions!')
            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = BlockChain(self.wallet.public_key)
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = BlockChain(self.wallet.public_key)
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list')
            if not Verification.verify_chain(self.blockchain.chain):
                print(self.print_blockchain_elements())
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))
            print('Choice registered')
        else:
            print('User left!')

        print('Done!')


# Initializing the node
if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
