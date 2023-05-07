import os.path

from loguru import logger
from omegaconf import OmegaConf

import game.systems.room.action.shop_action
from .cache import get_config, set_config, get_cache, from_cache
from .formatting import register_arguments, register_style
from .systems import currency, room, item
from .systems.entity.entities import Player
from .systems.event.add_item_event import AddItemEvent
from .systems.event.events import ConsumeItemEvent
from .systems.requirement.item_requirement import ConsumeItemRequirement
from .systems.room.action import actions
from .systems.room.action.actions import ViewInventoryAction

conf_dir_path: str = "./config/"
conf_file_path: str = "conf.yaml"
style_file_path: str = "styles.yaml"
conf_path: str = conf_dir_path + conf_file_path
style_path: str = conf_dir_path + style_file_path


class Engine:
    """
    A high-level manager that coordinates disk-io, config manipulation, loading content, saving content, and more
    """

    # An explicit order for order-dependant managers. Any managers not listed will be loaded in random order after the
    # lowest priority (the largest int).
    manager_load_priority = {
        0: ["CurrencyManager", "ResourceManager", "FlagManager"],
        1: ["ItemManager"],
        2: ["EquipmentManager"],
        3: ["EntityManager"],
        4: ["RoomManager"]
    }

    @classmethod
    def get_manager_priority(cls, manager_cls: str | type) -> int | None:
        """
        Retrieve the priority of a manager class

        args:
            manager_cls : The name of the class of the manager, or the class of the manager

        returns: The priority of the manager class if it has been set, otherwise None
        """

        if type(manager_cls) == str:
            true_cls = manager_cls
        elif type(manager_cls) == type:
            true_cls = manager_cls.__name__
        else:
            raise TypeError(f"Expect str or type for manager_cls. Got type {type(manager_cls)} instead!")

        for priority in cls.manager_load_priority:
            if true_cls in cls.manager_load_priority[priority]:
                return priority

        return None

    @classmethod
    def set_manager_priority(cls, manager_cls: str | type, priority: int) -> None:
        """
        Set a manager's loading priority.

        Priorities with lower numerical values are loaded sooner.

        Args:
            manager_cls: The name of the class of the manager
            priority: The priority of the loading.

        Returns: None
        """

        # Type checking
        if type(priority) != int:
            raise TypeError(f"Cannot set priority to type {type(priority)}. Priority must be an int!")
        if priority < 0:
            raise ValueError(f"Invalid priority: {priority}. Priority must be positive or zero!")

        if type(manager_cls) == str:
            true_cls = manager_cls
        elif type(manager_cls) == type:
            true_cls = manager_cls.__name__
        else:
            raise TypeError(f"Expect str or type for manager_cls. Got type {type(manager_cls)} instead!")

        # Check if the manager has already been assigned a priority. If so, remove it from the extant list
        extant_priority = cls.get_manager_priority(true_cls)
        if extant_priority is not None:
            cls.manager_load_priority[extant_priority].remove(true_cls)

        # Check if the that priority already has a mapped list. If not, make one.
        if priority not in cls.manager_load_priority:
            cls.manager_load_priority[priority] = []

        # Assign priority in map
        cls.manager_load_priority[priority].append(true_cls)

    def _debug_init_early(self) -> None:
        """
        A special function that runs before startup to support debugging efforts.
        Returns: None

        """

    def _debug_init_late(self) -> None:
        """
        A special function that runs post-startup to support debugging efforts.
        Returns:

        """
        # TODO: Remove debugging code
        currency.currency_manager.currencies[0] = currency.Currency(0, "USD", {"cents": 1, "dollars": 100})
        currency.currency_manager.currencies[1] = currency.Currency(1, "Imperial",
                                                                    {
                                                                        "bronze": 1,
                                                                        "silver": 1000,
                                                                        "gold": 1000000
                                                                    })

        i0 = item.Item("Generic Item", 0, {0: 10}, "A generic Item. It does nothing and is nothing.")
        i1 = item.Item("Item Number Two", 1, {0: 15}, "The second Item every created.")
        i2 = item.Item("Key", 2, {0: 1}, "A simple key.", max_quantity=1)

        item.item_manager.register_item(i0)
        item.item_manager.register_item(i1)
        item.item_manager.register_item(i2)

        shop_w = [0]
        shop = game.systems.room.action.shop_action.ShopAction("Something Something Shop", "You enter the shop",
                                                               wares=shop_w)

        get_cache()["player"] = Player(id=0, name="Player")
        p: Player = get_cache()["player"]
        p.coin_purse.adjust(0, 100)
        p.inventory.new_stack(1, 1)

        consume_event = ConsumeItemEvent(1, 1)
        consume_test = game.systems.room.action.actions.WrapperAction("Get robbed", "", consume_event)

        get_key_event = AddItemEvent(2, 1)
        get_key_action = game.systems.room.action.actions.WrapperAction("Inspect glinting object on the floor", "",
                                                                        get_key_event)
        key_req = ConsumeItemRequirement(2, 1)

        inventory_action = ViewInventoryAction()

        exit_r_1 = actions.ExitAction(1, requirement_list=[key_req])
        exit_r_0 = actions.ExitAction(0)

        r_0 = room.Room(name="A Debug Room",
                        action_list=[inventory_action, exit_r_1, consume_test, get_key_action],
                        enter_text="You enter a debug room",
                        rid=0)

        r_1 = room.Room(name="A Second Debug Room",
                        action_list=[inventory_action, exit_r_0, shop],
                        enter_text="You enter yet another debug room",
                        rid=1)
        room.room_manager.register_room(r_0)
        room.room_manager.register_room(r_1)

    def _load_assets(self) -> None:
        """
        A startup phase method that loads JSON assets from disk
        """

        # Get a list of all managers
        manager_keys: list[str] = list(from_cache('managers').keys())

        # Get an ordered list of available priorities in ascending order
        ordered_priorities = list(self.manager_load_priority)
        ordered_priorities.sort()

        # Starting from lowest, for each priority load the managers at that level
        for priority_level in ordered_priorities:
            logger.debug(f"Loading managers at [Priority {priority_level}]")
            for manager_key in self.manager_load_priority[priority_level]:
                logger.debug(f"[{manager_key}] Loading assets")
                from_cache(['managers', manager_key]).load()  # Fetch manager from cache and load
                manager_keys.remove(manager_key)  # Remove it from the list of remaining managers

        # For each manager that has no priority, load it
        if len(manager_keys) > 0:
            logger.debug("Loading un-prioritized Managers")
        for leftover_key in manager_keys:
            logger.debug(f"[{leftover_key}] Loading assets")
            from_cache(['managers', leftover_key]).load()  # Fetch from cache and load manager

    def _startup(self):
        """
        Perform required startup logic

        Returns: None
        """
        self._debug_init_early()
        logger.info("Engine::startup")
        logger.info("Loading config...")
        # Load config values from disk
        if os.path.exists(conf_path):

            # Load config data
            set_config(OmegaConf.load(conf_path))

        else:
            set_config(OmegaConf.create(self.get_default_conf()))
            self.write_conf()

        logger.info("Loading styles...")
        if os.path.exists(style_path):
            # Load style data
            raw_style = OmegaConf.load(conf_dir_path + style_file_path)
            register_arguments(raw_style.arguments)
            for style in raw_style.get("styles").items():
                register_style(*style)
        else:
            self.write_styles()
            raise IOError("No styles.yaml! Generating empty styles...")

        get_cache()["player_location"] = get_config()["room"]["default_id"]

        self._load_assets()

        logger.info("Engine::startup.done")
        self._debug_init_late()

    def _shutdown(self):
        """
        Perform required shutdown logic

        Returns: None
        """

        # Save state data to disk
        for manager in get_cache()['managers']:
            get_cache()['managers'][manager].save()

    def __init__(self):
        self._startup()  # Call startup logic.

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._shutdown()

    @staticmethod
    def get_default_conf() -> dict[str, any]:
        """

        Returns:

        """
        return {"io": {"save_data_path": "./saves", "asset_path": "./assets"},
                "inventory": {"default_capacity": 10},
                "room": {"default_id": 0}
                }

    def write_styles(self) -> None:
        """

        Returns: None
        """
        logger.info("Writing empty style file...")
        styles_empty = {"arguments": [],
                        "styles": {}
                        }

        if not os.path.exists(conf_dir_path):
            try:
                os.mkdir(conf_dir_path)
            except FileExistsError:
                logger.info("Config folder exists, skipping....")

            f = open(style_path, "x")
            f.close()
        OmegaConf.save(styles_empty, style_path)

    def write_conf(self) -> None:
        """

        Returns: None

        """
        logger.info("Writing default config...")
        if not get_config():
            raise ValueError("Engine::conf must not be None!")

        else:
            if not os.path.exists(conf_dir_path):
                try:
                    os.mkdir(conf_dir_path)
                except FileExistsError:
                    logger.info("Config folder exists, skipping....")

                f = open(conf_path, "x")
                f.close()
            OmegaConf.save(get_config(), conf_path)
