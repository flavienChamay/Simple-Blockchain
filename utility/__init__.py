"""
This module transforms the utility directory (`~/utility`) into a python package (for being able to use the import command).
And when importing, the var __all__ is present.

:var __all__ list: A list of two strings containing hashes.
"""


from utility.hash_util import hash_string_256, hash_block

__all__ = ['hash_string_256', 'hash_block']
