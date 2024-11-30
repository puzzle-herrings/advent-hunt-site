from bs4 import BeautifulSoup
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone
import pytest

from huntsite.puzzles.factories import PuzzleFactory
from huntsite.teams.factories import UserFactory
from huntsite.tester_utils.factories import OrganizerDashboardPermissionFactory
from huntsite.tester_utils.session_handlers import (
    TIME_TRAVEL_SESSION_VAR,
    read_time_travel_session_var,
)

pytestmark = pytest.mark.django_db


def test_tester_controls_in_views(client):
    """Tester controls should only appear for a user with the is_tester flag set."""
    puzzle = PuzzleFactory()

    # Anonymous user
    for url in (reverse("home"), reverse("puzzle_list")):
        response = client.get(url)
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        assert not soup.find("div", class_="tester-controls-container")

    # Regular user
    user = UserFactory()
    client.force_login(user)
    for url in (reverse("home"), reverse("puzzle_list"), puzzle.get_absolute_url()):
        response = client.get(url)
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        assert not soup.find("div", class_="tester-controls-container")

    # Test user
    tester = UserFactory(is_tester=True)
    client.force_login(tester)
    for url in (reverse("home"), reverse("puzzle_list"), puzzle.get_absolute_url()):
        response = client.get(url)
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.find("div", class_="tester-controls-container")


def test_time_travel_view(client):
    user = UserFactory(is_tester=True)
    client.force_login(user)

    puzzle = PuzzleFactory(
        title="Future Puzzle", available_at=timezone.now() + timezone.timedelta(days=1)
    )

    # Puzzle is not available yet
    response = client.get(reverse("puzzle_list"))
    assert response.status_code == 200
    assert puzzle.title not in response.content.decode()

    # Time travel to the future
    time_travel_to = (timezone.now() + timezone.timedelta(days=2)).replace(microsecond=0)
    time_travel_to_str = time_travel_to.strftime("%Y-%m-%d %H:%M:%S")
    response = client.post(
        reverse("time_travel"),
        {"time_travel_to": time_travel_to_str},
    )
    assert response.status_code == 200
    assert response["HX-Refresh"] == "true"
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "Time travel successful."
    assert client.session[TIME_TRAVEL_SESSION_VAR] == time_travel_to.isoformat(timespec="seconds")

    response = client.get(reverse("puzzle_list"))
    assert response.status_code == 200
    assert read_time_travel_session_var(response.wsgi_request) == time_travel_to
    assert puzzle.title in response.content.decode()


def test_organizer_dashboard_view(client):
    # Anonymous user should get 404
    response = client.get(reverse("organizer_dashboard"))
    assert response.status_code == 404

    # Regular user should get 404
    user = UserFactory()
    client.force_login(user)
    response = client.get(reverse("organizer_dashboard"))
    assert response.status_code == 404

    # User with permissions should be able to access
    OrganizerDashboardPermissionFactory(user=user)
    response = client.get(reverse("organizer_dashboard"))
    assert response.status_code == 200
