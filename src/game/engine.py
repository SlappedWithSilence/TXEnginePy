import os.path

from .structures.messages import Frame
from ..game import game_state_controller

from omegaconf import OmegaConf, DictConfig

conf_path: str = "./config/conf.yaml"


class Engine:

    def _startup(self):
        """
        Perform required startup logic

        Returns: None
        """

        # Load config values
        if os.path.exists(conf_path):
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
    def get_frame() -> Frame:
        """

        Returns:

        """
        return game_state_controller.get_current_frame()

    @staticmethod
    def submit(user_input: any) -> bool:
        """

        Args:
            user_input:

        Returns:

        """
        return game_state_controller.deliver_input(user_input)

    @staticmethod
    def get_default_conf() -> dict[str, any]:
        """

        Returns:

        """
        return {"io": {"save_data_path": "./saves", "asset_path": "./assets"}}

    def write_conf(self) -> None:
        """

        Returns:

        """
        if not self.conf:
            raise ValueError("Engine::conf must not be None!")

        else:
            OmegaConf.save(self.conf, conf_path)
