"""
Generated by 'esmerald createproject'
"""
from functools import cached_property
from typing import Optional

from esmerald.conf.enums import EnvironmentType
from esmerald.conf.global_settings import EsmeraldAPISettings

from mongoz import Registry


class AppSettings(EsmeraldAPISettings):
    app_name: str = "My application in production mode."
    environment: Optional[str] = EnvironmentType.PRODUCTION
    secret_key: str = "esmerald-insecure-h35r*b9$+hw-x2hnt5c)vva=!zn$*a7#"  # auto generated

    @cached_property
    def db_connection(self) -> Registry:
        """
        To make sure the registry and the database connection remains the same
        all the time, always use the cached_property.
        """
        database = "mongodb://root:mongoadmin@localhost:27017"
        return Registry(database=database)
