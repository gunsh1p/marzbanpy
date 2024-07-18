class Base:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__dict__})"

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.__dict__})"
