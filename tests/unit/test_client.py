"""Client tests run against a fake session: no network, fully deterministic."""
import pytest
import requests

from src.api.client import ApiError, RickAndMortyClient


class FakeResponse:
    def __init__(self, payload=None, status=200, text=""):
        self._payload, self.status_code, self.text = payload, status, text
        self.ok = status < 400

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeSession:
    """Maps URL -> response (or exception) and records every call."""
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, timeout=None):
        self.calls.append(url)
        result = self.routes[url]
        if isinstance(result, Exception):
            raise result
        return result

    def close(self):
        pass


BASE = "https://api.test/api"


def make_client(routes):
    session = FakeSession(routes)
    return RickAndMortyClient(BASE, session=session), session


@pytest.mark.unit
def test_get_episodes_follows_pagination():
    client, session = make_client({
        f"{BASE}/episode": FakeResponse({"info": {"next": f"{BASE}/episode?page=2"}, "results": [{"id": 1}]}),
        f"{BASE}/episode?page=2": FakeResponse({"info": {"next": None}, "results": [{"id": 2}, {"id": 3}]}),
    })
    assert [e["id"] for e in client.get_episodes()] == [1, 2, 3]
    assert len(session.calls) == 2


@pytest.mark.unit
def test_get_characters_uses_single_request_for_many_ids():
    client, session = make_client({f"{BASE}/character/12,345": FakeResponse([{"id": 12}, {"id": 345}])})
    assert [c["id"] for c in client.get_characters([12, 345])] == [12, 345]
    assert session.calls == [f"{BASE}/character/12,345"]


@pytest.mark.unit
def test_get_characters_normalizes_single_object_to_list():
    """The API returns a bare object (not a list) when only one id is requested."""
    client, _ = make_client({f"{BASE}/character/5": FakeResponse({"id": 5})})
    assert client.get_characters([5]) == [{"id": 5}]


@pytest.mark.unit
def test_get_characters_deduplicates_ids():
    client, session = make_client({f"{BASE}/character/5": FakeResponse({"id": 5})})
    client.get_characters([5, 5])
    assert session.calls == [f"{BASE}/character/5"]


@pytest.mark.unit
def test_get_characters_requires_ids():
    client, _ = make_client({})
    with pytest.raises(ValueError):
        client.get_characters([])


@pytest.mark.unit
def test_get_characters_detects_short_response():
    client, _ = make_client({f"{BASE}/character/1,2": FakeResponse([{"id": 1}])})
    with pytest.raises(ApiError, match="unexpected response"):
        client.get_characters([1, 2])


@pytest.mark.unit
@pytest.mark.parametrize("route", [
    FakeResponse(status=404, text='{"error":"Character not found"}'),
    FakeResponse(payload=None, status=200, text="<html>"),
    requests.ConnectionError("boom"),
])
def test_failures_are_wrapped_in_api_error(route):
    client, _ = make_client({f"{BASE}/character/1": route})
    with pytest.raises(ApiError):
        client.get_characters([1])


@pytest.mark.unit
def test_get_characters_detects_wrong_ids():
    client, _ = make_client({f"{BASE}/character/1,2": FakeResponse([{"id": 1}, {"id": 3}])})
    with pytest.raises(ApiError, match="got"):
        client.get_characters([1, 2])
