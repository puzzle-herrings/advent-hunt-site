from bs4 import BeautifulSoup
from django.utils import timezone
import pytest

from huntsite.puzzles.factories import ErratumFactory, PuzzleFactory
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_puzzle_list_view(client):
    """Puzzle list view displays only available puzzles in calendar and in list table."""

    puzzles = [
        PuzzleFactory(
            calendar_entry__day=i,
            available_at=timezone.now() + timezone.timedelta(days=i - 2.5),
        )
        for i in range(4)
    ]

    response = client.get("/puzzles/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    puzzle_list_table = soup.find("table", id="puzzle-list")

    # Only puzzles 0, 1, 2 should be displayed in calendar
    for i in (0, 1, 2):
        calendar_cell = soup.find("div", id=f"calendar-cell-{i}")
        assert "available" in calendar_cell.find("div").attrs.get("class")
        assert puzzles[i].title in calendar_cell.text
        assert puzzles[i].title in puzzle_list_table.text

    # Puzzle 3 should not be displayed in calendar
    calendar_cell = soup.find("div", id="calendar-cell-3")
    assert "unavailable" in calendar_cell.find("div").attrs.get("class")
    assert puzzles[3].title not in calendar_cell.text
    assert puzzles[3].title not in puzzle_list_table.text


def test_puzzle_detail_errata(client):
    """Errata display correctly on puzzle detail page."""
    puzzle = PuzzleFactory()

    user = UserFactory()
    client.force_login(user)

    # No errata
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find(id="errata")

    # Add one errata
    erratum1 = ErratumFactory(
        puzzle=puzzle, published_at=timezone.now() - timezone.timedelta(days=2)
    )
    assert erratum1 in puzzle.errata.all()
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    card = soup.find(id="errata")
    assert card
    header = card.find(class_="card-header")
    assert header
    assert "Errata (1)" in header.text
    assert erratum1.published_at.isoformat() in header.text
    entries = card.find(class_="card-content").find_all("p")
    assert len(entries) == 1
    assert erratum1.published_at.isoformat() in entries[0].text
    assert erratum1.text in entries[0].text

    ## Add second newer erratum
    erratum2 = ErratumFactory(
        puzzle=puzzle, published_at=timezone.now() - timezone.timedelta(days=1)
    )
    assert set(puzzle.errata.all()) == {erratum2, erratum1}
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    card = soup.find(id="errata")
    assert card
    header = card.find(class_="card-header")
    assert header
    assert "Errata (2)" in header.text
    # timestamp of newest erratum2 should be in header
    assert erratum2.published_at.isoformat() in header.text
    assert erratum1.published_at.isoformat() not in header.text
    entries = card.find(class_="card-content").find_all("p")
    assert len(entries) == 2
    # order should be erratum2, erratum1
    assert erratum2.published_at.isoformat() in entries[0].text
    assert erratum2.text in entries[0].text
    assert erratum1.published_at.isoformat() in entries[1].text
    assert erratum1.text in entries[1].text

    ## Add third erratum as oldest
    erratum3 = ErratumFactory(
        puzzle=puzzle, published_at=timezone.now() - timezone.timedelta(days=3)
    )
    assert set(puzzle.errata.all()) == {erratum2, erratum1, erratum3}
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    card = soup.find(id="errata")
    assert card
    header = card.find(class_="card-header")
    assert header
    assert "Errata (3)" in header.text
    # erratum2 is still the newest
    assert erratum2.published_at.isoformat() in header.text
    assert erratum1.published_at.isoformat() not in header.text
    assert erratum3.published_at.isoformat() not in header.text
    entries = card.find(class_="card-content").find_all("p")
    assert len(entries) == 3
    # order should be erratum2, erratum1, erratum3
    assert erratum2.published_at.isoformat() in entries[0].text
    assert erratum2.text in entries[0].text
    assert erratum1.published_at.isoformat() in entries[1].text
    assert erratum1.text in entries[1].text
    assert erratum3.published_at.isoformat() in entries[2].text
    assert erratum3.text in entries[2].text
