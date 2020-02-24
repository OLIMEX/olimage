from .loading import BoardLoading
from .model import BoardModel


class Board(object):
    """
    Parse board with all it's modules
    """
    def __init__(self, name, data) -> None:
        self._name = name
        self._data = data

        # Create variants
        self._default = None
        self._loading = BoardLoading(data['loading'])
        self._models = []
        for key, value in data['models'].items():
            self._models.append(BoardModel(key, value))

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
    def default(self) -> str:
        """
        Get default setting. Used when there is no model specified

        :return: string name
        """
        if 'default' in self._data:
            return self._data['default']

        return None

    @property
    def loading(self) -> BoardLoading:
        return self._loading

    @property
    def models(self) -> [BoardModel]:
        """
        Get all models of the board

        :return: board models
        """
        return self._models

    @property
    def name(self) -> str:
        """
        Get board common name

        :return: name string
        """
        if 'name' in self._data:
            return self._data['name']

        return None

    @property
    def soc(self) -> str:
        """
        Get board SoC

        :return: board soc
        """
        return self._data['soc']

    @property
    def target(self) -> BoardModel:
        """
        Get the target model

        :return: target model
        """
        return self._default

    @target.setter
    def target(self, model: BoardModel) -> None:
        """
        Set the target model
        
        :param model: target model
        :return: None
        """
        self._default = model
