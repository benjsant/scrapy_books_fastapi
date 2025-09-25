import pytest
from app.utils.randomizer import choose_random_tags, sample_tracks


def test_choose_random_tags_empty():
    assert choose_random_tags("") == ""


def test_choose_random_tags_none():
    # Handle None input gracefully
    assert choose_random_tags(None) == ""


def test_choose_random_tags_single():
    assert choose_random_tags("magic") == "magic"


def test_choose_random_tags_multiple(monkeypatch):
    tags = "magic fantasy dark medieval epic"

    # Force random.sample to return predictable output
    monkeypatch.setattr("random.sample", lambda lst, n: lst[:n])

    result = choose_random_tags(tags, max_tags=3)
    assert result == "magic fantasy dark"


def test_sample_tracks_empty():
    assert sample_tracks([], 10) == []


def test_sample_tracks_less_than_limit():
    tracks = [{"id": 1}, {"id": 2}]
    assert sample_tracks(tracks, 5) == tracks


def test_sample_tracks_equal_to_limit():
    tracks = [{"id": i} for i in range(5)]
    result = sample_tracks(tracks, 5)
    assert result == tracks


def test_sample_tracks_more_than_limit(monkeypatch):
    tracks = [{"id": i} for i in range(1, 11)]

    # Force deterministic random
    monkeypatch.setattr("random.sample", lambda lst, n: lst[:n])

    result = sample_tracks(tracks, 5)
    assert len(result) == 5
    assert result == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
