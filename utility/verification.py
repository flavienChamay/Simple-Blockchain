"""
This module provides verification helper methods to verify the blockchain, the transactions and the proof of work.

:class Verification: Class of the verification mechanism.
"""

from utility.hash_util import hash_block, hash_string_256
from wallet import Wallet


class Verification:
    """
    Verification class is used to create and use verfication mechanisms.

    :method: verify_chain(cls, blockchain)
    :method: verify_transactions(cls, open_transactions, get_balance) 
    :method: verify_transaction(transaction, get_balance,  check_funds=True)
    :method: valid_proof(transactions, last_hash, proof)
    """

    @classmethod
    def verify_chain(cls, blockchain):
        """
        This classmethod method verifies if the previous element of a blockchain is valid.

        :param cls:
        :param blockchain BlockChain: The blockchain to verify.
        :returns bool: True if the integrity of the blockchain is maintained, false if not.
        """

        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            elif block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            elif not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """
        This classmethod method verifies all the transactions.

        :param open_transactions: the transactions already  executed
        :param get_balance: the balance of the transactions
        :param cls:
        :returns: Returns true if all verified transactions are correct, returns false if not.
        """

        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """
        This staticmethod method verifies if a transaction is balanced.

        :param transaction: the transaction to verify.
        :param get_balance:
        :param check_funds: Default=True.
        :var sender_balance:
        :returns: True if the transaction is less or equal to the balance of the sender
        """

        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """
        This staticmethod method calculates the proof of all the transactions based on the previous hash and the proof's number.

        :param transactions: All of the transactions
        :param last_hash: the previous hash of the transactions
        :param proof: the proof's number
        :var guess:
        :var guess_hash:
        :returns bool: True if the proof is valid, returns false if not
        """

        guess = (str([tx.to_ordered_dict() for tx in transactions]
                     ) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'
