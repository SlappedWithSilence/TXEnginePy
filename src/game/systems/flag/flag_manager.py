from game.structures.manager import Manager


class FlagManager(Manager):

    def __init__(self):
        super().__init__()
        self._manifest: dict[str, any] = {}

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def clear(self) -> None:
        self._manifest = {}

    def get_flag(self, key: str) -> bool:
        """
        Gets the value of the flag associated with key.

        If the flag does not exist, but COULD exist (IE wouldn't cause a collision), return False. If setting the flag
        would cause a collision, throw an error instead.

        TXEngine Flags are slightly different from exact str-bool mappings. A Flag may define itself to be a part of a
        flag "subgroup" using dot-notation.
        For example:
         - A flag with a key of some.flag = True would store itself in the flags cache as flags['some']['flag'] = True
         - A flag with a key of this.is.a.deep.flag = False would be flags['this']['is']['a']['deep']['flag'] = False
        """

        level: dict | bool = self._manifest
        for part in key.split('.'):
            if part not in level:
                return False

            level = level[part]

        if type(level) != bool:
            raise KeyError(f"Flag {key} not found! {key} points to a dict.")

        return level

    def set_flag(self, key: str, value: bool) -> None:
        """
        Sets a flag of key 'key' to 'value'.

        TXEngine Flags are slightly different from exact str-bool mappings. A Flag may define itself to be a part of a
        flag "subgroup" using dot-notation.
        For example:
         - A flag with a key of some.flag = True would store itself in the flags cache as flags['some']['flag'] = True
         - A flag with a key of this.is.a.deep.flag = False would be flags['this']['is']['a']['deep']['flag'] = False
        """

        if type(key) != str:
            raise TypeError(f"Cannot set flag for key of type {type(key)}! key must be a str.")

        if type(value) != bool:
            raise TypeError(f"Cannot set flag {key} to value of type {type(value)}! Value must be of type bool.")

        if '.' not in key:
            self._manifest[key] = value

        else:
            level = self._manifest  # Record only deepest dict visited so far, starting with the root of the flags dict
            parts = key.split('.')  # Split the key into sub-keys

            # For each sub-key except the last one, traverse through the flags dict, creating new dicts where needed
            for i in range(len(parts) - 1):

                # If a new dict must be made
                if parts[i] not in level:
                    level[parts[i]] = {}
                    level = level[parts[i]]

                # If a flag exists in the way of creating a new dict, raise an error
                elif type(level[parts[i]]) != dict:
                    raise KeyError(f'Cannot set flag {key}, a collision with key {".".join(parts[:i])} was found!')

                # If the dict already exists, traverse to it
                else:
                    level = level[parts[i]]

            # Set the final sub-key's value in the lowest-traversed dict
            level[parts[-1]] = value



