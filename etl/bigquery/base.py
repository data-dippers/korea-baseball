from typing import Literal

from abc import ABCMeta, abstractmethod

import pandas as pd
from google.cloud import bigquery
from pandas import DataFrame


class BaseJob(metaclass=ABCMeta):
    """
    base job class for bigquery etl
    """

    def __init__(
        self,
        destination_table: str,
        if_exists: Literal["fail", "replace", "append"],
    ):
        self.destination_table = destination_table
        self.if_exists = if_exists

    @abstractmethod
    def extract(self) -> dict:
        pass

    @abstractmethod
    def transform(self, data: dict) -> DataFrame:
        pass

    @abstractmethod
    def define(self) -> list[dict[str, str]]:
        pass


    def load(self, df: DataFrame, table_schema: list[dict[str, str]]):
        df.to_gbq(
            destination_table=self.destination_table,
            if_exists=self.if_exists,
            table_schema=table_schema
        )

    def run(self):
        data = self.extract()
        df = self.transform(data)
        schema = self.define()
        self.load(df, schema)
