from .model import Model


class Board(object):
    """
    Parse board with all it's modules
    """
    def __init__(self, name, data) -> None:
        self._name = name
        self._data = data

        # Create variants
        self._default = None
        self._models = []
        for key, value in data['models'].items():
            self._models.append(Model(key, value))

    def __str__(self) -> str:
        """
        Get board name

        :return: board name
        """
        return self._name

    @property
    def arch(self) -> str:
        """
        Get board architecture, e.g. armhf, arm64, etc...

        :return: board arch
        """
        return self._data['arch']

    @property
    def soc(self) -> str:
        """
        Get board SoC

        :return: board soc
        """
        return self._data['soc']

    @property
    def models(self) -> [Model]:
        """
        Get all models of the board

        :return: board models
        """
        return self._models

    @property
    def target(self) -> Model:
        """
        Get the target model

        :return: target model
        """
        return self._default

    @target.setter
    def target(self, model: Model) -> None:
        """
        Set the target model
        
        :param model: target model
        :return: None
        """
        self._default = model
