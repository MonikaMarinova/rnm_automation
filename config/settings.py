"""Central configuration. Every value has a default and can be overridden via an RM_* env var."""
import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def _env_optional_int(name: str) -> Optional[int]:
    value = os.getenv(name)
    return int(value) if value else None


def _env_optional_path(name: str) -> Optional[Path]:
    value = os.getenv(name)
    return Path(value) if value else None


@dataclass(frozen=True)
class Settings:
    # --- API ---
    base_url: str
    request_timeout: float          # seconds, applied to every HTTP call
    min_episode_characters: int     # task: episode must contain at least this many characters
    characters_to_select: int

    # --- UI ---
    google_url: str
    browser_language: str
    headless: bool
    ui_timeout: float               # explicit-wait timeout, seconds
    chrome_args: Tuple[str, ...]    # extra Chrome flags, e.g. RM_CHROME_ARGS="--no-sandbox" on CI
    chrome_profile_dir: Optional[Path]  # dedicated profile folder => cookies/consent survive between runs
    captcha_wait: float             # seconds to wait for a HUMAN to solve a CAPTCHA (120 = fail immediately)

    # --- Output ---
    output_dir: Path
    seed: Optional[int]             # fixed seed => reproducible random selection

    @property
    def screenshots_dir(self) -> Path:
        return self.output_dir / "screenshots"

    @property
    def intro_file(self) -> Path:
        return self.output_dir / "characters_introduction.txt"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=os.getenv("RM_BASE_URL", "https://rickandmortyapi.com/api"),
            request_timeout=float(os.getenv("RM_REQUEST_TIMEOUT", "10")),
            min_episode_characters=int(os.getenv("RM_MIN_EPISODE_CHARACTERS", "30")),
            characters_to_select=2,
            google_url=os.getenv("RM_GOOGLE_URL", "https://www.google.com/?hl=en"),
            browser_language=os.getenv("RM_BROWSER_LANGUAGE", "en"),
            headless=_env_bool("RM_HEADLESS", False),
            ui_timeout=float(os.getenv("RM_UI_TIMEOUT", "15")),
            chrome_args=tuple(shlex.split(os.getenv("RM_CHROME_ARGS", ""))),
            chrome_profile_dir=_env_optional_path("RM_CHROME_PROFILE_DIR"),
            captcha_wait=float(os.getenv("RM_CAPTCHA_WAIT", "120")),
            output_dir=Path(os.getenv("RM_OUTPUT_DIR", PROJECT_ROOT / "output")),
            seed=_env_optional_int("RM_SEED"),
        )


settings = Settings.from_env()
