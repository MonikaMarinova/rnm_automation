"""Character domain model."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from config.settings import settings

_REQUIRED_KEYS = ("id", "name")


@dataclass(frozen=True)
class Location:
    """A place as the API describes it. `url` is empty for 'unknown' places."""
    name: str
    url: str = ""

    @classmethod
    def from_api(cls, data: Optional[Dict[str, Any]]) -> "Location":
        data = data or {}
        return cls(name=data.get("name", ""), url=data.get("url", ""))


@dataclass(frozen=True)
class Character:
    id: int
    name: str
    status: str
    species: str
    type: str
    gender: str
    origin: Location
    location: Location
    image: str
    episode_urls: Tuple[str, ...]
    url: str
    created: str

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Character":
        """Build a Character from one API character object. Fails loudly if id/name are missing."""
        missing = [key for key in _REQUIRED_KEYS if key not in data]
        if missing:
            raise ValueError(f"Character payload is missing {missing}: {data!r:.200}")
        return cls(
            id=int(data["id"]),
            name=data["name"],
            status=data.get("status", ""),
            species=data.get("species", ""),
            type=data.get("type", ""),
            gender=data.get("gender", ""),
            origin=Location.from_api(data.get("origin")),
            location=Location.from_api(data.get("location")),
            image=data.get("image", ""),
            episode_urls=tuple(data.get("episode", ())),
            url=data.get("url", ""),
            created=data.get("created", ""),
        )

    def introduction(self) -> str:
        """The friendly one-liner. 'From' is the character's ORIGIN (matches the task's example)."""
        return f"Hi! I'm {self.name}, My ID is {self.id}, I'm from {self.origin.name}."

    def hello(self, path: Optional[Path] = None, *, append: bool = True) -> str:
        """Write the introduction to `path` (default: characters_introduction.txt) and return it.

        Appends by default so several characters can share one file; the caller decides when
        to start a fresh file (e.g. once per test session).
        """
        target = Path(path) if path else settings.intro_file
        target.parent.mkdir(parents=True, exist_ok=True)
        line = self.introduction()
        with target.open("a" if append else "w", encoding="utf-8") as handle:
            handle.write(line + "\n")
        return line