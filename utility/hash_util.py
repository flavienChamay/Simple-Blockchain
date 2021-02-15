"""
This module is regroups all methods to generate hashes used by the blocks for identification and security mechanism.

:method: hash_string_256(string)
:method: hash_block(block)
"""

import json
import hashlib


def hash_string_256(string):
    """
    This function creates a SHA256 hash for a given input string.

    :param string str: The string that will be hashed.
    :returns str: The hash of the parameter string.
    """

    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """
    This function hashes a block and returns a string representation of it.

    :param block Block: The block that will be hashed.
    :var hashable_block dict: The block that is transformed into a dictionary.
    :returns str: The hash code of the parameter block.
    """

    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict()
                                      for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
