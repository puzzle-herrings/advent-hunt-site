from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Advent Puzzle Hunt" in response.content


def test_santa_missing(client, monkeypatch):
    """Favicon and Navbar logo should change based on the SANTA_MISSING_DATETIME setting."""
    # Before changeover date, normal santa
    monkeypatch.setattr(
        settings, "SANTA_MISSING_DATETIME", timezone.now() + timezone.timedelta(days=1)
    )
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    header = soup.find("head")
    assert "static/santa/" in str(header)
    assert "static/santa-missing" not in str(header)
    navbar = soup.find("div", class_="navbar-brand")
    assert "static/santa/" in navbar.img["src"]
    assert "static/santa-missing" not in navbar.img["src"]

    # After changeover date, santa missing
    monkeypatch.setattr(
        settings, "SANTA_MISSING_DATETIME", timezone.now() - timezone.timedelta(days=1)
    )
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    header = soup.find("head")
    assert "static/santa/" not in str(header)
    assert "static/santa-missing" in str(header)
    navbar = soup.find("div", class_="navbar-brand")
    assert "static/santa/" not in navbar.img["src"]
    assert "static/santa-missing" in navbar.img["src"]
