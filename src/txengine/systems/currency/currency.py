class Currency:
    """Currency records information about money an entity owns.

    Currency objects have a name, quantity, and one or more stages.
    A stage describes a quantified grouping. For example, USD has a stage of "cents: 1" and "dollars: 100"
    A Currency must have a stage with a value of 1.
    """

    def __init__(self, name: str, stages: dict[str, int], quantity: int = 0, allow_negative: bool = False):
        self.name: str = name
        self.stages: dict[str, int] = stages
        self.quantity: int = quantity
        self.allow_negative: bool = allow_negative

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
        if isinstance(other, type(self)):
            if self.name != other.name:
                raise ValueError(f"Cannot add currencies of different names! {self.name}, {other.name}")

            return Currency(self.name, self.stages, self.quantity + other.quantity)

        elif isinstance(other, int):
            return Currency(self.name, self.stages, self.quantity + other)

        else:
            raise TypeError(f"Cannot add {type(self)} and {type(other)}!")

    def __sub__(self, other):
        if isinstance(other, type(self)):
            if self.name != other.name:
                raise ValueError(f"Cannot add currencies of different names! {self.name}, {other.name}")

            return Currency(self.name, self.stages, self.quantity - other.quantity)
        elif isinstance(other, int):
            return Currency(self.name, self.stages, self.quantity - other)
        else:
            raise TypeError(f"Cannot add {type(self)} and {type(other)}!")

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Currency(self.name, self.stages, int(self.quantity * other))

        else:
            raise TypeError(f"A Currency may only be multiplied by int or float! Got {type(other)}")

    def __divmod__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Currency(self.name, self.stages, int(self.quantity / other))

        else:
            raise TypeError(f"A Currency may only be multiplied by int or float! Got {type(other)}")


if __name__ == "__main__":

    stages = {"cents": 1, "dollars": 100}
    currency = Currency("USD", stages, quantity=533)
    currency_2 = Currency("USD", stages, quantity=15)
    print(currency)
    print(currency * 2)
    print(currency * 0)
    print(currency + currency_2)
    print(currency + 55)

    stages = {"bronze" : 1, "silver" : 100, "gold" : 1000}
    currency = Currency("Imperial", stages, 66021)
    print(currency)
