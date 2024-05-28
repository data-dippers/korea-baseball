from enum import StrEnum
from typing import Literal

from abc import ABCMeta, abstractmethod

import pandas as pd
from pydantic import BaseModel, RootModel


class FieldType(StrEnum):
    """
    field type class
    """
    string = "STRING"
    bytes = "BYTES"
    integer = "INTEGER"
    float = "FLOAT"
    boolean = "BOOLEAN"
    timestamp = "TIMESTAMP"
    date = "DATE"
    time = "TIME"
    datetime = "DATETIME"
    geography = "GEOGRAPHY"
    numeric = "NUMBERIC"
    bignumeric = "BIGNUMERIC"
    json = "JSON"
    record = "RECORD"
    range = "RANGE"


class Column(BaseModel):
    """column class"""
    name: str
    type: FieldType


class Schema(RootModel):
    """schema class"""
    root: list[Column]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    @property
    def names(self) -> list[str]:
        return [column.name for column in self.root]

    def to_dict(self) -> list[dict[str, FieldType]]:
        return [column.model_dump() for column in self.root]


class BaseJob(metaclass=ABCMeta):
    """
    base job class

    :param project_id: The ID of the BiqQuery project.
    :param table_id: The ID of the BigQuery dataset table.
    :param schema: The schema of the BigQuery dataset table.
    :param chunk_size: Number of rows to be inserted in each chunk from dataframe.
        Set to None to load the whole dataframe at once.
    :param if_exists: Behavior when the table exists.
        'fail': If table exists raise pandas_gbq.gbq.TableCreationError.
        'replace': If table exists, drop it, recreate id, and insert data.
        'append': If table exists, insert data. Create if does not exist.
    """

    def __init__(
            self,
            project_id: str,
            table_id: str,
            schema: Schema,
            chunk_size: int | None = None,
            if_exists: Literal["fail", "replace", "append"] = "append"
    ):
        self.project_id = project_id
        self.table_id = table_id
        self.schema = schema
        self.chunk_size = chunk_size
        self.if_exists = if_exists

    def __repr__(self) -> str:
        return f"<cls:{self.__class__.__name__}>"

    @abstractmethod
    def sourcing(self) -> dict:
        pass

    @abstractmethod
    def transform(self, data: dict) -> pd.DataFrame:
        pass

    def sink(self, df: pd.DataFrame):
        df.to_gbq(
            destination_table=self.table_id,
            project_id=self.project_id,
            chunksize=self.chunk_size,
            if_exists=self.if_exists,
            table_schema=self.schema.to_dict()
        )

    def run(self):
        data = self.sourcing()
        df = self.transform(data)
        self.sink(df)
