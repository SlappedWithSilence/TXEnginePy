import os.path

from .formatting import register_arguments, register_style
from .cache import get_config, set_config, get_cache

from loguru import logger
from omegaconf import OmegaConf, DictConfig

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
                "room" : {"default_id" : 0}
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
