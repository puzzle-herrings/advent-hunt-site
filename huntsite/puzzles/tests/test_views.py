from bs4 import BeautifulSoup
from django.utils import timezone
import pytest
from pytest_django.asserts import assertRedirects, assertTemplateNotUsed, assertTemplateUsed

from huntsite.puzzles.factories import CannedHintFactory, ErratumFactory, PuzzleFactory
from huntsite.puzzles.services import guess_list_for_puzzle_and_user
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


def test_puzzle_detail_auth(client):
    """Puzzle detail page requires logged in user."""
    puzzle = PuzzleFactory()

    response = client.get(puzzle.get_absolute_url())
    assertRedirects(response, f"/accounts/login/?next={puzzle.get_absolute_url()}")

    user = UserFactory()
    client.force_login(user)
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    assert puzzle.title in response.content.decode()


def test_puzzle_detail_availability(client):
    """Puzzle detail page should be found if puzzle is available."""
    puzzle = PuzzleFactory(available_at=timezone.now() + timezone.timedelta(days=1))

    user = UserFactory()
    client.force_login(user)

    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 404

    puzzle.available_at = timezone.now() - timezone.timedelta(days=1)
    puzzle.save()
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    assert puzzle.title in response.content.decode()


def test_puzzle_detail_no_answer_in_source(client):
    """Puzzle detail should not include answer in HTML source if not solved."""
    user = UserFactory()
    client.force_login(user)

    puzzle1 = PuzzleFactory(
        answer="SECRET", available_at=timezone.now() - timezone.timedelta(days=1)
    )
    response = client.get(puzzle1.get_absolute_url())
    assert response.status_code == 200
    assert puzzle1.answer not in response.content.decode()

    puzzle2 = PuzzleFactory(
        answer="SECRET PHRASE", available_at=timezone.now() - timezone.timedelta(days=1)
    )
    response = client.get(puzzle2.get_absolute_url())
    assert response.status_code == 200
    assert puzzle2.answer not in response.content.decode()


def test_puzzle_detail_no_answer_keep_going_in_source(client):
    """Puzzle detail should not include answer or keep goign answers in HTML source if not
    solved."""
    puzzle = PuzzleFactory(
        answer="SECRET",
        available_at=timezone.now() - timezone.timedelta(days=1),
        keep_going_answers=["INTERMEDIATE A" "INTERMEDIATE B"],
    )

    user = UserFactory()
    client.force_login(user)

    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    assert puzzle.answer not in response.content.decode()
    assert "SECRET" not in response.content.decode()
    assert "INTERMEDIATE A" not in response.content.decode()
    assert "INTERMEDIATEA" not in response.content.decode()
    assert "INTERMEDIATE B" not in response.content.decode()
    assert "INTERMEDIATEB" not in response.content.decode()


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


def test_puzzle_detail_canned_hints(client):
    """Canned hints display correctly on puzzle detail page."""
    puzzle = PuzzleFactory()

    user = UserFactory()
    client.force_login(user)

    # No canned hints
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find(id="canned-hints")

    # Add one canned hint, no hint release
    CannedHintFactory(puzzle=puzzle, keywords="KEYWORD-A", text="HINT-A", order_by=1)
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find(id="canned-hints")

    # Before hint release
    puzzle.canned_hints_available_at = timezone.now() + timezone.timedelta(days=1)
    puzzle.save()
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find(id="canned-hints")

    # After hint release
    puzzle.canned_hints_available_at = timezone.now() - timezone.timedelta(days=1)
    puzzle.save()
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    card = soup.find(id="canned-hints")
    assert card
    header = card.find(class_="card-header")
    assert header
    assert "Hints" in header.text
    entries = card.find(class_="card-content").find("tbody").find_all("tr")
    assert len(entries) == 1
    assert "KEYWORD" in entries[0].text
    assert "HINT" in entries[0].text

    ## Add second and third canned hint
    CannedHintFactory(puzzle=puzzle, keywords="KEYWORD-B", text="HINT-B", order_by=0)
    CannedHintFactory(puzzle=puzzle, keywords="KEYWORD-C", text="HINT-C", order_by=2)
    response = client.get(puzzle.get_absolute_url())
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    card = soup.find(id="canned-hints")
    assert card
    header = card.find(class_="card-header")
    assert header
    assert "Hints" in header.text
    entries = card.find(class_="card-content").find("tbody").find_all("tr")
    assert len(entries) == 3
    assert "KEYWORD-B" in entries[0].text
    assert "HINT-B" in entries[0].text
    assert "KEYWORD-A" in entries[1].text
    assert "HINT-A" in entries[1].text
    assert "KEYWORD-C" in entries[2].text
    assert "HINT-C" in entries[2].text


def test_puzzle_guess_submit_auth(client):
    """Puzzle guess submission requires logged in user."""
    puzzle = PuzzleFactory(available_at=timezone.now() - timezone.timedelta(days=1))

    response = client.post(puzzle.get_absolute_url(), data={"guess": "test"})
    assertRedirects(response, f"/accounts/login/?next={puzzle.get_absolute_url()}")

    user = UserFactory()
    client.force_login(user)
    response = client.post(puzzle.get_absolute_url(), data={"guess": "I AM GUESSING"})
    assert response.status_code == 200
    assert "I AM GUESSING" in response.content.decode()


def test_puzzle_guess_submit(client):
    puzzle = PuzzleFactory(
        available_at=timezone.now() - timezone.timedelta(days=1),
        answer="FELIZ NAVIDAD",
    )

    user = UserFactory()
    client.force_login(user)

    # Incorrect guess
    response = client.post(puzzle.get_absolute_url(), data={"guess": "I AM GUESSING"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 1
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 1
    assert "I AM GUESSING" in guess_rows[0].text
    assert "Incorrect" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "Incorrect" in eval_message.text

    # Second incorrect guess
    response = client.post(puzzle.get_absolute_url(), data={"guess": "ANOTHER GUESS"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 2
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 2
    assert "ANOTHER GUESS" in guess_rows[0].text
    assert "Incorrect" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "Incorrect" in eval_message.text

    # Repeated guess
    response = client.post(puzzle.get_absolute_url(), data={"guess": "ANOTHER GUESS"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 2
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 2
    eval_message = soup.find(id="evaluation-message")
    assert "already submitted" in eval_message.text

    # Correct answer
    response = client.post(puzzle.get_absolute_url(), data={"guess": "FELIZ NAVIDAD"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 3
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 3
    assert "FELIZ NAVIDAD" in guess_rows[0].text
    assert "Correct" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "Correct" in eval_message.text


def test_puzzle_guess_submit_keep_going(client):
    puzzle = PuzzleFactory(
        available_at=timezone.now() - timezone.timedelta(days=1),
        answer="FELIZ NAVIDAD",
        keep_going_answers=["SNOWFLAKE", "JINGLE BELLS"],
    )

    user = UserFactory()
    client.force_login(user)

    # Incorrect guess
    response = client.post(puzzle.get_absolute_url(), data={"guess": "I AM GUESSING"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 1
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 1
    assert "I AM GUESSING" in guess_rows[0].text
    assert "Incorrect" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "Incorrect" in eval_message.text

    # Keep going guess
    response = client.post(puzzle.get_absolute_url(), data={"guess": "JINGLE BELLS"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 2
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 2
    assert "JINGLE BELLS" in guess_rows[0].text
    assert "Keep going" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "intermediate" in eval_message.text

    # Other keep going guess
    response = client.post(puzzle.get_absolute_url(), data={"guess": "SNOWFLAKE"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 3
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 3
    assert "SNOWFLAKE" in guess_rows[0].text
    assert "Keep going" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "intermediate" in eval_message.text

    # Correct answer
    response = client.post(puzzle.get_absolute_url(), data={"guess": "FELIZ NAVIDAD"})
    assert response.status_code == 200
    assert guess_list_for_puzzle_and_user(puzzle=puzzle, user=user).count() == 4
    assertTemplateUsed(response, "partials/puzzle_guess_list.html")
    assertTemplateNotUsed(response, "puzzle_detail.html")
    soup = BeautifulSoup(response.content, "html.parser")
    guess_rows = soup.find_all("tr", class_="guess-list-row")
    assert len(guess_rows) == 4
    assert "FELIZ NAVIDAD" in guess_rows[0].text
    assert "Correct" in guess_rows[0].text
    eval_message = soup.find(id="evaluation-message")
    assert "Correct" in eval_message.text


def test_puzzle_solve_with_story_unlock(client):
    pass
