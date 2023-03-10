import os.path

import game.systems.room.action.shop_action
from .formatting import register_arguments, register_style
from .cache import get_config, set_config, get_cache

from loguru import logger
from omegaconf import OmegaConf

from .systems import currency, room, item
from .systems.entity.entities import Player
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

        i0 = item.Item("Generic Item", 0, {0: 10}, "A generic Item. It does nothing and is nothing.")
        item.item_manager.register_item(i0)

        exit_r_1 = actions.ExitAction(1)
        exit_r_0 = actions.ExitAction(0)

        shop_w = [0]
        shop = game.systems.room.action.shop_action.ShopAction("Something Something Shop", "You enter the shop",
                                                               wares=shop_w)

        get_cache()["player"] = Player("Player", 0)
        p: Player = get_cache()["player"]
        p.coin_purse.gain(0, 100)

        inventory_action = ViewInventoryAction()

        r_0 = room.Room(name="A Debug Room", action_list=[inventory_action, exit_r_1], enter_text="You enter a debug room", id=0)
        r_1 = room.Room(name="A Second Debug Room", action_list=[inventory_action, exit_r_0, shop],
                        enter_text="You enter yet another debug room", id=1)
        room.room_manager.register_room(r_0)
        room.room_manager.register_room(r_1)

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

        logger.info("Engine::startup.done")
        self._debug_init_late()

    def _shutdown(self):
        """
        Perform required shutdown logic

        Returns: None

        """

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
