"""
This module implements the transformation of a dictionnary into a string type.

:class Printable: Class of the conversion mechanism into a string of a dict.
"""


class Printable:
    """
    Printable class is used to transform the dictionary into a str type.

    :method: __repr__(self)
    """

    def __repr__(self):
        """
        Customization of the printing of the Printable class.

        :returns str: Transforms from a string into a dictionary.
        """

        return str(self.__dict__)
