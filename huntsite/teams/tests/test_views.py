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
