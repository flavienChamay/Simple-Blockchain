from time import time
from utility.printable import Printable


class Block(Printable):
    """
    Constructor of the Block class
    """
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof
