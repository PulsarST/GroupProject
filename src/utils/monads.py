class Maybe:
    def __init__(self, value):
        self.value = value

    def map(self, func):
        if self.value is None:
            return Maybe(None)
        return Maybe(func(self.value))

    def unwrap(self, default=None):
        return self.value if self.value is not None else default


class Either[T]:
    def __init__(self, left: T | None = None, right: T | None = None):
        self.left: T | None = left
        self.right: T | None = right

    @staticmethod
    def right(value):
        return Either(right=value)

    @staticmethod
    def left(value):
        return Either(left=value)

    def map(self, func):
        if self.right is not None:
            return Either.right(func(self.right))
        return self

    def unwrap(self, default=None):
        return self.right if self.right is not None else default
