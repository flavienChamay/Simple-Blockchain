"""
This module implements the creation of a block, the component of a blockchain. It allows the user to simply create a block with the required informations.

:class Block: Class of the block.
"""

from time import time
from utility.printable import Printable


class Block(Printable):
    """
    Block class is used to create a block.

    :method: __init__(self, index, previous_hash, transactions, proof, time=time())
    """

    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        """
        Initialize the block with input values.

        :param index int: The position of the block relative to the blockchain.
        :param previous_hash str: The previous hash of the blockchain.
        :param transactions list: The list of transactions.
        :param proof int: 0 if the block is valid, other if not.
        :param time float: The time of its creation.
        :returns Block: Yields a block's instance.
        """
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof
