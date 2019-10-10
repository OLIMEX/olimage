from dependency_injector import containers, providers

from olimage.core.parsers import Distributions, Images, Partitions, Users


class IocContainer(containers.DeclarativeContainer):
    distributions = providers.Singleton(Distributions)

    images = providers.Singleton(Images)

    partitions = providers.Singleton(Partitions)

    users = providers.Singleton(Users)


