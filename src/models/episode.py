"""Episode domain model."""
from dataclasses import dataclass
from typing import Any, Dict, Tuple


def id_from_url(url: str) -> int:
    """'https://.../api/character/42' -> 42."""
    try:
        return int(url.rstrip("/").rsplit("/", 1)[-1])
    except ValueError as exc:
        raise ValueError(f"Cannot extract a numeric id from URL: {url!r}") from exc


@dataclass(frozen=True)
class Episode:
    id: int
    name: str
    code: str                       # e.g. "S01E01"
    air_date: str
    character_ids: Tuple[int, ...]

    @property
    def character_count(self) -> int:
        return len(self.character_ids)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Episode":
        """Episodes only carry character URLs; we keep just the ids (enough for one batch request)."""
        ids = dict.fromkeys(id_from_url(url) for url in data.get("characters", ()))
        return cls(id=int(data["id"]), name=data["name"], code=data.get("episode", ""),
                   air_date=data.get("air_date", ""), character_ids=tuple(ids))