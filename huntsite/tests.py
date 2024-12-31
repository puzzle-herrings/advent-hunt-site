from bs4 import BeautifulSoup
from django.conf import settings
from django.test import Client, RequestFactory
from django.utils import timezone
from metadata_parser import MetadataParser
import pytest

from huntsite.puzzles.factories import MetapuzzleInfoFactory, PuzzleFactory
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory
from huntsite.teams.models import AnonymousUser
from huntsite.utils import HuntState, get_hunt_state

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


def test_hunt_state(settings):
    request_factory = RequestFactory()

    # Prehunt
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() + timezone.timedelta(days=1)
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() + timezone.timedelta(days=2)
    request = request_factory.get("/")
    request.user = AnonymousUser()
    assert get_hunt_state(request) == HuntState.PREHUNT

    # Live
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() - timezone.timedelta(days=2)
    request = request_factory.get("/")
    request.user = AnonymousUser()
    assert get_hunt_state(request) == HuntState.LIVE

    # Ended
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() - timezone.timedelta(days=1)
    request = request_factory.get("/")
    request.user = AnonymousUser()
    assert get_hunt_state(request) == HuntState.ENDED


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


def test_navbar_hunt_ended(client, settings):
    """Navbar should not have any account-related options if hunt is ended."""
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() - timezone.timedelta(days=2)
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() - timezone.timedelta(days=1)

    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    navbar = soup.find("nav")
    assert "Advent Hunt" in navbar.text
    assert "Login" not in navbar.text
    assert "Register" not in navbar.text

    user = UserFactory(team_name="Test Herrings 🎏")
    client.force_login(user)
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    navbar = soup.find("nav")
    assert "Advent Hunt" in navbar.text
    assert "Test Herrings 🎏" not in navbar.text
    assert "Logout" not in navbar.text


def test_santa_missing(monkeypatch):
    """Favicon and Navbar logo should change based on the hunt state."""

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


def test_santa_missing_og_image(client, monkeypatch):
    """The og:image meta tag should change based on the HUNT_IS_LIVE_DATETIME setting."""

    monkeypatch.setattr(
        settings, "META_OG_IMAGE_PREHUNT", "https://example.com/og_image_prehunt.png"
    )
    monkeypatch.setattr(settings, "META_OG_IMAGE", "https://example.com/og_image.png")
    ## Before changeover date, normal santa
    monkeypatch.setattr(
        settings, "HUNT_IS_LIVE_DATETIME", timezone.now() + timezone.timedelta(days=1)
    )

    response = client.get("/")
    assert response.status_code == 200
    meta_parser = MetadataParser(html=response.content.decode())
    assert meta_parser.get_metadata_link("image") == "https://example.com/og_image_prehunt.png"

    ## After changeover date, santa missing
    monkeypatch.setattr(
        settings, "HUNT_IS_LIVE_DATETIME", timezone.now() - timezone.timedelta(days=1)
    )
    response = client.get("/")
    assert response.status_code == 200
    meta_parser = MetadataParser(html=response.content.decode())
    assert meta_parser.get_metadata_link("image") == "https://example.com/og_image.png"


def test_announcement_message(client, monkeypatch):
    monkeypatch.setattr(settings, "ANNOUNCEMENT_MESSAGE", None)
    assert settings.ANNOUNCEMENT_MESSAGE is None

    message = "This is an announcement message."

    response = client.get("/")
    assert response.status_code == 200
    assert not response.context.get("ANNOUNCEMENT_MESSAGE")
    assert message not in response.content.decode()

    monkeypatch.setattr(settings, "ANNOUNCEMENT_MESSAGE", message)
    response = client.get("/")
    assert response.status_code == 200
    assert response.context.get("ANNOUNCEMENT_MESSAGE") == message
    assert message in response.content.decode()


def test_discord_server_link(monkeypatch):
    monkeypatch.setattr(settings, "DISCORD_SERVER_LINK", None)
    assert settings.DISCORD_SERVER_LINK is None

    # Set up users
    anon_client = Client()
    user1 = UserFactory()
    user1_client = Client()
    user1_client.force_login(user1)

    # No discord server link, neither in context nor in navbar
    for user in (anon_client, user1_client):
        response = user.get("/")
        assert response.status_code == 200
        assert not response.context.get("DISCORD_SERVER_LINK")
        soup = BeautifulSoup(response.content, "html.parser")
        assert not soup.find("a", attrs={"id": "discord-server-link"})

    # Set discord server link
    monkeypatch.setattr(settings, "DISCORD_SERVER_LINK", "https://example.com/discord")

    # Anon user still does not see, but it's in context
    response = anon_client.get("/")
    assert response.status_code == 200
    assert response.context.get("DISCORD_SERVER_LINK")
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find("a", attrs={"id": "discord-server-link"})

    # Logged in user sees
    response = user1_client.get("/")
    assert response.status_code == 200
    assert response.context.get("DISCORD_SERVER_LINK")
    soup = BeautifulSoup(response.content, "html.parser")
    assert soup.find("a", attrs={"id": "discord-server-link"})
