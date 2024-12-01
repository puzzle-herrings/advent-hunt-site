from io import StringIO
from itertools import islice

from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from loguru import logger
import markdown
from markdown import Markdown

from huntsite.teams.models import User


@transaction.atomic
def user_deactivate(user: User):
    logger.info("Deactivating user {user}", user=user)
    user.is_active = False
    old_username = user.username
    user.username = f"deactivated-{old_username}"
    user.team_name = f"{user.team_name} (Deactivated)"
    user.email = (
        user.email.replace("@", "__at__").replace(".", "__dot__") + "@deactivated.adventhunt.com"
    )
    user.set_unusable_password()
    user.save()
    # Remove allauth email addresses
    email_addresses = EmailAddress.objects.filter(user=user)
    email_addresses.delete()
    logger.success(
        "Deactivated user {old_username}, new username is {user}",
        old_username=old_username,
        user=user,
    )


def user_clear_password(user: User):
    """Clears a user password. This makes them unable to log in until they perform a password
    reset."""
    logger.info("Clearing password for user {user}", user=user)
    user.set_password("")
    user.save()
    logger.success("Cleared password for user {user}", user=user)


def email_address_select_all_active():
    """Select all active email addresses for users that are not staff or testers."""
    return (
        EmailAddress.objects
        # Exclude inactive accounts
        .exclude(user__is_active=False)
        # Exclude staff and testers
        .exclude(user__is_staff=True)
        .exclude(user__is_tester=True)
        .order_by("user")
        .all()
    )


# https://stackoverflow.com/a/54923798
def _unmark_element(element, stream=None):
    """Recursive function to convert markdown to plain text."""
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        _unmark_element(sub, stream)
    if element.tag == "p":
        # Linebreaks after paragraphs
        stream.write("\n")
    if element.tag == "a":
        # Add the URL after the link text
        stream.write(f" ({element.get('href')})")
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
markdown.Markdown.output_formats["plain"] = _unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def _unmark(text):
    return __md.convert(text)


EMAIL_BATCH_SIZE = 10


def batched(iterable, n):
    "Batch data into lists of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    it = iter(iterable)
    while True:
        batch = list(islice(it, n))
        if not batch:
            return
        yield batch


def send_email(subject, message, recipient_list):
    """Send email to a list of recipients as BCC, with a markdown message converted to both HTML
    and plaintext."""
    logger.info(f"Sending email with subject '{subject}' to {len(recipient_list)} recipients.")

    message_html = render_to_string("email.html", {"content": markdown.markdown(message)})
    message_plain = _unmark(message)

    for batch in batched(recipient_list, EMAIL_BATCH_SIZE):
        email = EmailMultiAlternatives(
            subject=subject,
            body=message_plain,
            to=(settings.EMAIL_REPLY_TO,),
            reply_to=(settings.EMAIL_REPLY_TO,),
            bcc=batch,
        )
        email.attach_alternative(message_html, "text/html")
        email.send()
