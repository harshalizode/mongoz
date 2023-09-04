import asyncio
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple, Union

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from mongoz.core.connection.database import Database


class Registry:
    """
    MongoDB client object referencing the Async Motor Client
    """

    def __init__(
        self,
        url: str,
        database: Database,
        event_loop: Union[Callable[[], asyncio.AbstractEventLoop], None] = None,
    ) -> None:
        self.event_loop = event_loop or asyncio.get_event_loop
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(url)
        self._client.get_io_loop = self.event_loop

        assert isinstance(
            database, Database
        ), "`database` must be an instance of mongoz.core.connection.database.Database"
        self._database = database

    @property
    def address(self) -> Tuple[str, int]:
        """
        Returns the address of the client
        """
        return self._client.address

    @property
    def host(self) -> str:
        return self._client.HOST

    @property
    def port(self) -> str:
        return self._client.PORT

    async def drop_database(self, database: Union[str, Database]) -> None:
        """
        Drops an existing mongo db database/
        """
        if not isinstance(database, Database):
            await self._client.drop_database(database)
        else:
            await self._client.drop_database(database._db)

    def get_database(self, name: str) -> Database:
        database = self._client.get_database(name)
        return Database(name=name, database=database)

    async def get_databases(self) -> Sequence[Database]:
        databases = await self._client.list_database_names()
        return list(map(self.get_database, databases))
