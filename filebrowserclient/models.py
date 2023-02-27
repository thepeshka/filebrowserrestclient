from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Sorting(BaseModel):
    by: str
    asc: bool


class Permissions(BaseModel):
    admin: bool
    execute: bool
    create: bool
    rename: bool
    modify: bool
    delete: bool
    share: bool
    download: bool


class User(BaseModel):
    id: int
    username: str
    password: str
    scope: str
    locale: str
    lock_password: bool = Field(alias="singleClick")
    viewMode: str
    single_click: bool = Field(alias="singleClick")
    perm: Permissions
    commands: List[str]
    sorting: Sorting
    rules: List[str]
    hide_dotfiles: bool = Field(alias="hideDotfiles")
    date_format: bool = Field(alias="dateFormat")


class Share(BaseModel):
    hash: str
    path: str
    user_id: int = Field(alias="userID")
    expire: int
    password_hash: Optional[str]


class Units(str, Enum):
    SECONDS = 'seconds'
    MINUTES = 'minutes'
    HOURS = 'hours'
    DAYS = 'days'


class CreateShare(BaseModel):
    password: str = ""
    expires: str
    unit: Units


class Item(BaseModel):
    path: str
    name: str
    size: int
    extension: str
    modified: datetime
    mode: int
    is_dir: bool = Field(alias="isDir")
    is_symlink: bool = Field(alias="isSymlink")
    type: str


class Resources(Item):
    items: List[Item]
    num_dirs: int = Field(alias="numDirs")
    num_files: int = Field(alias="numFiles")
    sorting: Sorting
