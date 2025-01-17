from datetime import timedelta

from bs4 import BeautifulSoup, Tag
from django.test import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from huntsite.content.factories import (
    AboutEntryFactory,
    AttributionsEntryFactory,
    StoryEntryFactory,
    UpdateEntryFactory,
)
from huntsite.content.models import WrapupEntry
from huntsite.puzzles.factories import (
    MetapuzzleInfoFactory,
    PuzzleAttributionsEntryFactory,
    PuzzleFactory,
)
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_about_page(client):
    AboutEntryFactory(
        title="But do you recall the most famous reindeer of all?",
        content="Rudolph the red-nosed reindeer had a very shiny nose.",
    )
    AboutEntryFactory(
        title="Won't you guide my sleigh tonight?",
        content="Rudolph the Red-Nosed Reindeer, you'll go down in history.",
    )

    response = client.get("/about/")
    assert response.status_code == 200
    assert b"But do you recall" in response.content
    assert b"had a very shiny nose" in response.content
    assert b"guide my sleigh tonight" in response.content
    assert b"go down in history" in response.content


def test_story_page(client, settings):
    # Set up puzzles and story entries
    puzzle1 = PuzzleFactory()
    story1_title = "Here is Story 1"
    story1_content = "Twas the night before Christmas, when all through the house..."
    story1 = StoryEntryFactory(
        title=story1_title, content=story1_content, puzzle=puzzle1, order_by=1
    )

    puzzle2 = PuzzleFactory()
    story2_title = "There Be Story 2"
    story2_content = "Not a creature was stirring, not even a mouse."
    story2 = StoryEntryFactory(
        title=story2_title, content=story2_content, puzzle=puzzle2, order_by=2
    )

    puzzle3 = PuzzleFactory()
    story3_title = "Mayhaps Story 3"
    story3_content = "The stockings were hung by the chimney with care..."
    story3 = StoryEntryFactory(
        title=story3_title, content=story3_content, puzzle=puzzle3, order_by=3
    )

    # Set up users
    anon_client = Client()

    user1 = UserFactory()
    user1_client = Client()
    user1_client.force_login(user1)

    user2 = UserFactory()
    user2_client = Client()
    user2_client.force_login(user2)

    ## Before hunt live - no story entries, only invitation
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() + timedelta(days=1)
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() + timedelta(days=2)

    def _assert_invitation_available(story_cards: list[Tag], is_hidden: bool):
        invitation_story_card = story_cards[0]
        assert (
            "You receive an exciting piece of mail from the North Pole"
            in invitation_story_card.text
        )
        assert (
            "is-hidden" in invitation_story_card.find("div", class_="card-content")["class"]
        ) == is_hidden

    # All users should only see the invitation
    for client in [anon_client, user1_client, user2_client]:
        response = anon_client.get("/story/")
        assert response.status_code == 200
        assert len(response.context["entries"]) == 0
        soup = BeautifulSoup(response.content, "html.parser")
        story_cards = soup.find_all("div", class_="story-card")
        assert len(story_cards) == 1

        _assert_invitation_available(story_cards, is_hidden=False)

    ## After hunt live - Arriving in North Pole
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() - timedelta(days=1)

    def _assert_arrived_available(story_cards: list[Tag], is_hidden: bool):
        arrived_story = story_cards[1]
        assert "You arrive at the North Pole" in arrived_story.text
        assert (
            "is-hidden" in arrived_story.find("div", class_="card-content")["class"]
        ) == is_hidden

    # All users should see both invitation and arriving story
    for client in [anon_client, user1_client, user2_client]:
        response = client.get("/story/")
        assert response.status_code == 200
        assert len(response.context["entries"]) == 0
        soup = BeautifulSoup(response.content, "html.parser")
        story_cards = soup.find_all("div", class_="story-card")
        assert len(story_cards) == 2

        _assert_invitation_available(story_cards, is_hidden=True)
        _assert_arrived_available(story_cards, is_hidden=False)

    ## User 1 solves puzzle 1
    guess_submit(puzzle=puzzle1, user=user1, guess_text=puzzle1.answer)

    def _assert_story1_available(
        story_cards: list[Tag],
        is_hidden: bool,
        has_spoiler_warning: bool = False,
    ):
        story1_card = next(card for card in story_cards if story1_title in card.find("h3").text)
        assert story1_content in story1_card.text
        assert (
            "is-hidden" in story1_card.find("div", class_="card-content")["class"]
        ) == is_hidden
        if has_spoiler_warning:
            assert f"Spoiler warning for {puzzle1.title}" in story1_card.text
        else:
            assert "Spoiler warning" not in story1_card.text

    # Anon should still only see invitation and arriving story
    response = anon_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 0
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 2
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=False)

    # User 1 should see invitation, arriving story, and story 1
    response = user1_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 1
    assert response.context["entries"][0] == story1
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 3
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=True)

    # User 2 should still only see invitation and arriving story
    response = user2_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 0
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 2
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=False)

    ## User 1 solves puzzle 2
    guess_submit(puzzle=puzzle2, user=user1, guess_text=puzzle2.answer)

    def _assert_story2_available(
        story_cards: list[Tag],
        is_hidden: bool,
        has_spoiler_warning: bool = False,
    ):
        story2_card = next(card for card in story_cards if story2_title in card.find("h3").text)
        assert story2_content in story2_card.text
        assert (
            "is-hidden" in story2_card.find("div", class_="card-content")["class"]
        ) == is_hidden
        if has_spoiler_warning:
            assert f"Spoiler warning for {puzzle2.title}" in story2_card.text
        else:
            assert "Spoiler warning" not in story2_card.text

    # Anon should still only see invitation and arriving story
    response = anon_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 0
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 2
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=False)

    # User 1 should see invitation, arriving story, story 1, and story 2
    response = user1_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 2
    assert response.context["entries"][0] == story1
    assert response.context["entries"][1] == story2
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 4
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=True)
    _assert_story1_available(story_cards, is_hidden=True)
    _assert_story2_available(story_cards, is_hidden=False)

    # User 2 should still only see invitation and arriving story
    response = user2_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 0
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 2
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=False)

    ## User 2 solves puzzle 3
    guess_submit(puzzle=puzzle3, user=user2, guess_text=puzzle3.answer)

    def _assert_story3_available(
        story_cards: list[Tag],
        is_hidden: bool,
        has_spoiler_warning: bool = False,
    ):
        story3_card = next(card for card in story_cards if story3_title in card.find("h3").text)
        assert story3_content in story3_card.text
        assert (
            "is-hidden" in story3_card.find("div", class_="card-content")["class"]
        ) == is_hidden
        if has_spoiler_warning:
            assert f"Spoiler warning for {puzzle3.title}" in story3_card.text
        else:
            assert "Spoiler warning" not in story3_card.text

    # Anon should still only see invitation and arriving story
    response = anon_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 0
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 2
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=False)

    # User 1 should see invitation, arriving story, story 1, story 2
    response = user1_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 2
    assert response.context["entries"][0] == story1
    assert response.context["entries"][1] == story2
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 4
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=True)
    _assert_story1_available(story_cards, is_hidden=True)
    _assert_story2_available(story_cards, is_hidden=False)

    # User 2 should see invitation, arriving story, story 3
    response = user2_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 1
    assert response.context["entries"][0] == story3
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    assert len(story_cards) == 3
    _assert_invitation_available(story_cards, is_hidden=True)
    _assert_arrived_available(story_cards, is_hidden=True)
    _assert_story3_available(story_cards, is_hidden=False)

    ## Hunt state is ended
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() - timedelta(days=1)
    # All users should see all story entries, all are hidden
    for client in (anon_client, user1_client, user2_client):
        response = client.get("/story/")
        assert response.status_code == 200
        assert len(response.context["entries"]) == 3
        assert response.context["entries"][0] == story1
        assert response.context["entries"][1] == story2
        assert response.context["entries"][2] == story3
        soup = BeautifulSoup(response.content, "html.parser")
        story_cards = soup.find_all("div", class_="story-card")
        assert len(story_cards) == 5
        _assert_invitation_available(story_cards, is_hidden=True)
        _assert_arrived_available(story_cards, is_hidden=True)
        _assert_story1_available(story_cards, is_hidden=True, has_spoiler_warning=True)
        _assert_story2_available(story_cards, is_hidden=True, has_spoiler_warning=True)
        _assert_story3_available(story_cards, is_hidden=True, has_spoiler_warning=True)


def test_victory_unlock(settings):
    # Set up users
    anon_client = Client()
    user1 = UserFactory()
    user1_client = Client()
    user1_client.force_login(user1)
    user2 = UserFactory()
    user2_client = Client()
    user2_client.force_login(user2)
    tester = UserFactory(is_tester=True)
    tester_client = Client()
    tester_client.force_login(tester)

    # Set up puzzles and story entries
    puzzle = PuzzleFactory()
    MetapuzzleInfoFactory(puzzle=puzzle, is_final=True)
    story_title = "Here is Story 1"
    story_content = "Twas the night before Christmas, when all through the house..."
    story = StoryEntryFactory(
        title=story_title, content=story_content, puzzle=puzzle, order_by=1, is_final=True
    )

    ## Hunt state is live
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() - timedelta(days=2)
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() + timedelta(days=2)

    ## Before solve, nobody sees victory entry or victory page
    for client in [anon_client, user1_client, user2_client]:
        response = client.get("/story/")
        assert response.status_code == 200
        assert len(response.context["entries"]) == 0

        response = client.get("/story/victory/")
        assert response.status_code == 404

    # Except that tester can access the victory page
    response = tester_client.get("/story/victory/")
    assert response.status_code == 200
    assert story_title in response.content.decode()
    assert story_content in response.content.decode()

    ## User 1 finishes the final puzzle
    guess_submit(puzzle=puzzle, user=user1, guess_text=puzzle.answer)

    # After solve, only user 1 sees victory entry and victory page
    response = user1_client.get("/story/")
    assert response.status_code == 200
    assert len(response.context["entries"]) == 1
    assert response.context["entries"][0] == story
    soup = BeautifulSoup(response.content, "html.parser")
    story_cards = soup.find_all("div", class_="story-card")
    last_story_card = story_cards[-1]
    assert story_title in last_story_card.text
    assert (
        reverse("victory") in last_story_card.find("div", class_="card-content").find("a")["href"]
    )

    response = user1_client.get("/story/victory/")
    assert response.status_code == 200
    assert story_title in response.content.decode()
    assert story_content in response.content.decode()

    # User 2 and anon still don't see victory entry or victory page
    for client in [anon_client, user2_client]:
        response = client.get("/story/")
        assert response.status_code == 200
        assert len(response.context["entries"]) == 0

        response = client.get("/story/victory/")
        assert response.status_code == 404

    # Tester still sees victory page
    response = tester_client.get("/story/victory/")
    assert response.status_code == 200

    ## Hunt state is ended
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() - timedelta(days=1)
    # Everyone sees victory entry and victory page
    for client in (anon_client, user1_client, user2_client, tester_client):
        response = client.get("/story/")
        assert response.status_code == 200
        assert len(response.context["entries"]) == 1
        assert response.context["entries"][0] == story
        soup = BeautifulSoup(response.content, "html.parser")
        story_cards = soup.find_all("div", class_="story-card")
        last_story_card = story_cards[-1]
        assert story_title in last_story_card.text
        assert (
            reverse("victory")
            in last_story_card.find("div", class_="card-content").find("a")["href"]
        )

        response = client.get("/story/victory/")
        assert response.status_code == 200
        assert story_title in response.content.decode()
        assert story_content in response.content.decode()


def test_attributions_page(client):
    attrs_entry = AttributionsEntryFactory()
    puzz_attrs_entry1 = PuzzleAttributionsEntryFactory(
        puzzle__available_at=timezone.now() - timedelta(days=2)
    )
    puzz_attrs_entry2 = PuzzleAttributionsEntryFactory(
        puzzle__available_at=timezone.now() - timedelta(days=1)
    )
    puzz_attrs_entry3 = PuzzleAttributionsEntryFactory(
        puzzle__available_at=timezone.now() + timedelta(days=1)
    )
    puzz_attrs_entry4 = PuzzleAttributionsEntryFactory(
        puzzle__available_at=timezone.now() + timedelta(days=2)
    )
    extra_puzz = PuzzleFactory()

    response = client.get("/attributions/")
    assert response.status_code == 200
    assert attrs_entry.title in response.content.decode()
    assert puzz_attrs_entry1.puzzle.title in response.content.decode()
    assert puzz_attrs_entry2.puzzle.title in response.content.decode()
    assert puzz_attrs_entry3.puzzle.title not in response.content.decode()
    assert puzz_attrs_entry4.puzzle.title not in response.content.decode()
    assert extra_puzz.title not in response.content.decode()


def test_updates_page(client):
    UpdateEntryFactory(
        content="The North Pole is a-buzz with activity as elves prepare for the big day.",
        published_at=timezone.now() - timedelta(days=1),
    )
    UpdateEntryFactory(
        content="The reindeer are practicing their take-offs and landings.",
        published_at=timezone.now() - timedelta(days=3),
    )
    UpdateEntryFactory(
        content="Santa is checking his list twice.",
        published_at=timezone.now() - timedelta(days=2),
    )

    response = client.get("/updates/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    entries = soup.find_all("div", class_="update-entry")
    assert len(entries) == 3
    assert "North Pole" in entries[0].text
    assert "Santa" in entries[1].text
    assert "reindeer" in entries[2].text


def test_wrapup_navbar(client, settings):
    ## Hunt state is live
    settings.HUNT_IS_LIVE_DATETIME = timezone.now() - timedelta(days=3)
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() + timedelta(days=3)

    wrapup_entry = WrapupEntry.get_solo()
    wrapup_entry.content = "Merry Christmas to all, and to all a good night!"
    wrapup_entry.available_at = timezone.now() + timedelta(days=6)
    wrapup_entry.save()

    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find("a", class_="navbar-item", string="Wrap-up")

    ## Hint state is ended but before wrapup available
    settings.HUNT_IS_ENDED_DATETIME = timezone.now() - timedelta(days=2)
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert not soup.find("a", class_="navbar-item", string="Wrap-up")

    ## Wrapup is available
    wrapup_entry.available_at = timezone.now() - timedelta(days=1)
    wrapup_entry.save()
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert soup.find("a", class_="navbar-item", string="Wrap-up")


def test_wrapup_page(client):
    wrapup_entry = WrapupEntry.get_solo()
    wrapup_entry.content = "Merry Christmas to all, and to all a good night!"
    wrapup_entry.save()

    # 404 on wrapup page if not available
    response = client.get("/wrapup/")
    assert response.status_code == 404

    # Test user can see wrapup page though
    test_user = UserFactory(is_tester=True)
    test_client = Client()
    test_client.force_login(test_user)
    response = test_client.get("/wrapup/")
    assert response.status_code == 200
    assert wrapup_entry.content in response.content.decode()

    # Update wrapup entry to be available
    wrapup_entry.available_at = timezone.now() - timedelta(days=1)
    wrapup_entry.save()
    response = client.get("/wrapup/")
    assert response.status_code == 200
    assert wrapup_entry.content in response.content.decode()
