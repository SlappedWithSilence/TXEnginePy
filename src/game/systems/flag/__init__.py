from game.systems.flag.flag_manager import FlagManager

flag_manager = FlagManager()


def get_flag(flag: str) -> bool:
    """
    A convenience wrapper for FlagManager::get_flag
    """
    return flag_manager.get_flag(flag)


def set_flag(flag: str, value: bool) -> None:
    """
    A convenience wrapper for FlagManager::set_flag
    """
    flag_manager.set_flag(flag, value)
