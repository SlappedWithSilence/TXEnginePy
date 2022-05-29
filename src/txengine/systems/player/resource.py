class PlayerResource:
    """Represents a resource to be used by the player."""

    def __init__(self, name: str, description: str, maximum: int, current: int):
        self.name: str = name
        self.description: str = description
        self.maximum: int = maximum
        self.current: int = current

    def consume(self, quantity: int) -> None:
        """Simulates the player consuming 'n' of the resource"""

        if quantity <= self.current:
            self.current = self.current - quantity

        else:
            self.current = 0

    def test(self, quantity) -> bool:
        """Returns true if quantity <= current, false otherwise."""

        if self.current >= quantity:
            return True

        return False
