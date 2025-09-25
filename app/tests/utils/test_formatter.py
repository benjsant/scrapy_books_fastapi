"""
Unit tests for utility functions in the formatter module.

Covers normalization of license URLs and transformation of raw Jamendo data
into structured response objects.
"""

import pytest
from app.utils.formatter import normalize_license_url, format_jamendo_track


def test_normalize_license_url_removes_region():
    """
    Ensure that the license URL normalization removes any regional suffixes.
    """
    url = "http://creativecommons.org/licenses/by/4.0/be/"
    expected = "https://creativecommons.org/licenses/by/4.0/"
    assert normalize_license_url(url) == expected


def test_normalize_license_url_empty():
    """
    Ensure that an empty URL returns an empty string.
    """
    assert normalize_license_url("") == ""


def test_format_jamendo_track_minimal_data():
    """
    Ensure that format_jamendo_track correctly formats a track with minimal data.
    """
    raw_track = {
        "id": "123",
        "name": "Test Track",
        "artist_name": "Test Artist",
        "audio": "https://audio.com/test.mp3",
        "duration": 300,
        "license_ccurl": "https://creativecommons.org/licenses/by/4.0/",
        "musicinfo": {"tags": {"vartags": ["ambient"]}},
        "album_image": "https://image.jpg"
    }

    formatted = format_jamendo_track(raw_track)
    assert formatted["id"] == "123"
    assert formatted["license_name"] == "CC BY 4.0"
