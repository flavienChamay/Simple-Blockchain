from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):
    def __init__(self, sender, recipient, signature, amount):
        """
        Constructor of the Transaction class
        :param sender: the name of the sender of the transaction
        :param recipient: the name of the recipient of the transaction
        :param amount: the amount of the transaction
        :param signature: the signature of the transaction
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        """
        Transform the information of a transaction into an Ordered Dictionary
        :return:
        """
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
