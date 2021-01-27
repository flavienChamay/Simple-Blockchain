"""Provided verification helper methods."""

from utility.hash_util import hash_block, hash_string_256
from wallet import Wallet

class Verification:
    """
    A helper class which iffer various static and class-based verifications
    """
    @classmethod
    def verify_chain (cls, blockchain):
        """
        Verify if the previous element of a blockchain is intact
        :return: True if it is or false if not
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
        Verify all the transactions
        :param open_transactions: the transactions already executed
        :param get_balance: the balance of the transactions
        :return: Returns true if all verified transactions are correct, returns false if not
        """
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])

    @staticmethod
    def verify_transaction(transaction, get_balance,  check_funds = True):
        """
        Verify if a transaction is balanced
        :param transaction: the transaction to verify
        :return: True if the transaction is less or equal to the balance of the sender
        """
        if check_funds:
            sender_balance = get_balance()
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """
        Calculate the proof of all the transactions based of the previous hash and the proof's number
        :param transactions: All of the transactions
        :param last_hash: the previous hash of the transactions
        :param proof: the proof's number
        :return: True if the proof is valid, returns false if not
        """
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'