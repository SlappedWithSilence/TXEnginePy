import os.path

from .formatting import register_arguments, register_style

from loguru import logger
from omegaconf import OmegaConf, DictConfig

conf_dir_path: str = "./config/"
conf_file_path: str = "conf.yaml"
style_file_path: str = "styles.yaml"
conf_path: str = conf_dir_path + conf_file_path


class Engine:

    def _debug_init_early(self) -> None:
        """
        A special function that runs before startup to supoprt debugging efforts.
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

        # Load config values from disk
        if os.path.exists(conf_dir_path):

            # Load config data
            self.conf = OmegaConf.load(conf_path)

            # Load style data
            raw_style = OmegaConf.load(conf_dir_path + style_file_path)
            register_arguments(raw_style.arguments)
            for style in raw_style.get("styles").items():
                register_style(*style)

        else:
            self.conf = OmegaConf.create(self.get_default_conf())
            self.write_conf()

        self._debug_init_late()

    def _shutdown(self):
        """
        Perform required shutdown logic

        Returns: None

        """

    def __init__(self):
        self.conf: DictConfig = None  # The global config. # TODO: Move to a package-level cache
        self.player_location: int = 0  # The player's location, as it relates to room ids
        self._startup()  # Call startup logic.

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._shutdown()

    @staticmethod
    def get_default_conf() -> dict[str, any]:
        """

        Returns:

        """
        return {"io": {"save_data_path": "./saves", "asset_path": "./assets"},
                "inventory": {"default_capacity": 10}}

    def write_conf(self) -> None:
        """

        Returns:

        """
        if not self.conf:
            raise ValueError("Engine::conf must not be None!")

        else:
            if not os.path.exists(conf_dir_path):
                try:
                    os.mkdir(conf_dir_path)
                except FileExistsError:
                    logger.info("Config folder exists, skipping....")

                f = open(conf_path, "x")
                f.close()
            OmegaConf.save(self.conf, conf_path)
