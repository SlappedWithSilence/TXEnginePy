import dataclasses
from typing import Union


@dataclasses.dataclass
class Currency:
    """Currency records information about money an entity owns.

    Currency objects have a name, quantity, and one or more stages.
    A stage describes a quantified grouping. For example, USD has a stage of "cents: 1" and "dollars: 100"
    A Currency must have a first stage with a value of 1.
    """
    id: int
    name: str
    stages: dict[str, int]
    quantity: int = 0
    allow_negative: bool = False

    @property
    def key(self) -> tuple[int, str]:
        return self.id, self.name

    def __str__(self) -> str:
        sorted_stages = list(self.stages.items())
        sorted_stages.sort(key=lambda x: x[1])
        sorted_stages.reverse()

        base: str = ""
        working_quantity: int = self.quantity

        for stage_name, stage_scale in sorted_stages:
            stage_quantity: int = int(working_quantity / stage_scale)  # Amount of currency that fit into the stage
            remainder: int = int(working_quantity - (stage_scale * stage_quantity))  # How much currency is left
            working_quantity = remainder
            stage_str = f"{stage_quantity} {stage_name} "
            base = base + stage_str

        return base

    def __add__(self, other):

        # If (Currency + Currency)
        if isinstance(other, type(self)):
            if self.id != other.id:
                raise ValueError(f"Cannot add currencies of different names! {self.name}, {other.name}")

            return Currency(self.id, self.name, self.stages, self.quantity + other.quantity)

        # If (Currency + Int)
        elif isinstance(other, int):
            return Currency(self.id, self.name, self.stages, self.quantity + other)

        else:
            raise TypeError(f"Cannot add {type(self)} and {type(other)}!")

    def __sub__(self, other):

        # If (Currency - Currency)
        if isinstance(other, type(self)):
            if self.name != other.name:
                raise ValueError(f"Cannot subtract currencies of different names! {self.name}, {other.name}")

            return Currency(self.id, self.name, self.stages, self.quantity - other.quantity)

        # If (Currency - Int)
        elif isinstance(other, int):
            return Currency(self.id, self.name, self.stages, self.quantity - other)
        else:
            raise TypeError(f"Cannot subtract  {type(self)} and {type(other)}!")

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Currency(self.id, self.name, self.stages, int(self.quantity * other))

        else:
            raise TypeError(f"A Currency may only be multiplied by int or float! Got {type(other)}")

    def __divmod__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Currency(self.id, self.name, self.stages, int(self.quantity / other))

        else:
            raise TypeError(f"A Currency may only be multiplied by int or float! Got {type(other)}")

    def adjust(self, amount: Union[int, float]):
        """ Adjust quantity by 'amount'.

            If amount is an int, simply add it to 'quantity' (flat adjustment).  2 + 3 = 5
            If amount is a float, multiply 'quantity' by it (percent adjustment). 2 x 0.5 = 1
        """
        if type(amount) == int:
            self.quantity = self.quantity + amount

        elif type(amount) == float:
            self.quantity = int(self.quantity * amount)

    def set(self, quantity: int):
        """Set 'quantity' to the passed value."""

        if type(quantity) == int:
            self.quantity = quantity
        else:
            raise TypeError(f"Cannot set a Currency's quantity to type {type(quantity)}! Must be of type int.")


@dataclasses.dataclass
class CoinPurse:
    currencies: dict[tuple[int, str], Currency] = dataclasses.field(default_factory=dict)

    def balance(self, cur: Currency | int | str | tuple[int, str]) -> int:
        # If the passed value is a Currency
        if type(cur) == Currency:
            if cur.key in self.currencies:
                return self.currencies[cur.key].quantity

        # If the passed type is a Currency.key
        if type(cur) == tuple[int, str]:
            if cur in self.currencies:
                return self.currencies[cur].quantity

        # TODO: Improve lookup syntax
        # If the passed type is Currency.id or Currency.name
        if type(cur) == int or type(cur) == str:
            for key in self.currencies:
                if key[0] == cur or key[1] == cur:
                    return self.currencies[key].quantity

        return 0

    def spend(self, cur: Currency | int | str | tuple[int, str], quantity: int | None = None) -> bool:
        if type(cur) == Currency:
            if self.balance(cur) >= cur.quantity:
                self.currencies[cur.key] = self.currencies[cur.key] - cur
                return True

        elif (type(cur) == int or type(cur) == str or type(cur) == tuple[int, str]) and type(quantity) == int:
            if type(cur) == tuple and cur in self.currencies:
                if self.currencies[cur].quantity >= quantity:

                    # Currency exists and has sufficient quantity
                    self.currencies[cur] = self.currencies[cur] - quantity
                    return True

                # The currency exists, but has insufficient quantity
                return False

            elif cur not in self.currencies:
                # THe currency doesn't exist
                return False

            for key in self.currencies:

                # Currency exists and is sufficient
                if cur in key and self.balance(key) >= quantity:
                    self.currencies[key] = self.currencies[key] - quantity
                    return True

                # Currency exists and is insufficient
                elif cur in key and self.balance(key) < quantity:
                    return False

            return False


if __name__ == "__main__":
    stages = {"cents": 1, "dollars": 100}
    currency = Currency(1, "USD", stages, quantity=533)
    currency_2 = Currency(2, "USD", stages, quantity=15)
    print(currency)
    print(currency * 2)
    print(currency * 0)
    print(currency + currency_2)
    print(currency + 55)

    stages = {"bronze": 1, "silver": 100, "gold": 1000}
    currency = Currency(3, "Imperial", stages, 66021)
    print(currency)

