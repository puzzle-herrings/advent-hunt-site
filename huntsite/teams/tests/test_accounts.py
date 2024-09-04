from django.urls import reverse
import pytest

from huntsite.teams.factories import UserFactory
from huntsite.teams.models import TEAM_NAME_MAX_LENGTH, User

pytestmark = pytest.mark.django_db


def test_signup(client):
    """Normal signup under normal conditions."""
    response = client.post(
        reverse("account_signup"),
        data={
            "email": "foo@example.com",
            "username": "foo",
            "team_name": "Team Foo",
            "password1": "foobadoo123!",
            "password2": "foobadoo123!",
        },
    )
    assert response.status_code == 302

    assert User.objects.count() == 1
    user = User.objects.first()
    assert user.email == "foo@example.com"
    assert user.username == "foo"
    assert user.team_name == "Team Foo"


def test_signup_team_name_errors(client):
    # Too long
    team_name = "a" * 200
    response = client.post(
        reverse("account_signup"),
        data={
            "email": "foo@example.com",
            "username": "foo",
            "team_name": team_name,
            "password1": "foobadoo123!",
            "password2": "foobadoo123!",
        },
    )
    assert response.status_code == 200
    assert response.context["form"].errors["team_name"] == [
        f"Ensure this value has at most {TEAM_NAME_MAX_LENGTH} characters (it has 200)."
    ]

    assert User.objects.count() == 0

    # Is blank
    team_name = ""
    response = client.post(
        reverse("account_signup"),
        data={
            "email": "foo@example.com",
            "username": "foo",
            "team_name": team_name,
            "password1": "foobadoo123!",
            "password2": "foobadoo123!",
        },
    )
    assert response.status_code == 200
    assert response.context["form"].errors["team_name"] == ["This field is required."]

    assert User.objects.count() == 0

    # Is only whitespace
    team_name = "     "
    response = client.post(
        reverse("account_signup"),
        data={
            "email": "foo@example.com",
            "username": "foo",
            "team_name": team_name,
            "password1": "foobadoo123!",
            "password2": "foobadoo123!",
        },
    )
    assert response.status_code == 200
    assert response.context["form"].errors["team_name"] == ["This field is required."]

    assert User.objects.count() == 0


def test_signup_team_name_duplicate(client):
    team_name = "Cool Team Name"
    UserFactory(team_name=team_name)

    response = client.post(
        reverse("account_signup"),
        data={
            "email": "foo@example.com",
            "username": "foo",
            "team_name": team_name,
            "password1": "foobadoo123!",
            "password2": "foobadoo123!",
        },
    )
    assert response.status_code == 200
    assert response.context["form"].errors["team_name"] == [
        "A team with that name already exists."
    ]


def test_profile_update(client):
    user = UserFactory(team_name="Old Team Name")
    client.force_login(user)

    response = client.post(
        reverse("account_manage"),
        data={"team_name": "New Team Name", "members": "Someone, Someone Else"},
    )
    assert response.status_code == 200
    assert response.context["form"].errors == {}
    assert "Profile updated successfully" in response.content.decode()
    user.refresh_from_db()
    assert user.team_name == "New Team Name"
    assert user.profile.members == "Someone, Someone Else"

    # Try to set team name to blank, should error
    response = client.post(
        reverse("account_manage"),
        data={"team_name": "", "members": "Someone, Someone Else"},
    )
    assert response.status_code == 200
    assert response.context["form"].errors == {"team_name": ["This field is required."]}

    # Try to set team name too long, should error
    team_name = "a" * 200
    response = client.post(
        reverse("account_manage"),
        data={"team_name": team_name, "members": "Someone, Someone Else"},
    )
    assert response.status_code == 200
    assert response.context["form"].errors == {
        "team_name": [
            f"Ensure this value has at most {TEAM_NAME_MAX_LENGTH} characters (it has 200)."
        ]
    }


def test_username_update(client):
    user = UserFactory(username="oldusername", team_name="Old Team Name")
    client.force_login(user)

    response = client.post(reverse("account_username"), data={"username": "newusername"})
    assert response.status_code == 200
    assert response.context["form"].errors == {}
    assert "Username updated successfully" in response.content.decode()

    user.refresh_from_db()
    assert user.username == "newusername"
    assert user.team_name == "Old Team Name"
