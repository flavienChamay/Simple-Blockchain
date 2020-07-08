class Printable:
    def __repr__(self):
        """
        Constructor of the Printable class
        :return: Transform into a string a dictionary
        """
        return str(self.__dict__)