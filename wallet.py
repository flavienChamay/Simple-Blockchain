"""
This module implements the creation of a wallet (or of a node). It allows the user to create a wallet, to create the keys, to save them, to load them and to verify transactions.

:class Wallet: Class of the wallet.
"""

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:
    """
    Wallet class is used to create a wallet, to generate its keys, to load them and to verify transactions.

    :method: __init__(self, node_id)
    :method: save_keys(self)
    :method: create_keys(self)
    :method: load_keys(self)
    :method: generate_keys(self)
    :method: sign_transaction(self, sender, recipient, amount)
    :method: verify_transaction(transaction)
    """

    def __init__(self, node_id):
        """
        Initialize the wallet with input values.

        :param node_id str: Unique identifier of the node.
        :var private_key str: The private key of the wallet. Default=None.
        :var public_key str: The public key of the wallet. Default=None.
        :returns Wallet: Yields a wallet's instance.
        """
        # TODO: See what is node_id in contrast to the public key.

        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def save_keys(self):
        """
        This function saves the keys of the wallet in a text file.

        :returns bool: True if the keys are correctly saved, false if not.
        :raises IOError: If the file is not correctly created or written into.
        :raises IndexError: If the position in the file is incorrect.
        """

        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), mode='w') as file:
                    file.write(self.public_key)
                    file.write('\n')
                    file.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving wallet failed...')
                return False

    def create_keys(self):
        """
        This function creates the keys for the wallet.

        :var private_key str: The private key of the wallet.
        :var public_key str: The public key of the wallet.
        :returns: None.
        """

        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def load_keys(self):
        """
        This function loads the keys of the wallet from the text file.

        :var public_key str: The public key of the wallet.
        :var private_key str: The private key of the wallet.
        :returns: True if the keys are correctly loaded, false if not.
        :raises IOError, IndexError: If the wallet failed to be loaded from text file.
        """

        try:
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as file:
                keys = file.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except (IOError, IndexError):
            print('Loading wallet failed...')
            return False

    def generate_keys(self):
        """
        This function generates the keys of the wallet.

        :var private_key str: The private key to be generated for the wallet.
        :var public_key str: The public key to be generated for the wallet.
        :returns (str, str): A couple containing the public and private keys.
        """

        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

    def sign_transaction(self, sender, recipient, amount):
        """
        This function signs the transaction for validation.

        :param sender str: The sender of the transaction.
        :param recipient str: The recipient of the transaction.
        :param amount float: The amount of the transaction.
        :var signer : 
        :var hash_payload:
        :var signature str:
        :returns str:
        """
        # TODO: Need more information on the variables

        signer = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(self.private_key)))
        hash_payload = SHA256.new(
            (str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(hash_payload)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        """
        This staticmethod function verifies a transaction.

        :param transaction Transaction: The transaction to verify.
        :var public_key str: Imports the public key from the sender's transaction.
        :var verifier PKCS115_Cipher: Create a cipher for performing PKCS#1 v1.5 decryption.
        :var h SHA256: The hash of the transaction's sender, recipient and amount.
        :returns bool: True if the transaction is verified, false if not.
        """

        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) +
                        str(transaction.amount)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
