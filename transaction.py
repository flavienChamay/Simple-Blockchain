"""
This module implements the creation of a transaction. It allows the user to simply create a transaction with the required informations.

:class Transaction: Class of the transaction.
"""

from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):
    """
    Transaction class is used to create a transaction.

    :method: __init__(self, sender, recipient, signature, amount)
    :method: to_ordered_dict(self)
    """

    def __init__(self, sender, recipient, signature, amount):
        """
        Initialize the transaction with input values.

        :param sender str: The name of the sender of the transaction.
        :param recipient str: The name of the recipient of the transaction.
        :param amount float: The amount of the transaction
        :param signature str: the signature of the transaction
        :returns Transaction: Yields a transaction's instance.
        """

        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        """
        This function transforms the information of a transaction into an Ordered Dictionary.

        :returns dict: The ordered dictionnary of the transaction.
        """

        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
