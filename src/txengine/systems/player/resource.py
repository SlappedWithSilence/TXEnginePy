from typing import Union


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

    def adjust(self, quantity: Union[int, float]) -> int:
        """Alter the quantity of 'current' by 'quantity'

            if 'quantity' is an int, simply increment
            if 'quantity' is a float, increment by ('maximum' * 'quantity')

            In both cases, the floor for 'current' is zero, and the ceiling is 'maximum'
        """

        if type(quantity) == int:
            self.current = max(min(self.maximum, self.current + quantity), 0)

        elif type(quantity) == float:
            term: float = self.maximum * quantity
            self.current = max(min(self.maximum, self.current + int(term)), 0)
        else:
            raise TypeError(f"PlayerResource.adjust accepts only int and float! {type(quantity)} is not supported!")

        return self.current

    def set(self, quantity: int) -> int:
        """Set 'current' to 'quantity' """
        if self.maximum > quantity >= 0:
            self.current = quantity
            return self.current

        raise ValueError(f"Quantity {quantity} is out of bounds!")

    @property
    def percent(self) -> float:
        """Returns percentage of remaining resource"""
        return float(self.current) / float(self.maximum)

