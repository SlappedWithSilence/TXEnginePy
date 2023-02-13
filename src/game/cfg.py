config: dict[str, any] = None


def set_config(cfg: dict) -> None:
    global config

    config = cfg


def get_config() -> dict:
    global config
    return config
