import json
import hashlib


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """
    Hashes a block
    :param block: The block that will be hashed
    :return: The hash code of the block
    """
    return hash_string_256(json.dumps(block, sort_keys=True).encode())