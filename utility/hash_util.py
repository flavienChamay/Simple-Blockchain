import json
import hashlib


def hash_string_256(string):
    """
    Create a SHA256 hash for a given input string
    :param string: the string that will be hashed
    :return: the hash of the string
    """
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """
    Hashes a block and returns a string representation of it.
    :param block: The block that will be hashed
    :return: The hash code of the block
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())