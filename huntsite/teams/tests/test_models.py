import pytest

from huntsite.teams.factories import UserFactory
from huntsite.teams.models import User

pytestmark = pytest.mark.django_db


def test_nonprivileged_user_manager():
    assert User.objects.count() == 0
    assert User.nonprivileged.count() == 0

    normal_user = UserFactory(username="normie")
    UserFactory(username="admin", is_staff=True, is_superuser=True)
    UserFactory(username="tester", is_tester=True)

    assert User.objects.count() == 3
    assert User.nonprivileged.count() == 1
    assert User.nonprivileged.first() == normal_user
