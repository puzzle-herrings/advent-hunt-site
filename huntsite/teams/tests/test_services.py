import pytest

from huntsite.teams.factories import NO_EMAIL_ADDRESSES, UserFactory
from huntsite.teams.services import user_deactivate

pytestmark = pytest.mark.django_db


def test_user_deactivate(client):
    # User with one email address
    user1 = UserFactory()
    assert user1.is_active
    assert not user1.username.startswith("deactivated-")
    assert "(Deactivated)" not in user1.team_name
    assert not user1.email.endswith("@deactivated.adventhunt.com")
    assert user1.emailaddress_set.count() == 1
    user_deactivate(user1)
    assert not user1.is_active
    assert user1.username.startswith("deactivated-")
    assert "(Deactivated)" in user1.team_name
    assert user1.email.endswith("@deactivated.adventhunt.com")
    assert user1.emailaddress_set.count() == 0

    # User with multiple email addresses
    user2 = UserFactory(email_addresses=["dancer@example.com", "prancer@example.com"])
    assert user2.is_active
    assert user2.emailaddress_set.count() == 3
    user_deactivate(user2)
    assert not user2.is_active
    assert user2.emailaddress_set.count() == 0

    # User with no email addresses
    user3 = UserFactory(email_addresses=NO_EMAIL_ADDRESSES)
    assert user3.emailaddress_set.count() == 0
    assert user3.is_active
    user_deactivate(user3)
    assert not user3.is_active
