"""Thin HTTP client for the Rick and Morty API.

Responsibility: HTTP only (URLs, pagination, retries, error mapping).
It returns raw JSON dicts; turning them into domain objects is the model's job.
"""
from typing import Any, Dict, List, Optional, Sequence

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings
from src.utils.logger import get_logger

log = get_logger("api")


class ApiError(Exception):
    """Raised for any failed API interaction (network, HTTP status, bad JSON, unexpected payload)."""


class RickAndMortyClient:
    def __init__(self, base_url: str, timeout: float = 10.0,
                 session: Optional[requests.Session] = None, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or self._build_session(max_retries)

    @classmethod
    def from_settings(cls) -> "RickAndMortyClient":
        return cls(base_url=settings.base_url, timeout=settings.request_timeout)

    @staticmethod
    def _build_session(max_retries: int) -> requests.Session:
        """Session with connection reuse and retry/backoff for rate limits and transient 5xx."""
        retry = Retry(total=max_retries, backoff_factor=0.5, allowed_methods=("GET",),
                      status_forcelist=(429, 500, 502, 503, 504), respect_retry_after_header=True)
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    # ------------------------------------------------------------------ public API

    def get_episodes(self) -> List[Dict[str, Any]]:
        """Return ALL episodes, following the `info.next` pagination links."""
        episodes: List[Dict[str, Any]] = []
        url: Optional[str] = f"{self.base_url}/episode"
        while url:
            payload = self._get(url)
            try:
                episodes.extend(payload["results"])
                url = payload["info"]["next"]
            except (KeyError, TypeError) as exc:
                raise ApiError(f"Unexpected episode page format from {url}: {payload!r:.200}") from exc
        log.info("Fetched %d episodes", len(episodes))
        return episodes

    def get_characters(self, ids: Sequence[int]) -> List[Dict[str, Any]]:
        """Fetch several characters in ONE request (`/character/1,2,3`).

        The API returns a list for several ids but a bare object for a single id;
        this method always returns a list.
        """
        unique_ids = list(dict.fromkeys(ids))  # de-duplicate, keep order
        if not unique_ids:
            raise ValueError("At least one character id is required")
        payload = self._get(f"{self.base_url}/character/{','.join(str(i) for i in unique_ids)}")
        characters = [payload] if isinstance(payload, dict) else payload
        if not isinstance(characters, list) or len(characters) != len(unique_ids):
            raise ApiError(f"Requested {len(unique_ids)} characters {unique_ids}, "
                           f"got an unexpected response: {payload!r:.200}")
        return characters

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "RickAndMortyClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    # ------------------------------------------------------------------ internals

    def _get(self, url: str) -> Any:
        log.debug("GET %s", url)
        try:
            response = self._session.get(url, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ApiError(f"GET {url} failed: {exc}") from exc
        if not response.ok:
            raise ApiError(f"GET {url} returned HTTP {response.status_code}: {response.text[:200]}")
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"GET {url} returned invalid JSON: {response.text[:200]}") from exc