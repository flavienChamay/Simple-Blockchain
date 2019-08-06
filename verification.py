from hash_util import hash_block, hash_string_256


class Verification:

    def verify_chain (self, blockchain):
        """
        Verify if the previous element of a blockchain is intact
        :return: True if it is or false if not
        """
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            elif block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            elif not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False

        return True

    def verify_transactions(self, open_transactions, get_balance):
        return all([self.verify_transactions(tx, get_balance) for tx in open_transactions])

    def verify_transaction(self, transaction, get_balance):
        """
        Verify if a transaction is balanced
        :param transaction: the transaction to verify
        :return: True if the transaction is less or equal to the balance of the sender
        """
        sender_balance = get_balance(transaction.sender)
        return sender_balance >= transaction.amount

    def valid_proof(self, transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'