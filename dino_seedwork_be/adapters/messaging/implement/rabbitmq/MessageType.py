from enum import Enum

__all__ = ["MessageType"]


class MessageType(Enum):
    BINARY = "BINARY"
    TEXT = "TEXT"
