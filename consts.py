from enum import StrEnum
from functools import lru_cache


class Extensions(StrEnum):
    PLAYLIST = 'm3u8'
    SEGMENT = 'ts'
    SUBTITLES = 'srt'
    KEY = 'key'

    @classmethod
    @lru_cache
    def get_all(cls) -> set[bytes]:
        return {e.value.encode() for e in cls}
