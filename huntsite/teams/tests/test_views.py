from bs4 import BeautifulSoup
import pytest

from huntsite.puzzles.factories import PuzzleFactory
from huntsite.puzzles.services import guess_submit
from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_team_list_view(client):
    UserFactory(team_name="Team 1")
    UserFactory(team_name="Team 2")
    UserFactory(team_name="Team 3")
    UserFactory(team_name="Team Test", is_tester=True)
    UserFactory(team_name="Team Admin", is_staff=True)
    UserFactory(team_name="Team Deactivated", is_active=False)

    response = client.get("/teams/")
    assert response.status_code == 200
    assert "Team 1" in response.content.decode()
    assert "Team 2" in response.content.decode()
    assert "Team 3" in response.content.decode()
    assert "Team Test" not in response.content.decode()
    assert "Team Admin" not in response.content.decode()
    assert "Team Deactivated" not in response.content.decode()

    soup = BeautifulSoup(response.content, "html.parser")
    team_count_p = soup.find("p", id="team-count")
    assert "3" in team_count_p.text


def test_team_detail_view(client):
    team = UserFactory(team_name="Team 1")
    other_team = UserFactory(team_name="Team 2")

    ## View as anonymous
    response = client.get(f"/teams/{team.pk}/", user=team)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert team.team_name in soup.find("section").text
    assert other_team.team_name not in soup.find("section").text

    response = client.get(f"/teams/{other_team.pk}/", user=team)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert team.team_name not in soup.find("section").text
    assert other_team.team_name in soup.find("section").text

    ## Log in as team
    client.force_login(team)

    response = client.get(f"/teams/{team.pk}/", user=team)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert team.team_name in soup.find("section").text
    assert "Your team's profile" in soup.find("section").text
    assert "Manage your account" in soup.find("section").text
    assert other_team.team_name not in soup.find("section").text

    response = client.get(f"/teams/{other_team.pk}/", user=team)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert team.team_name not in soup.find("section").text
    assert other_team.team_name in soup.find("section").text

    ## Solve a puzzle
    puzzle1 = PuzzleFactory()
    puzzle2 = PuzzleFactory()

    guess_submit(puzzle=puzzle1, user=team, guess_text=puzzle1.answer)

    response = client.get(f"/teams/{team.pk}/", user=team)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert puzzle1.title in soup.find("section").text
    assert puzzle2.title not in soup.find("section").text

    response = client.get(f"/teams/{other_team.pk}/", user=team)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert puzzle1.title not in soup.find("section").text
    assert puzzle2.title not in soup.find("section").text


def test_team_view_nonexistent(client):
    """Test that a nonexistent team returns a 404 (and not a server error)."""
    response = client.get("/teams/999/")
    assert response.status_code == 404
    assert "Not Found" in response.content.decode()


def test_team_view_privileged(client):
    """Test that only privileged users can view all team profiles."""

    user1 = UserFactory(team_name="Team 1")
    user2 = UserFactory(team_name="Team 2")
    tester = UserFactory(team_name="Team Test", is_tester=True)
    admin = UserFactory(team_name="Team Admin", is_staff=True)
    deactivated = UserFactory(team_name="Team Deactivated", is_active=False)

    # anonymous user can only view nonprivileged teams profiles
    for team in (user1, user2):
        response = client.get(f"/teams/{team.pk}/")
        assert response.status_code == 200
        assert team.team_name in response.content.decode()
    for team in (tester, admin, deactivated):
        response = client.get(f"/teams/{team.pk}/")
        assert response.status_code == 404
        assert "Not Found" in response.content.decode()

    # regular user can only view nonprivileged teams profiles
    client.force_login(user1)
    for team in (user1, user2):
        response = client.get(f"/teams/{team.pk}/")
        assert response.status_code == 200
        assert team.team_name in response.content.decode()
    for team in (tester, admin, deactivated):
        response = client.get(f"/teams/{team.pk}/")
        assert response.status_code == 404
        assert "Not Found" in response.content.decode()

    # tester and admin can view all profiles
    for current_user in (tester, admin):
        client.force_login(current_user)
        for team in (user1, user2, tester, admin, deactivated):
            response = client.get(f"/teams/{team.pk}/")
            assert response.status_code == 200
            assert team.team_name in response.content.decode()
