from txengine.ui.color.colors import c_form


class Item:
    def __init__(self):
        self.name: str = None
        self.desc: str = None
        self.id: int = None
        self.value: int = None
        self.max_stacks: int = None

    @property
    def summary(self):
        """Returns a formatted string containing pertinent information about the item."""
        return c_form(self.name, "item_name") + "\n" \
               + c_form(self.desc, "item_desc") + "\n" \
               + "Value: " + c_form(str(self.value), "item_value")
