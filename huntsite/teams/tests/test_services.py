from textwrap import dedent

from django.core import mail
import pytest

from huntsite.teams.factories import NO_EMAIL_ADDRESSES, EmailAddressFactory, UserFactory
from huntsite.teams.services import (
    _unmark,
    email_address_select_all_active,
    send_email,
    user_deactivate,
)

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


def test_active_email_select():
    user1_email = EmailAddressFactory(user=UserFactory())
    user2 = UserFactory()
    user2_email1 = EmailAddressFactory(user=user2)
    user2_email2 = EmailAddressFactory(user=user2)
    admin_email = EmailAddressFactory(user=UserFactory(is_staff=True))
    deactivated_email = EmailAddressFactory(user=UserFactory(is_active=False))
    tester_email = EmailAddressFactory(user=UserFactory(is_tester=True))

    emails = email_address_select_all_active()
    assert user1_email in emails
    assert user2_email1 in emails
    assert user2_email2 in emails
    assert admin_email not in emails
    assert deactivated_email not in emails
    assert tester_email not in emails


def test_markdown_unmark():
    message = "foo [bar](https://www.adventhunt.com) baz"
    expected = "foo bar (https://www.adventhunt.com) baz"
    assert _unmark(message) == expected

    message = dedent("""\
    Here's a first **paragraph**. There's a [link](https://www.adventhunt.com) in it.

    And here's a _second_ paragraph.
    """)
    expected = dedent("""\
    Here's a first paragraph. There's a link (https://www.adventhunt.com) in it.

    And here's a second paragraph.
    """).strip()
    output = _unmark(message)
    assert output == expected, output


def test_send_email():
    subject = "Test Subject"
    message = "Test Message"

    email_addresses = [EmailAddressFactory() for _ in range(15)]

    assert mail.outbox == []

    recipients = [email.email for email in email_addresses]
    send_email(subject, message, recipients)

    assert len(mail.outbox) == 2
    assert mail.outbox[0].subject == subject
    assert mail.outbox[0].body == message
    assert mail.outbox[0].to == []
    assert mail.outbox[0].bcc == recipients[:10]

    assert mail.outbox[1].subject == subject
    assert mail.outbox[1].body == message
    assert mail.outbox[1].to == []
    assert mail.outbox[1].bcc == recipients[10:]
