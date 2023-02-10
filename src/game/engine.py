import os.path

from loguru import logger
from omegaconf import OmegaConf, DictConfig

conf_dir_path: str = "./config/"
conf_file_path: str = "conf.yaml"
conf_path: str = conf_dir_path + conf_file_path


class Engine:

    def _startup(self):
        """
        Perform required startup logic

        Returns: None
        """

        # Load config values
        if os.path.exists(conf_dir_path):
            self.conf = OmegaConf.load(conf_path)

        else:
            self.conf = OmegaConf.create(self.get_default_conf())
            self.write_conf()

    def _shutdown(self):
        """
        Perform required shutdown logic

        Returns: None

        """

    def __init__(self):
        self.conf: DictConfig = None
        self._startup()

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
