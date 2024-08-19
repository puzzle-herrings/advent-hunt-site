from bs4 import BeautifulSoup
from django.conf import settings
from django.test import Client
from django.utils import timezone
import pytest

from huntsite.puzzles.factories import MetapuzzleInfoFactory, PuzzleFactory
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Advent Puzzle Hunt" in response.content.decode()

    user = UserFactory()
    client.force_login(user)
    response = client.get("/")
    assert response.status_code == 200
    assert "Advent Puzzle Hunt" in response.content.decode()


def test_navbar(client):
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    navbar = soup.find("nav")
    assert "Advent Hunt" in navbar.text
    assert "Login" in navbar.text
    assert "Register" in navbar.text

    user = UserFactory(team_name="Test Herrings 🎏")
    client.force_login(user)
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    navbar = soup.find("nav")
    assert "Advent Hunt" in navbar.text
    assert "Test Herrings 🎏" in navbar.text
    assert "Logout" in navbar.text


def test_santa_missing(monkeypatch):
    """Favicon and Navbar logo should change based on the HUNT_IS_LIVE_DATETIME setting."""

    # Set up users
    anon_client = Client()
    user1 = UserFactory()
    user1_client = Client()
    user1_client.force_login(user1)
    user2 = UserFactory()
    user2_client = Client()
    user2_client.force_login(user2)

    ## Before changeover date, normal santa
    monkeypatch.setattr(
        settings, "HUNT_IS_LIVE_DATETIME", timezone.now() + timezone.timedelta(days=1)
    )
    for client in (anon_client, user1_client, user2_client):
        response = client.get("/")
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        # Favicon
        header = soup.find("head")
        assert "static/santa/" in str(header)
        assert "static/santa-missing" not in str(header)
        # Navbar logo
        navbar = soup.find("div", class_="navbar-brand")
        assert "static/santa/" in navbar.img["src"]
        assert "static/santa-missing" not in navbar.img["src"]

    ## After changeover date, santa missing
    monkeypatch.setattr(
        settings, "HUNT_IS_LIVE_DATETIME", timezone.now() - timezone.timedelta(days=1)
    )
    # But user1 finishes the hunt, Santa is back
    final_puzzle = PuzzleFactory()
    MetapuzzleInfoFactory(puzzle=final_puzzle, is_final=True)
    assert not user1.is_finished
    guess_submit(final_puzzle, user=user1, guess_text=final_puzzle.answer)
    assert user1.is_finished
    assert not user2.is_finished

    for client in (anon_client, user2_client):
        response = client.get("/")
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        # Favicon
        header = soup.find("head")
        assert "static/santa/" not in str(header)
        assert "static/santa-missing" in str(header)
        # Navbar logo
        navbar = soup.find("div", class_="navbar-brand")
        assert "static/santa/" not in navbar.img["src"]
        assert "static/santa-missing" in navbar.img["src"]

    response = user1_client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    # Favicon
    header = soup.find("head")
    assert "static/santa/" in str(header)
    assert "static/santa-missing" not in str(header)
    # Navbar logo
    navbar = soup.find("div", class_="navbar-brand")
    assert "static/santa/" in navbar.img["src"]
    assert "static/santa-missing" not in navbar.img["src"]
