import pytest

from huntsite.teams.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_team_list_view(client):
    UserFactory(team_name="Team 1")
    UserFactory(team_name="Team 2")
    UserFactory(team_name="Team 3")

    response = client.get("/teams/")
    assert response.status_code == 200
    assert "Team 1" in response.content.decode()
    assert "Team 2" in response.content.decode()
    assert "Team 3" in response.content.decode()


def test_team_detail_view(client):
    team = UserFactory(team_name="Team 1")

    response = client.get(f"/teams/{team.pk}/")
    assert response.status_code == 200
    assert team.team_name in response.content.decode()
